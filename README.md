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
- [ ] PostgreSQL with `asyncpg` driver

### Architecture & Production
- [X] Refactor into modules
- [X] Project tools (ruff, mypy, precommit)
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

```env
# .env file
SECRET_KEY=secret_key_here
ENCRYPT_KEY=your_32_byte_hex_key_here
```

- `SECRET_KEY` and `ENCRYPT_KEY` can be generated with the following terminal command:

`poetry run python -c "import os; print(os.urandom(32).hex())"`

Install required dependencies:

`poetry install`

Run server:

`poetry run uvicorn main:app --reload`

Open browser, and enter Swagger UI at:

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

### Load Testing & Performance

#### Synchronous SQLite

- I ran some concurrent traffic simulations using Locust, exposing two distinct bottlenecks. I started testing under a load of around 200 concurrent users. After reducing the load, the constraint shifted from the storage layer to application resource limits, resulting in SQLAlchemy `TimeoutError` exceptions, after a brief period. This is because the application held onto connections too long, which exhausted the connection pool, throwing such exception after a brief period.

- The metrics also reflected this. While read operations remained stable, `POST /notes` latencies spiked to a 2000ms 99th percentile because requests waited for available database slots. Migrating to PostgreSQL and switching to an async driver will resolve this by allowing non-blocking, concurrent writes.

#### Encryption and threadpools

- As encryption is CPU-bound, three strategies were load-tested at 100 concurrent users (to prevent write-locking of SQLite):
  - No encryption: 39.8 ms median
  - Synchronous AES‑256‑GCM: 39.9 ms median
  - Threadpool AES‑256‑GCM: 45.0 ms median

- At this scale, AES-256-GCM encryption introduces minimal overhead, whereas offloading it to a threadpool introduced ~5 ms median overhead (and a worse p95 latency), showing the context-switching when running it in a threadpool exceeded the actual encryption process. While both AES-256-GCM and Argon2 are implemented in C, AES encryption is hardware accelerated, whereas Argon2 hashing is deliberately slow. Following this, I stripped `run_in_threadpool` from all encrypt/decrypt function calls.