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
- [ ] Note pagination

### Security & Response
- [X] Ownership validation on note routes
- [X] JWT expiration handling
- [ ] Token refreshing
- [ ] Rate limiting (Redis) against DoS

### Testing
- [X] Pytest test suite
- [X] Authentication tests
- [X] API Integration tests
- [X] Async testing

### Async & Database
- [X] Migrate to async routes and async SQLAlchemy
- [ ] PostgreSQL with `asyncpg` driver

### Architecture & Production
- [X] Refactor into modules
- [ ] Project tools (i.e. poetry, ruff, black)
- [ ] Dockerfile
- [ ] Docker Compose
- [ ] Logging


## Tech Stack

- Python
- `FastAPI`
- `SQLAlchemy` via ORM
- SQLite (current) -> PostgreSQL (planned)
- `Argon2`
- `PyJWT`

## How to run

Create a `.env` file in the root directory:

```python
# .env file
SECRET_KEY=secret_key_here
ENCRYPT_KEY=your_32_byte_hex_key_here
```

- `ENCRYPT_KEY` can be generated with the following terminal command:

`python -c "import os; print(os.urandom(32).hex())"`

Install required dependencies:

`pip install -r requirements.txt`

Run server:

`uvicorn main:app --reload`

Open browser, and enter Swagger UI at:

http://127.0.0.1:8000/docs


## Design Decisions & Tradeoffs

- SQLite transition to PostgreSQL: PostgreSQL allows for high concurrency and horizontal scaling. SQLite is used initially due to its ease of use, easy testing and simple configuration.
- Write Concurrency Limits: Testing in the `notes-routes` PR confirms SQLite locks under concurrent `POST` requests. By design, SQLite serialises writes while allowing parallel reads. PostgreSQL is preferred for production due to its support for concurrent writes.
- AioSQLite vs PostgreSQL: While `aiosqlite` uses a background thread pool to enable asynchronous code, it is still bound by SQLite's write-lock limitation under heavy load. PostgreSQL supports asynchronous drivers and allows concurrent reads and writes without blocking.

- Username Case-Sensitivity: Usernames were initially case-sensitive at the database level. A follow-up step i.e. lowercasing on registration and login, has been executed to prevent duplicate accounts and authentication friction between equivalent usernames such as `admin1` and `Admin1`.

- `AES-256-GCM` over `Fernet`: Chosen over Fernet (AES-128-CBC) for stronger key length and built-in integrity verification. GCM mode provides both confidentiality via encryption and both authenticity and integrity via authentication tag, preventing ciphertext tampering.

- Argon2 hashing vs. `bcrypt` with `passlib`: Although initially considered, bcrypt falls short of argon2 hashing against modern GPU brute force attacks. Argon2 is the winner of the PHC and is recommended by the OWASP, due to being memory-hard.
- Maximum Password Length vs. CPU Exhaustion (DoS): Allowing 128 characters in password introduces a potential Denial of Service (DoS) vector, as hashing large inputs with Argon2 is computationally expensive. Accepted as a trade-off to prioritise user password flexibility. In a future PR, application-level CPU exhaustion DoS attacks on authentication will be mitigated via Redis rate-limiting, over shortening user inputs. Distributed DoS (DDoS) mitigation would require infrastructure level solutions, which are outside of the scope of this project.
- Password composition rules vs OWASP guidance: OWASP  recommends against composition rules in favour of length. Composition rules retained as a deliberate design choice for this project, with awareness of the usability tradeoff.

### Load Testing & Performance

#### Synchronous SQLite

- Concurrency Load Testing: Simulated concurrent traffic, via Locust, indicated two distinct bottlenecks. Initially tested under a load of around 200 concurrent users. After reducing the load, the constraint shifted from the storage layer to application resource limits, resulting in SQLAlchemy `TimeoutError` exceptions, after a brief period.

- Connection Pool Exhaustion: The metrics reflected this resource starvation. While read operations remained stable, `POST /notes` latencies spiked to a 2000ms 99th percentile. Likely a result of connection starvation, migrating to PostgreSQL and use of an async driver should allow concurrent writes without these bottlenecks.

#### Encryption and threadpools

- As encryption is CPU-bound, three strategies were load-tested at 100 concurrent users (to prevent write-locking of SQLite):
  - No encryption: 39.8 ms median
  - Synchronous AES‑256‑GCM: 39.9 ms median
  - Threadpool AES‑256‑GCM: 45.0 ms median

- At this scale, AES-256-GCM encryption introduces minimal overhead, whereas offloading it to a threadpool introduced ~5 ms median overhead (and a worse p95 latency), showing the context-switching when running it in a threadpool exceeded the actual encryption process. While both AES-256-GCM and Argon2 are implemented in C, AES encryption is hardware accelerated, whereas Argon2 hashing is deliberately slow. Following this, `run_in_threadpool` stripped from all encrypt/decrypt function calls.