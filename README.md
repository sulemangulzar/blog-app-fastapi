# Blog App Backend - FastAPI

A backend API for a blog application built with **FastAPI**, **SQLModel/SQLAlchemy**, **PostgreSQL**, **Alembic**, and **JWT authentication**.

This backend supports:

- User registration and login
- JWT access and refresh tokens
- User profile endpoint
- Blog posts with draft/published/archived status
- Tags attached directly to posts
- Comments and nested comment support
- Likes
- Bookmarks
- PostgreSQL database migrations with Alembic
- Scalar/OpenAPI API documentation

---

## Tech Stack

- Python 3.13+
- FastAPI
- SQLModel
- SQLAlchemy Async
- PostgreSQL
- asyncpg
- Alembic
- PyJWT
- pwdlib / Argon2 password hashing
- Uvicorn

---

## Project Structure

```text
blog-app-fastapi/
├── app/
│   ├── api/v1/routes/
│   │   ├── auth.py
│   │   └── post.py
│   ├── core/
│   │   ├── jwt.py
│   │   └── security.py
│   ├── models/
│   │   ├── user.py
│   │   ├── post.py
│   │   ├── comment.py
│   │   ├── tag.py
│   │   ├── post_like.py
│   │   └── post_bookmark.py
│   ├── schemas/
│   │   ├── auth.py
│   │   └── post.py
│   ├── services/
│   │   ├── auth.py
│   │   └── post.py
│   ├── config.py
│   ├── database.py
│   └── dependencies.py
├── migrations/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── alembic.ini
├── main.py
├── pyproject.toml
├── uv.lock
├── .env.example
└── README.md
```

---

## Main Features

### Authentication

Users can:

- Register
- Login
- Get current profile
- Update profile
- Refresh access token

### Posts

Users can:

- Create posts
- List published posts
- Search posts
- Filter posts by tag
- Get post by ID
- Get post by slug
- Update their own posts
- Delete their own posts

Admins can update/delete any post.

### Tags

Tags are added directly when creating or updating a post.

Example:

```json
{
  "title": "Learning FastAPI",
  "content": "FastAPI is great...",
  "status": "published",
  "tags": ["fastapi", "python"]
}
```

The backend automatically:

1. Cleans tag names.
2. Reuses existing tags.
3. Creates missing tags.
4. Connects tags to the post.

There is also a read-only endpoint to list tags.

### Comments

Users can:

- Add comments to posts
- Reply to comments using `parent_comment_id`
- Edit their own comments
- Delete their own comments

Comments are soft-deleted using `deleted_at`.

### Likes and Bookmarks

Users can:

- Like/unlike posts
- Bookmark/remove bookmark from posts

---

## Setup

### 1. Clone the project

```bash
git clone <your-repo-url>
cd blog-app-fastapi
```

### 2. Install dependencies

This project uses `uv`.

```bash
uv sync
```

If you do not use `uv`, install dependencies another way from `pyproject.toml`.

---

## Environment Variables

Create a `.env` file in the project root.

You can copy the example file:

```bash
cp .env.example .env
```

Example `.env`:

