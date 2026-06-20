import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import PostCreate, PostResponse, PostUpdate
from app.db import Post, create_db_and_tables, get_async_session


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

text_posts = {
    1: {"title": "New Post", "content": "Cool test post"},
    2: {"title": "Python Tip", "content": "Use list comprehensions for cleaner loops."},
    3: {"title": "Daily Motivation", "content": "Consistency beats intensity every time."},
    4: {"title": "Fun Fact", "content": "The first computer bug was an actual moth found in a Harvard Mark II."},
    5: {"title": "Update", "content": "Just launched my new project! Excited to share more soon."},
    6: {"title": "Tech Insight", "content": "Async IO in Python can massively speed up I/O-bound tasks."},
    7: {"title": "Quote", "content": "Programs must be written for people to read, and only incidentally for machines to execute."},
    8: {"title": "Weekend Plans", "content": "Might finally clean up my GitHub repos... or just play some Minecraft"},
    9: {"title": "Question", "content": "What's the most underrated Python library you've ever used?"},
    10: {"title": "Mini Announcement", "content": "New video drops tomorrow-covering the weirdest Python features!"},
}


# ---------------------------------------------------------------------------
# GET requests
# ---------------------------------------------------------------------------

# A simple "root" endpoint. Visiting http://localhost:8000/ hits this.
@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI tutorial API", "docs": "/docs"}


# /posts  -> list every post (with an optional ?limit= query parameter)
@app.get("/posts")
def get_all_posts(limit: int | None = None):
    if limit:
        return list(text_posts.values())[:limit]
    return text_posts


# /posts/count -> how many posts exist.
# NOTE: this is declared BEFORE "/posts/{id}" on purpose. FastAPI matches
# routes top-to-bottom, so the fixed path "count" must win before the
# dynamic "{id}" path tries to read it.
@app.get("/posts/count")
def count_posts():
    return {"count": len(text_posts)}


# /posts/search?keyword=python -> case-insensitive search in title + content.
# This shows how to use a *required* query parameter (keyword has no default).
@app.get("/posts/search")
def search_posts(keyword: str):
    keyword = keyword.lower()
    results = {
        post_id: post
        for post_id, post in text_posts.items()
        if keyword in post["title"].lower() or keyword in post["content"].lower()
    }
    return results


# /posts/{id} -> fetch a single post by its integer id.
@app.get("/posts/{id}")
def get_post(id: int) -> PostResponse:
    if id not in text_posts:
        raise HTTPException(status_code=404, detail="Post not found")
    return text_posts.get(id)


# ---------------------------------------------------------------------------
# POST requests
# ---------------------------------------------------------------------------

# /posts -> create a single new post. The request body is validated against
# the PostCreate schema automatically.
@app.post("/posts", status_code=201)
def create_post(post: PostCreate) -> PostResponse:
    new_post = {"title": post.title, "content": post.content}
    # default=0 avoids a ValueError when the store is empty (e.g. all deleted).
    new_id = max(text_posts.keys(), default=0) + 1
    text_posts[new_id] = new_post
    return new_post


# /posts/bulk -> create several posts in one request.
# Here the body is a *list* of PostCreate objects.
@app.post("/posts/bulk", status_code=201)
def create_posts_bulk(posts: list[PostCreate]) -> list[PostResponse]:
    created = []
    for post in posts:
        new_id = max(text_posts.keys(), default=0) + 1
        new_post = {"title": post.title, "content": post.content}
        text_posts[new_id] = new_post
        created.append(new_post)
    return created


# ---------------------------------------------------------------------------
# PUT / PATCH requests
# ---------------------------------------------------------------------------

# /posts/{id} (PUT) -> FULL update. The client must send every field, and the
# whole post is replaced. Returns the updated post.
@app.put("/posts/{id}")
def update_post(id: int, post: PostCreate) -> PostResponse:
    if id not in text_posts:
        raise HTTPException(status_code=404, detail="Post not found")
    updated_post = {"title": post.title, "content": post.content}
    text_posts[id] = updated_post
    return updated_post


# /posts/{id} (PATCH) -> PARTIAL update. The client sends only the fields they
# want to change; everything else stays the same. This uses PostUpdate, whose
# fields are all optional.
@app.patch("/posts/{id}")
def patch_post(id: int, post: PostUpdate) -> PostResponse:
    if id not in text_posts:
        raise HTTPException(status_code=404, detail="Post not found")

    existing_post = text_posts[id]
    # exclude_unset=True -> only the fields the client actually sent.
    update_data = post.model_dump(exclude_unset=True)
    existing_post.update(update_data)
    text_posts[id] = existing_post
    return existing_post


# /posts/{id} (DELETE) -> delete a post from the in-memory store.
@app.delete("/posts/{id}")
def delete_post_in_memory(id: int):
    if id not in text_posts:
        raise HTTPException(status_code=404, detail="Post not found")
    deleted = text_posts.pop(id)
    return {"success": True, "deleted": deleted}


# /db/posts/{post_id} (DELETE) -> async, database-backed delete example.
# Kept on its own path so it doesn't clash with the in-memory delete above.
@app.delete("/db/posts/{post_id}")
async def delete_post(post_id: str, session: AsyncSession = Depends(get_async_session)):
    try:
        post_uuid = uuid.UUID(post_id)

        result = await session.execute(select(Post).where(Post.id == post_uuid))
        post = result.scalars().first()

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        await session.delete(post)
        await session.commit()

        return {"success": True, "message": "Post deleted successfully"}
    except HTTPException:
        # Let intentional HTTP errors (like the 404 above) pass through
        # unchanged instead of being re-wrapped as a 500.
        raise
    except ValueError:
        # uuid.UUID(post_id) raises ValueError on a malformed id.
        raise HTTPException(status_code=400, detail="Invalid post id")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
