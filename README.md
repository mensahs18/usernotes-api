# Notes API

A backend API built with FastAPI, that allows users to register, log in, and manage personal notes. Planned to involve user auth, secure auth, with information stored on databases. Eventual update into productivity and scheduling system.

## Features
- [ ] User Greeting
- [ ] User Registration
- [ ] User login
- [ ] Create notes
- [ ] View notes
- [ ] Delete notes

## Tech Stack

- Python
- FastAPI
- SQLite (inital)
- PostgreSQL (planned)

## How to run

Install required dependencies:

`pip install fastapi uvicorn`

Run server:

uvicorn main:app --reload

Open browser:

http://127.0.0.1:8000/docs

## Status:

Incomplete - In Progress

## Current Progress:

- Application initialised
- Models, schemas defined
- Database and session initialised