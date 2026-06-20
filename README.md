# Learn-Fast-API-With-This-ONE-Project

A small FastAPI project built while learning the framework. It demonstrates the
core REST building blocks — path & query parameters, request/response models,
and every common HTTP method — backed by a simple in-memory store, plus an
async SQLAlchemy example.

## Project structure

```
.
├── app/
│   ├── __init__.py     # package marker / version
│   ├── app.py          # FastAPI app + all routes
│   ├── schemas.py      # Pydantic models (PostCreate, PostResponse, PostUpdate)
│   └── db.py           # async SQLAlchemy engine, Post model, session
├── main.py             # uvicorn entry point
└── pyproject.toml      # dependencies
```

## Setup

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate

pip install fastapi uvicorn pydantic sqlalchemy aiosqlite python-multipart
```

## Run

```bash
python main.py
```

Then open the interactive API docs at **http://localhost:8000/docs**.

## Endpoints

| Method | Path                  | Description                                   |
|--------|-----------------------|-----------------------------------------------|
| GET    | `/`                   | Welcome message                               |
| GET    | `/posts`              | List all posts (optional `?limit=`)           |
| GET    | `/posts/count`        | Number of posts                               |
| GET    | `/posts/search`       | Search by `?keyword=` (title + content)       |
| GET    | `/posts/{id}`         | Get a single post by id                       |
| POST   | `/posts`              | Create one post                               |
| POST   | `/posts/bulk`         | Create many posts in one request              |
| PUT    | `/posts/{id}`         | Full update (all fields required)             |
| PATCH  | `/posts/{id}`         | Partial update (only changed fields)          |
| DELETE | `/posts/{id}`         | Delete a post (in-memory)                     |
| DELETE | `/db/posts/{post_id}` | Async, database-backed delete example         |

## Concepts demonstrated

- **Path vs query params vs request body** (Pydantic models)
- **Route ordering** — fixed paths (`/posts/count`) declared before `/posts/{id}`
- **PUT vs PATCH** — full replace vs partial update with `exclude_unset=True`
- **Status codes** and `HTTPException` for errors
- **Async dependencies** via `Depends(get_async_session)`
