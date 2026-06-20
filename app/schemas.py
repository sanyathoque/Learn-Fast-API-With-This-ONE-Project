from pydantic import BaseModel


class PostCreate(BaseModel):
    title: str
    content: str


class PostResponse(BaseModel):
    title: str
    content: str


# Used for partial updates (PATCH): every field is optional, so the
# client only has to send the field(s) they actually want to change.
class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