```env
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/blog_app
JWT_SECRET=change-this-to-a-long-random-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Important

Do **not** commit `.env` to GitHub.

Your real `.env` contains secrets. Only commit `.env.example`.

---

## Database Setup

Make sure PostgreSQL is running and your database exists.

Example database name:

```text
blog_app
```

Then run migrations:

```bash
alembic upgrade head
```

Check current migration:

```bash
alembic current
```

Check if models and migrations are in sync:

```bash
alembic check
```

Create a new migration after model changes:

```bash
alembic revision --autogenerate -m "describe your change"
```

Then apply it:

```bash
alembic upgrade head
```

---

## Run the Server

From the project root:

```bash
uvicorn main:app --reload
```

The API will run at:

```text
http://127.0.0.1:8000
```

Health check:

```text
GET /health
```

Docs:

```text
http://127.0.0.1:8000/docs
```

Scalar docs:

```text
http://127.0.0.1:8000/scalar
```

---

## API Endpoints

### Auth

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| POST | `/auth/register` | Register user | No |
| POST | `/auth/login` | Login user | No |
| POST | `/auth/refresh` | Refresh access token | Refresh token |
| GET | `/auth/me` | Get current user | Yes |
| PUT | `/auth/me` | Update current user | Yes |

### Posts

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| POST | `/posts/` | Create post | Yes |
| GET | `/posts/` | List posts | No |
| GET | `/posts/{post_id}` | Get post by ID | No |
| GET | `/posts/slug/{slug}` | Get post by slug | No |
| PATCH | `/posts/{post_id}` | Update post | Yes |
| DELETE | `/posts/{post_id}` | Delete post | Yes |
| GET | `/posts/tags` | List tags | No |

### Comments

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| POST | `/posts/{post_id}/comments` | Create comment | Yes |
| GET | `/posts/{post_id}/comments` | List comments for post | No |
| PATCH | `/posts/comments/{comment_id}` | Update comment | Yes |
| DELETE | `/posts/comments/{comment_id}` | Delete comment | Yes |

### Likes

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| POST | `/posts/{post_id}/like` | Like post | Yes |
| DELETE | `/posts/{post_id}/like` | Unlike post | Yes |

### Bookmarks

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| POST | `/posts/{post_id}/bookmark` | Bookmark post | Yes |
| DELETE | `/posts/{post_id}/bookmark` | Remove bookmark | Yes |

---

## Example Requests

### Register

```http
POST /auth/register
Content-Type: application/json
```

```json
{
  "username": "suleman",
  "email": "suleman@example.com",
  "password": "strongpassword123",
  "display_name": "Suleman"
}
```

---

### Login

Login uses OAuth2 form data, not JSON.

```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded
```

Form fields:

```text
username=suleman@example.com
password=strongpassword123
```

Response:

```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer"
}
```

Use the access token like this:

```http
Authorization: Bearer your_access_token
```

---

### Create Post

```http
POST /posts/
Authorization: Bearer your_access_token
Content-Type: application/json
```

```json
{
  "title": "Learning FastAPI",
  "content": "FastAPI is a modern Python web framework.",
  "excerpt": "A short intro to FastAPI.",
  "status": "published",
  "tags": ["fastapi", "python", "backend"]
}
```

---

### List Posts

```http
GET /posts/
```

With search:

```http
GET /posts/?search=fastapi
```

With tag filter:

```http
GET /posts/?tag=python
```

With pagination:

```http
GET /posts/?skip=0&limit=20
```

---

### Create Comment

```http
POST /posts/{post_id}/comments
Authorization: Bearer your_access_token
Content-Type: application/json
```

```json
{
  "content": "Great post!"
}
```

Reply to another comment:

```json
{
  "content": "I agree with you.",
  "parent_comment_id": "comment-uuid-here"
}
```

---

### Like Post

```http
POST /posts/{post_id}/like
Authorization: Bearer your_access_token
```

---

### Bookmark Post

```http
POST /posts/{post_id}/bookmark
Authorization: Bearer your_access_token
```

---

## How the Data Relates

```text
User
 ├── writes many Posts
 ├── writes many Comments
 ├── likes many Posts
 └── bookmarks many Posts

Post
 ├── belongs to one User author
 ├── has many Comments
 ├── has many Tags
 ├── has many Likes
 └── has many Bookmarks

Tag
 └── belongs to many Posts

Comment
 ├── belongs to one Post
 ├── belongs to one User author
 └── can reply to another Comment
```

---

## Migration Notes

Migrations should be pushed to GitHub.

Commit these:

```text
alembic.ini
migrations/env.py
migrations/script.py.mako
migrations/versions/*.py
```

Do not delete old migration files after they have been applied.

Alembic uses them to understand database history.

---

## Git Ignore

Do not commit:

```text
.env
.venv/
__pycache__/
.DS_Store
*.db
*.sqlite
```

Commit:

```text
.env.example
README.md
migrations/
app/
main.py
pyproject.toml
uv.lock
```

---

## Small Production Checklist

Before deploying:

- Use a strong `JWT_SECRET`
- Use HTTPS
- Use a real PostgreSQL database
- Set CORS allowed origins for your frontend
- Run `alembic upgrade head` on the server
- Do not expose `.env`
- Keep migrations committed
- Add tests for auth and posts
- Add rate limiting for login later
- Add logging later

---

## Useful Commands

Run server:

```bash
uvicorn main:app --reload
```

Apply migrations:

```bash
alembic upgrade head
```

Create migration:

```bash
alembic revision --autogenerate -m "your message"
```

Check migration sync:

```bash
alembic check
```

Check current migration:

```bash
alembic current
```

---

## Current Backend Status

The backend currently includes the core features needed for a small production blog API:

```text
auth
users
posts
tags
comments
likes
bookmarks
migrations
JWT security
PostgreSQL async database
```
