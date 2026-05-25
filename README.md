# Blog App FastAPI

A simple async blog API built with **FastAPI**, **SQLModel**, **PostgreSQL**, and basic **JWT authentication**.

## Features

- Create, read, update, publish/unpublish, and delete blog posts
- User signup and login
- JWT access tokens
- Logout support with Redis token blacklist
- Async PostgreSQL database access
- Automatic table creation when the app starts
- Swagger UI and Scalar API docs

## Tech Stack

- Python 3.13
- FastAPI
- SQLModel
- SQLAlchemy async sessions
- PostgreSQL with `asyncpg`
- Redis
- PyJWT
- Passlib / bcrypt
- uv
- Docker Compose

## Project Structure

```text
blog-app-fastapi/
├── app/
│   └── src/
│       ├── api/              # FastAPI dependencies
│       ├── core/             # Auth/security setup
│       ├── database/         # PostgreSQL and Redis setup
│       ├── models/           # SQLModel database models
│       ├── routers/          # API routes
│       ├── schemas/          # Request/response schemas
│       ├── services/         # Business logic
│       ├── config.py         # App settings
│       └── main.py           # FastAPI app
├── compose.yml               # PostgreSQL and Redis services
├── pyproject.toml            # Project dependencies
├── uv.lock                   # Locked dependencies
└── README.md
```

## Requirements

- Python `>=3.13`
- `uv`
- Docker and Docker Compose, or your own PostgreSQL and Redis services

## Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Example values for the services in `compose.yml`:

```env
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=fastapi
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/fastapi

REDIS_HOST=localhost
REDIS_PORT=6379

JWT_SECRET=change-this-secret
JWT_ALGORITHM=HS256
```

Do not commit your real `.env` file.

## Start and Stop Databases

`compose.yml` starts PostgreSQL and Redis for local development.

Start both services:

```bash
docker compose up -d
```

Check running services:

```bash
docker compose ps
```

Stop services without deleting data:

```bash
docker compose stop
```

Start stopped services again:

```bash
docker compose start
```

Stop and remove containers/network, but keep PostgreSQL data:

```bash
docker compose down
```

Stop and remove everything, including PostgreSQL volume data:

```bash
docker compose down -v
```

> `docker compose down -v` deletes the local PostgreSQL data volume.

## Installation

Install dependencies:

```bash
uv sync
```

## Run the App

Make sure PostgreSQL and Redis are running first:

```bash
docker compose up -d
```

Start the API:

```bash
uv run uvicorn app.src.main:app --reload
```

Open the docs:

- Swagger UI: <http://127.0.0.1:8000/docs>
- Scalar: <http://127.0.0.1:8000/scalar>
- ReDoc: <http://127.0.0.1:8000/redoc>

## API Endpoints

### Users

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/users/signup` | Create a user |
| `POST` | `/users/login` | Login and get JWT token |
| `POST` | `/users/logout` | Logout and blacklist current token |

### Posts

Base prefix: `/post`

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/post/all` | Get all blog posts |
| `GET` | `/post/{id}` | Get one blog post by ID |
| `POST` | `/post/create` | Create a new blog post |
| `PUT` | `/post/publish/{id}` | Publish or unpublish a blog post |
| `PUT` | `/post/update/{id}` | Update a blog post |
| `DELETE` | `/post/delete/{id}` | Delete a blog post |

## Example Requests

Sign up:

```bash
curl -X POST http://127.0.0.1:8000/users/signup \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","password":"Password123"}'
```

Login:

```bash
curl -X POST http://127.0.0.1:8000/users/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Password123"}'
```

Use the returned token:

```text
Authorization: Bearer <JWT_TOKEN>
```

Create a post:

```bash
curl -X POST http://127.0.0.1:8000/post/create \
  -H "Content-Type: application/json" \
  -d '{"title":"My First Post","content":"Hello","slug":"my-first-post","is_published":false}'
```

Logout:

```bash
curl -X POST http://127.0.0.1:8000/users/logout \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

Logout requires a valid JWT token in the `Authorization` header. When a user logs out, the app stores the token ID in Redis so the same token cannot be used again. Make sure Redis is running with `docker compose up -d` before using logout.

## Check Code

Run lint checks:

```bash
uv run ruff check .
```

Compile Python files:

```bash
uv run python -m compileall app main.py
```

## License

No license file is currently included.
