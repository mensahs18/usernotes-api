# Notes API

A secure REST API backend built with FastAPI and SQLAlchemy, implementing JWT authentication and Argon2 hashing. Users can register, authenticate themselves, and manage personal notes via protected endpoints. Designed with production and security principles in mind. Future plans involve changing endpoints to be asynchronous (async) and migrating database to PostgreSQL for improved concurrency and horizontal scaling. Later, aims to include Redis and Docker.

## Features

### Registration and Authentication
- [X] User registration with argon2 hashing for password security
- [X] Field validation for registration using Pydantic schemas
- [X] Login endpoint with JWT token generation
- [X] Token verification and resolution from token
- [X] Password stripped from API responses
- [X] Protected routes using OAuth2 bearer scheme

### Notes
- [ ] Create note (POST /notes)
- [ ] Get all my notes (GET /notes)
- [ ] Get single note (GET /notes/{id})
- [ ] Update note (PUT /notes/{id})
- [ ] Delete note (DELETE /notes/{id})

### Security & Response
- [ ] Ownership validation on note routes
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

Create a `.env` file in the root directory, containing SECRET_KEY:

SECRET_KEY: 'secret_key_here'

Install required dependencies:

`pip install fastapi uvicorn sqlalchemy argon2-cffi pyjwt python-dotenv pydantic`

Run server:

uvicorn main:app --reload

Open browser, and enter Swagger UI at:

http://127.0.0.1:8000/docs

## Status & Current Progress:

- Added login endpoints
- JWT authentication added
- Working on notes POST, DELETE and managing own users notes.

## Design Decisions & Tradeoffs

- SQLite transition to PostgreSQL: PostgreSQL allows for high concurrency and horizontal scaling. SQLite is used initially due to its ease of use, easy testing and simple configuration.

- Argon2 hashing vs `bcrypt` with `passlib`: Although initially considered, bcrypt falls short to argon2 hashing against modern GPU brute force attacks. Argon2 is the winner of the PHC and is reccommended by the OWASP, due to being memory hard.
