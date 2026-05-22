# Blog App FastAPI

A simple asynchronous blog API built with **FastAPI**, **SQLModel**, **SQLAlchemy async sessions**, and **PostgreSQL**. The app provides CRUD endpoints for blog posts and creates database tables automatically when the FastAPI application starts.

## Features

- Create, read, update, publish/unpublish, and delete blog posts
- Async PostgreSQL database access using `asyncpg`
- SQLModel model definitions for database tables
- Pydantic schemas for request and response validation
- Dependency-injected database session and blog service layer
- Automatic table creation during FastAPI lifespan startup
- Interactive API docs through FastAPI Swagger UI

## Tech Stack

- Python 3.13
- FastAPI
- SQLModel
- SQLAlchemy async engine/session
- asyncpg
- Pydantic Settings
- PostgreSQL
- uv for dependency management

## Project Structure

```text
blog-app-fastapi/
├── api/
│   └── dependencies.py      # FastAPI dependency providers
├── database/
│   └── database.py          # Async engine, session, and table creation
├── models/
│   └── blog.py              # SQLModel database model
├── routers/
│   └── routers.py           # Blog post API routes
├── schemas/
│   └── blog.py              # Request/response schemas
├── services/
│   └── blog.py              # Blog business logic and database operations
├── config.py                # Environment-based settings
├── main.py                  # FastAPI application entry point
├── pyproject.toml           # Project metadata and dependencies
├── uv.lock                  # Locked dependency versions
├── .env.example             # Example environment variables
└── README.md
```

## API Endpoints

Base prefix: `/post`

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/post/all` | Get all blog posts |
| `GET` | `/post/{id}` | Get one blog post by ID |
| `POST` | `/post/create` | Create a new blog post |
| `PUT` | `/post/publish/{id}` | Publish or unpublish a blog post |
| `PUT` | `/post/update/{id}` | Update a blog post |
| `DELETE` | `/post/delete/{id}` | Delete a blog post |

## Data Model

A blog post contains:

- `id`: integer primary key
- `title`: post title
- `content`: post body/content
- `slug`: URL-friendly identifier
- `is_published`: publication status
- `created_at`: creation timestamp
- `updated_at`: update timestamp

## Requirements

- Python `>=3.13`
- PostgreSQL running locally or remotely
- `uv` installed

## Environment Variables

Create a `.env` file in the project root. You can copy `.env.example`:

```bash
cp .env.example .env
```

Example values:

```env
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=blog_app
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/blog_app
```

> Do not commit your real `.env` file. It may contain database credentials.

## Installation

1. Clone the repository:

```bash
git clone git@github.com:sulemangulzar/blog-app-fastapi.git
cd blog-app-fastapi
```

2. Install dependencies:

```bash
uv sync
```

3. Configure environment variables:

```bash
cp .env.example .env
```

4. Update `.env` with your PostgreSQL credentials and database name.

## Running the App

Start the development server:

```bash
uv run fastapi dev main.py
```

Or run with Uvicorn directly:

```bash
uv run uvicorn main:app --reload
```

Open the API docs:

- Swagger UI: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>

## Example Requests

Create a post:

```bash
curl -X POST http://127.0.0.1:8000/post/create \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Post",
    "content": "This is my first blog post.",
    "slug": "my-first-post",
    "is_published": false
  }'
```

Publish a post:

```bash
curl -X PUT http://127.0.0.1:8000/post/publish/1 \
  -H "Content-Type: application/json" \
  -d '{"is_published": true}'
```

Update a post:

```bash
curl -X PUT http://127.0.0.1:8000/post/update/1 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Title",
    "content": "Updated content.",
    "slug": "updated-title"
  }'
```

Delete a post:

```bash
curl -X DELETE http://127.0.0.1:8000/post/delete/1
```

## Current App Status

The app has the foundation of a working CRUD blog API and is suitable as a small learning/demo project. It is not fully production-ready yet.

Recommended next improvements:

- Add automated tests
- Add authentication/authorization for creating, updating, publishing, and deleting posts
- Add database migrations with Alembic instead of relying only on automatic table creation
- Add pagination and filtering for the post list endpoint
- Add validation for unique slugs
- Update `updated_at` automatically when posts change
- Add consistent error response schemas

## License

No license file is currently included.
