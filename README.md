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
- Poetry installed

- A Postgres container can be run in Docker by the following command:

```bash
docker run --name notes-postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=notesdb \
  -p 5432:5432 \
  -d postgres:16
```

Create a `.env` file in the project root:

```env
SECRET_KEY=secret_key_here
ENCRYPT_KEY=your_32_byte_hex_key_here
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/notesdb
TEST_DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5433/testdb
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


### Testing

To run tests, you must create a separate test database. This can be done in a docker container with the following command:

```bash
docker run --name test-postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=testdb \
  -p 5433:5432 \
  -d postgres:16
```

Once the container is running, the following command can be used to run tests: 

`poetry run pytest tests/`


## Design Decisions & Tradeoffs

- I initially used SQLite as the database, due to its ease of use and simple configuration, while being aware of PostgreSQL as the industry standard.

- Testing in the `notes-routes` branch (PR #2) confirms SQLite locks under concurrent `POST` requests. By design, SQLite serialises writes while allowing concurrent reads. This is fine for testing, but under load, it locks up preventing further writes. While this can be mitigated with SQLite's Write Ahead Logging (WAL) mode, which allows concurrent reads while writes occur, PostgreSQL is still preferred in production due to its native support for concurrent writes.

- When transitioning to asynchronous execution, `aiosqlite` was used to give SQLite an asynchronous interface. While `aiosqlite` does use a background thread pool to allow asynchronous code, it is still bound by SQLite's write-lock limitation under heavy load. PostgreSQL supports asynchronous drivers and allows concurrency without blocking.

- Initially, usernames were case-sensitive at the database level. I fixed this by lowercasing inputs on registration and login to prevent duplicate accounts and authentication friction between equivalent usernames such as `admin1` and `Admin1`.

- I chose `AES-256-GCM` over Fernet (AES-128-CBC) due to its stronger key length and built-in integrity verification. GCM mode provides confidentiality via encryption as well as authenticity and integrity via an authentication tag, which prevents ciphertext tampering.

- Although I initially intended to use `bcrypt` with `passlib` for password hashing, bcrypt has been proven to be less effective than Argon2 hashing against modern GPU brute force attacks. Argon2id is the industry standard and is recommended by OWASP, due to being memory-hard, which means it requires a significant amount of memory to process each hash.

- When adding password length constraints, I allowed up to 128 characters to give users flexibility and accommodate password managers. While Argon2's hashing cost scales with its configured time and memory parameters rather than input length, it is an expensive operation by design. Running these intensive operations on a bounded thread pool introduces a potential application-level CPU exhaustion Denial of Service (DoS) vector if multiple authentication requests are sent in quick succession. In a future PR, this threat will be mitigated via Redis rate-limiting to prevent thread pool saturation. Distributed DoS (DDoS) mitigation would require infrastructure-level solutions, which are outside the scope of this project.

- Regarding password composition rules, OWASP actually recommends against composition rules in favour of length, as users tend to make predictable substitutions e.g. swapping an 'a' for '@'. In this case, composition rules have been used as a deliberate design choice for this project, with awareness of the usability tradeoff.

## Load Testing & Performance

**TL;DR:** Synchronous local SQLite can match asynchronous PostgreSQL at low concurrency when WAL mode and multiple workers are used, but its fundamental write‑locking design still caps scalability. As concurrency rises, serialized writes trigger lock contention, stalled connections, and eventual TimeoutError pool exhaustion. Migrating to PostgreSQL with asyncpg removes this bottleneck entirely through MVCC, enabling true concurrent reads and writes. Additionally, AES‑256‑GCM encryption is so fast natively (<1ms) that offloading it to an async threadpool only adds unnecessary context‑switching overhead, increasing latency by ~5ms instead of reducing it.

<details>
<summary>View Load Testing & Performance Tests</summary>

### Encryption and threadpools

- As encryption is CPU-bound, three strategies were load-tested at 100 concurrent users (to prevent write-locking of SQLite):
  - No encryption: 39.8 ms median
  - Synchronous AES‑256‑GCM: 39.9 ms median
  - Threadpool AES‑256‑GCM: 45.0 ms median

- At this scale, AES-256-GCM encryption introduces minimal overhead, whereas offloading it to a threadpool introduced ~5 ms median overhead (and a worse p95 latency), showing the context-switching when running it in a threadpool exceeded the actual encryption process. While both AES-256-GCM and Argon2 are implemented in C, AES encryption is hardware accelerated, whereas Argon2 hashing is deliberately slow. Following this, I stripped `run_in_threadpool` from all encrypt/decrypt function calls.

### Synchronous SQLite vs Asynchronous PostgreSQL

- This project originally used SQLite, but was migrated to PostgreSQL. Before doing this, I performed relative tests to see exactly SQLite fell short of PostgreSQL under high concurrencies. Test conditions were kept constant, relative to one another, but did not match a production system's. A full breakdown of the methodology, configurations, and results can be found in [benchmarks/README.md](./benchmarks/README.md). 

To summarise:
- SQLite performs well at low concurrency but cannot scale well due to serialized writes and file‑locking. With proper configuration and WAL mode, it is suitable for lightweight or read-heavy applications.
- PostgreSQL’s MVCC enables true concurrent reads/writes and scales linearly under load, making it ideal for applications that are expected to handle high write concurrency.

All detailed metrics, p50/p95/p99 latencies, and concurrency scaling tests (200–800 users) are documented in the dedicated load‑testing report.

</details>