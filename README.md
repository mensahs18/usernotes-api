# Notes API

A secure REST API backend built with FastAPI and SQLAlchemy, implementing JWT authentication and Argon2 hashing. Users can register, authenticate themselves, and manage personal notes via protected endpoints. Designed with production and security principles in mind. Future plans involve changing endpoints to be asynchronous (async) and migrating database to PostgreSQL for improved concurrency and horizontal scaling. Later, aims to include Redis and Docker.

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
- [ ] JWT expiration handling
- [ ] Token refreshing
- [ ] Rate limiting (Redis) against DoS

### Testing
- [ ] Pytest test suite
- [ ] Authentication tests
- [ ] API Integration tests
- [ ] Async testing

### Async & Database
- [ ] Migrate to async routes and async SQLAlchemy
- [ ] PostgreSQL with asyncpg driver

### Architecture & Production
- [ ] Refactor into modules
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

SECRET_KEY = 'secret_key_here'

Install required dependencies:

`pip install fastapi uvicorn sqlalchemy argon2-cffi pyjwt python-dotenv pydantic`

Run server:

uvicorn main:app --reload

Open browser, and enter Swagger UI at:

http://127.0.0.1:8000/docs

## Status & Current Progress:

- Notes table and Pydantic schemas added
- Added notes CRUD routes: GET, POST, PATCH (instead of PUT, to align with convention) and DELETE
- Protected all routes, and added valid status codes
- Incremental integer ID replaced with UUID for better scalability
- UUID alongside get_current_user() dependency, and object-level auth prevents BOLA
- Working on refactoring project, then writing unit and integration tests for both CRUD and authentication
- Async/postgre planned

## Design Decisions & Tradeoffs

- SQLite transition to PostgreSQL: PostgreSQL allows for high concurrency and horizontal scaling. SQLite is used initially due to its ease of use, easy testing and simple configuration.
- Write Concurrency Limits: Testing in the `notes-routes` PR confirms SQLite locks under concurrent `POST` requests. By design, SQLite serialises writes while allowing parallel reads. PostgreSQL is architected and preferred in my use case for high-concurrency write access.

- Argon2 hashing vs. `bcrypt` with `passlib`: Although initially considered, bcrypt falls short of argon2 hashing against modern GPU brute force attacks. Argon2 is the winner of the PHC and is recommended by the OWASP, due to being memory-hard.

### Load Testing & Performance

- Concurrency Load Testing: Simulated concurrent traffic, via Locust, indicated two distinct bottlenecks. Initially tested under a load of around 200 concurrent users. After reducing the load, the constraint shifted from the storage layer to application resource limits, resulting in SQLAlchemy `TimeoutError` exceptions, after a brief period.

- Connection Pool Exhaustion: The metrics reflected this resource starvation. While read operations remained stable (though large byte-wise, due to concurrent posting), `POST /notes` latencies spiked to a 2000ms 99th percentile. Likely a result of connection starvation, migrating to PostgreSQL and use of an async driver should allow concurrent writes without these bottlenecks.