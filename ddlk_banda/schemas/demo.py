from uuid import UUID

from pydantic import BaseModel


class DemoBootstrapResponse(BaseModel):
    group_id: UUID
    title: str
    is_forum: bool


class GroupRead(BaseModel):
    id: UUID
    title: str | None
    is_forum: bool

    class Config:
        from_attributes = True
