# Blog App FastAPI

A simple asynchronous blog API built with FastAPI and SQLModel. This project is a learning/demo app that shows how to build async endpoints, use SQLModel for database models, and add basic JWT authentication.

---

## Highlights

- CRUD endpoints for blog posts (create, read, update, publish/unpublish, delete)
- Async database access using `asyncpg` + SQLAlchemy async engine
- Simple JWT authentication for user actions (signup/login)
- Interactive API docs via Swagger UI

## Tech stack

- Python 3.13
- FastAPI
- SQLModel
- asyncpg (PostgreSQL driver)
- uv (dependency manager used by this project)

## Quick Start (beginner friendly)

1. Clone the repo:

```bash
git clone git@github.com:sulemangulzar/blog-app-fastapi.git
cd blog-app-fastapi
```

2. Copy environment file and edit values:

```bash
cp .env.example .env
# then open .env and set DATABASE_URL and other values
```

3. Install dependencies (uses `uv`):

```bash
uv sync
```

4. (Optional) Start a local PostgreSQL using Docker Compose:

```bash
docker compose up -d
```

5. Run the app locally:

```bash
uv run uvicorn app.src.main:app --reload
```

Open the docs at http://127.0.0.1:8000/docs

---

## Environment variables

Copy `.env.example` and update values. Important variable:

- `DATABASE_URL` (example): `postgresql+asyncpg://postgres:postgres@localhost:5432/fastapi`

Do not commit your real `.env` file since it may contain secrets.

---

## Authentication (users)

This app includes a simple JWT-based authentication flow for demonstration.

- Sign up: `POST /users/signup` with JSON body:

```json
{ "name": "Your Name", "email": "you@example.com", "password": "yourpassword" }
```

- Login: `POST /users/login` with JSON body:

```json
{ "email": "you@example.com", "password": "yourpassword" }
```

Response example:

```json
{ "access_token": "<JWT_TOKEN>", "token_type": "bearer" }
```

- Use the token for protected endpoints by sending an `Authorization` header:

```
Authorization: Bearer <JWT_TOKEN>
```

Tip for scalar-fastapi and other tools: some clients wrap long tokens across multiple lines when you copy them. If you paste a wrapped token, make sure it becomes a single continuous string (no spaces or line breaks) after `Bearer ` — the app already strips common surrounding characters and internal whitespace to help with this.

---

## API endpoints (summary)

- Posts (base prefix `/post`):
  - `GET /post/all` — list posts
  - `GET /post/{id}` — get post by id
  - `POST /post/create` — create a post
  - `PUT /post/update/{id}` — update a post
  - `PUT /post/publish/{id}` — publish/unpublish
  - `DELETE /post/delete/{id}` — delete a post

- Users:
  - `POST /users/signup` — create user
  - `POST /users/login` — get JWT token
  - `GET /users/dashboard` — protected example endpoint

---

## Example requests

Signup and login (example with `curl`):

```bash
curl -X POST http://127.0.0.1:8000/users/signup \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","password":"Password123"}'

curl -X POST http://127.0.0.1:8000/users/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Password123"}'
```

Call protected `dashboard` with the returned token:

```bash
curl -H "Authorization: Bearer <JWT_TOKEN>" http://127.0.0.1:8000/users/dashboard
```

Create a post:

```bash
curl -X POST http://127.0.0.1:8000/post/create \
  -H "Content-Type: application/json" \
  -d '{"title":"My First Post","content":"Hello","slug":"my-first-post","is_published":false}'
```

---

## Notes & Next steps

- This is a learning/demo project. For production use add:
  - Database migrations (Alembic)
  - Tests and CI
  - Stronger auth (refresh tokens, password reset)
  - Input validation and consistent error schemas

If you'd like, I can also add a small test for token decoding or create a short CONTRIBUTING.md.

---

## License

No license file is included.

