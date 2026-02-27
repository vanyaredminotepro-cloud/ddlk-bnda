from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class TopicCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    icon_emoji: str | None = Field(default=None, max_length=16)


class TopicArchive(BaseModel):
    archived: bool = True


class TopicDelete(BaseModel):
    delete_for_all: bool = True


class TopicRead(BaseModel):
    id: int
    group_id: UUID
    title: str
    icon_emoji: str | None
    last_message_id: UUID | None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
