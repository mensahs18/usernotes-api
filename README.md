# Notes API

[![Tests](https://github.com/mensahs18/usernotes-api/actions/workflows/main.yml/badge.svg)](https://github.com/mensahs18/usernotes-api/actions/workflows/main.yml)

A secure asynchronous REST API backend built with FastAPI and SQLAlchemy, implementing JWT authentication and Argon2 hashing. Users can register, authenticate themselves, and manage personal notes via protected endpoints. Designed with production and security principles in mind. Future plans involve migrating database to PostgreSQL for improved concurrency and horizontal scaling. Later, aims to include Redis and Docker.

## Features

### Registration and Authentication
- [X] User registration with argon2 hashing for password security
- [X] Field validation for registration using Pydantic schemas
- [X] Login endpoint with JWT token generation
- [X] Token verification and user resolution from token
- [X] Password stripped from API responses
- [X] Protected routes using OAuth2 bearer scheme

### Notes
- [X] Create note (POST /notes)
- [X] Get all my notes (GET /notes)
- [X] Get single note (GET /notes/{id})
- [X] Update note (PATCH /notes/{id})
- [X] Delete note (DELETE /notes/{id})

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
- [ ] PostgreSQL with asyncpg driver

### Architecture & Production
- [X] Refactor into modules
- [ ] Dockerfile
- [ ] Docker Compose
- [ ] Logging


## Tech Stack

- Python
- FastAPI
- SQLAlchemy via ORM
- SQLite (current) -> PostgreSQL (planned)
- Argon2
- PyJWT

## How to run

Create a `.env` file in the root directory, containing a *SECRET_KEY*.

`SECRET_KEY = 'secret_key_here'`

Install required dependencies:

`pip install -r requirements.txt`

Run server:

`uvicorn main:app --reload`

Open browser, and enter Swagger UI at:

http://127.0.0.1:8000/docs

## Status & Current Progress:

- Project refactored into modular components
- Integration tests for both routes and authentication implemented for all routes, testing both happy paths and edge cases, such as unauthenticated and unauthorized users.
- Routes are now asynchronous, using aiosqlite initially
- Hashing logic offloaded to run in thread pool to prevent CPU blocking
- Tests are functioning after refactor to async, with test coverage of 96%
- Async/aiosqlite implemented
- Usernames normalised in database and password validation entropy improved

- Version tested and functioning
- Note encryption planned
- PostgreSQL planned

## Design Decisions & Tradeoffs

- SQLite transition to PostgreSQL: PostgreSQL allows for high concurrency and horizontal scaling. SQLite is used initially due to its ease of use, easy testing and simple configuration.
- Write Concurrency Limits: Testing in the `notes-routes` PR confirms SQLite locks under concurrent `POST` requests. By design, SQLite serialises writes while allowing parallel reads. PostgreSQL is architected and preferred in my inital implementation for high-concurrency write access.
- AioSQLite vs PostgreSQL: While `aiosqlite` uses a background thread pool to enable asynchronous code, it is still bound by SQLite's write-lock limitation under heavy load. PostgreSQL supports asynchronous drivers and allows concurrent reads and writes without blocking.

- Username Case-Sensitivity: Usernames were initially case-sensitive at the database level. A follow-up step i.e. lowercasing on registration and login, has been executed to prevent duplicate accounts and authentication friction between equivalent usernames such as `admin1` and `Admin1`.

- Argon2 hashing vs. `bcrypt` with `passlib`: Although initially considered, bcrypt falls short of argon2 hashing against modern GPU brute force attacks. Argon2 is the winner of the PHC and is recommended by the OWASP, due to being memory-hard.
- Maximum Password Length vs. CPU Exhaustion (DoS): Allowing 128 characters in password introduces a potential Denial of Service (DoS) vector, as hashing large inputs with Argon2 is computationally expensive. Accepted as a trade-off to prioritise user password flexibility. In a future PR, application-level CPU exhaustion DoS attacks on authentication will be mitigated via Redis rate-limiting, over shortening user inputs. Distributed DoS (DDos) mitigation would require infrastructure level solutions, which are outside of the scope of this project.


### Load Testing & Performance

#### Synchronous SQLite

- Concurrency Load Testing: Simulated concurrent traffic, via Locust, indicated two distinct bottlenecks. Initially tested under a load of around 200 concurrent users. After reducing the load, the constraint shifted from the storage layer to application resource limits, resulting in SQLAlchemy `TimeoutError` exceptions, after a brief period.

- Connection Pool Exhaustion: The metrics reflected this resource starvation. While read operations remained stable (though large byte-wise, due to concurrent posting), `POST /notes` latencies spiked to a 2000ms 99th percentile. Likely a result of connection starvation, migrating to PostgreSQL and use of an async driver should allow concurrent writes without these bottlenecks.

#### Encryption and threadpools

- As encryption is CPU-bound, three strategies were load-tested at 100 concurrent users (to prevent write-locking of SQLite):
  - No encryption: 39.8 ms median
  - Synchronous AES‑256‑GCM: 39.9 ms median
  - Threadpool AES‑256‑GCM: 45.0 ms median

- At this scale, AES-256-GCM encryption introduces minimal overhead, whereas offloading it to a threadpool introduced ~5 ms median overhead (and a worse p95 latency), showing the context-switching when running it in a threadpool exceeded the actual encryption process. While both AES-256-GCM and Argon2 are implemented in C, AES encryption is hardware accelerated, whereas Argon2 hashing is deliberately slow. Following this, `run_in_threadpool` stripped from all encrypt/decrypt function calls.