# Notes API

[![Tests](https://github.com/mensahs18/usernotes-api/actions/workflows/main.yml/badge.svg)](https://github.com/mensahs18/usernotes-api/actions/workflows/main.yml)

A secure asynchronous REST API backend built with FastAPI and SQLAlchemy, implementing JWT authentication, Argon2 password hashing, and AES-256-GCM note encryption.

## Features

### Registration and Authentication
- [X] User registration with argon2 hashing for password security
- [X] Field validation for registration using Pydantic schemas
- [X] Login endpoint with JWT token generation
- [X] Token verification and user resolution from token
- [X] Password stripped from API responses
- [X] Protected routes using OAuth2 bearer scheme
- [X] Username normalisation and validation

### Notes
- [X] Create note (POST /notes)
- [X] Get all my notes (GET /notes)
- [X] Get single note (GET /notes/{id})
- [X] Update note (PATCH /notes/{id})
- [X] Delete note (DELETE /notes/{id})
- [X] Encrypt notes in database
- [X] Note pagination

### Security & Response
- [X] Ownership validation on note routes
- [X] JWT expiration handling
- [ ] Token refreshing
- [ ] JWT denylisting on logout
- [ ] Rate limiting (Redis) against DoS

### Testing
- [X] Pytest test suite
- [X] Authentication tests
- [X] API Integration tests
- [X] Async testing

### Async & Database
- [X] Migrate to async routes and async SQLAlchemy
- [X] PostgreSQL with `asyncpg` driver

### Architecture & Production
- [X] Refactor into modules
- [X] Project tools (ruff, mypy, precommit)
- [ ] Dockerfile
- [ ] Docker Compose
- [ ] Logging


## Tech Stack

- Python
- `FastAPI`
- `SQLAlchemy`
- PostgreSQL (asyncpg)
- `Argon2`
- `PyJWT`

## How to run

### Prerequisites
- PostgreSQL running and accessible (via Docker)
- Poetry

- A Postgres container can be run in Docker by the following command:

```bash
docker run --name notes-postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=notesdb \
  -p 5432:5432 \
  -d postgres:16
```

Create a `.env` file in the root directory:

```env
SECRET_KEY=secret_key_here
ENCRYPT_KEY=your_32_byte_hex_key_here
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/notesdb
```

- `SECRET_KEY` and `ENCRYPT_KEY` can be generated with:

```bash
poetry run python -c "import os; print(os.urandom(32).hex())"
```

Install dependencies:

`poetry install`

Run database migrations:

`poetry run alembic upgrade head`

Run server:

`poetry run uvicorn main:app --workers 4`

While the server is running, open the browser, and enter Swagger UI at:

http://127.0.0.1:8000/docs


## Design Decisions & Tradeoffs

- I initially used SQLite as the database, due to its ease of use and simple configuration, while being aware of PostgreSQL as the industry standard.

- Testing in the `notes-routes` branch (PR #2) confirms SQLite locks under concurrent `POST` requests. By design, SQLite serialises writes while allowing concurrent reads. This is fine for testing, but under load, it locks up preventing further writes. While this can be mitigated with SQLite's Write Ahead Logging (WAL) mode, which allows concurrent reads while writes occur, PostgreSQL is still preferred in production due to its native support for concurrent writes.

- When transitioning to asynchronous execution, `aiosqlite` was used to give SQLite an asynchronous interface. While `aiosqlite` does use a background thread pool to allow asynchronous code, it is still bound by SQLite's write-lock limitation under heavy load. PostgreSQL supports asynchronous drivers and allows concurrency without blocking.

- Initially, usernames were case-sensitive at the database level. I fixed this by lowercasing inputs on registration and login to prevent duplicate accounts and authentication friction between equivalent usernames such as `admin1` and `Admin1`.

- I chose `AES-256-GCM` over Fernet (AES-128-CBC) due to its stronger key length and built-in integrity verification. GCM mode provides confidentiality via encryption as well as authenticity and integrity via an authentication tag, which prevents ciphertext tampering.

- Although I initially intended to use `bcrypt` with `passlib` for password hashing, bcrypt has been proven to be less effective than Argon2 hashing against modern GPU brute force attacks. Argon2 is the industry standard and is recommended by OWASP, due to being memory-hard, which means it requires a significant amount of memory to process each hash.

- When adding password length constraints, I allowed 128 characters. This introduces a potential Denial of Service (DoS) vector, as hashing large inputs with Argon2 is computationally expensive. I accepted it as a trade-off to give users more flexibility with their password lengths and allow 128-character string password managers. In a future PR, application-level CPU exhaustion DoS attacks on authentication will be mitigated via Redis rate-limiting, rather than shortening user inputs. Distributed DoS (DDoS) mitigation would require infrastructure level solutions, which are outside of the scope of this project.

- Regarding password composition rules, OWASP actually recommends against composition rules in favour of length, as users tend to make predictable substitutions e.g. swapping an 'a' for '@'. In this case, composition rules have been used as a deliberate design choice for this project, with awareness of the usability tradeoff.

## Load Testing & Performance

**TL;DR:** While synchronous local SQLite matches asynchronous PostgreSQL at low concurrency (100 users, WAL mode, 4 workers), its strict write-locking architecture triggers database locks and `TimeoutError` pool exhaustion at higher loads. Migrating to PostgreSQL with `asyncpg` removed the write-lock bottleneck. Additionally, CPU-bound AES-256-GCM encryption introduces <1ms of native overhead; offloading it to an async threadpool introduced a counterproductive ~5ms latency increase due to context-switching overhead.

<details>
<summary>View Load Testing & Performance Tests</summary>

### Encryption and threadpools

- As encryption is CPU-bound, three strategies were load-tested at 100 concurrent users (to prevent write-locking of SQLite):
  - No encryption: 39.8 ms median
  - Synchronous AES‑256‑GCM: 39.9 ms median
  - Threadpool AES‑256‑GCM: 45.0 ms median

- At this scale, AES-256-GCM encryption introduces minimal overhead, whereas offloading it to a threadpool introduced ~5 ms median overhead (and a worse p95 latency), showing the context-switching when running it in a threadpool exceeded the actual encryption process. While both AES-256-GCM and Argon2 are implemented in C, AES encryption is hardware accelerated, whereas Argon2 hashing is deliberately slow. Following this, I stripped `run_in_threadpool` from all encrypt/decrypt function calls.

### Synchronous SQLite vs Asynchronous PostgreSQL


#### SQLite ( no WAL )

- I ran some concurrent traffic simulations using Locust, exposing distinct performance bottlenecks. I started testing under a load of 200 concurrent users, but this caused database locking, an inherent limitation of SQLite: only one writer can operate at a time. Furthermore, when a write lock is held, standard SQLite prevents concurrent reads. This resulted in connections holding for longer, eventually exhausting the connection pool and raising SQLAlchemy `TimeoutError` exceptions. 

- After reducing the load to 100 users (4 added per second), the apparent bottleneck shifted from the storage layer to application resource limits. Standard SQLite's write-locking behaviour, without additional configuration, resulted in a significant amount of pool contention. The metrics also reflected this. While read operations were less severely impacted than writes, both degraded under sustained load as read requests queued behind held write locks. `POST /notes` latencies spiked to a 2000ms 99th percentile because requests waited for available connections, which could remain occupied while other operations waited on the write lock.

#### SQLite ( WAL mode / 1 worker )

- **1 worker**: Enabling Write-Ahead Logging (WAL) with a single worker showed significantly improved read performance by allowing concurrent reads during writes. However, under sustained load at 100 concurrent users, `POST` p99 reached 2800ms and the server eventually threw `TimeoutError` exceptions, indicating connection pool exhaustion. WAL allows concurrent reads while writing, but the write lock still serialises all writes regardless of WAL mode.

#### SQLite ( WAL mode / 4 workers)

- **4 workers**: Using 4 workers `uvicorn main:app --workers 4` with WAL produced the best SQLite metrics, a POST p50 of 13ms and GET p50 of 12ms, rivalling PostgreSQL at low concurrency (100 users). However, under sustained load, p99.9 latency still reached ~900ms under sustained load, exposing the write lock's persistence even after configuration adjustments. Multiple workers may attempt to `POST` simultaneously to the same database, and in the unfortunate case they push simultaneously, SQLite's write lock exposes itself once again.

#### Asynchronous PostgreSQL

Finally, migrating to PostgreSQL with `asyncpg` eliminated SQLite's write-lock by using **Multi-Versioning Concurrency Control** (MVCC). MVCC allows true concurrent reads and writes regardless of the user count. The following metrics were captured at 100 concurrent users (4 per second) to provide a controlled comparison against the SQLite baseline. However, it's important to note that due to its architecture, PostgreSQL can scale to handle much higher levels of concurrency.

**1 worker, pool_size=60:**

| Endpoint | p50 | p95 | p99 |
|---|---|---|---|
| GET /notes | 15ms | 32ms | 44ms |
| POST /notes | 20ms | 41ms | 60ms |

**4 workers, pool_size=15 per worker**

| Endpoint | p50 | p95 | p99 |
|---|---|---|---|
| GET /notes | 13ms | 25ms | 35ms |
| POST /notes | 18ms | 33ms | 50ms |

At only 100 concurrent users, the difference between 1 and 4 workers is small, sitting at around 1-2ms. A single async event loop handles 100 concurrent users efficiently. The benefit of multiple workers becomes more apparent at higher concurrency scales. For instance, at 500 concurrent users, the API was able to efficiently handle requests at around 225 requests per second, and suffered <1 ms of latency degradation. Both tests recorded no failures. 

- When configuring pooling, I kept the connection count across pools under PostgreSQL's `max_connections=100`, leaving room for other potential services. For 1 worker, I allowed an overflow of 20, whereas with 4, I allowed 5. This consistently used 80% of the maximum connections across both tests. Python's garbage collector periodically blocks the event loop, so I froze startup modules using `gc.freeze()` to eliminate potential GC pauses from impacting requests.

#### Key Takeaways

While the difference in operation between SQLite and PostgreSQL appears negligible at low concurrency, there is a confounding factor to note. PostgreSQL runs in a Docker container, introducing the overhead of network virtualisation between the database and the API. This is ~2-5ms per query that SQLite's direct, local file access avoids. In production, both would involve network latency: PostgreSQL to a managed database service, SQLite would need to remain local to the application. The comparison would likely favour PostgreSQL more significantly in a remote deployment scenario.

</details>