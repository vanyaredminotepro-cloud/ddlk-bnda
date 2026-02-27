from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ddlk_banda.db.models import Chat, ChatType, ForumTopic, TopicStatus
from ddlk_banda.db.session import get_db
from ddlk_banda.schemas.topics import TopicCreate, TopicRead

router = APIRouter(prefix="/groups", tags=["forum-topics"])


@router.post("/{group_id}/topics", response_model=TopicRead, status_code=status.HTTP_201_CREATED)
def create_topic(group_id: UUID, payload: TopicCreate, db: Session = Depends(get_db)):
    group = db.execute(select(Chat).where(Chat.id == group_id)).scalar_one_or_none()
    if not group or group.type != ChatType.supergroup:
        raise HTTPException(status_code=404, detail="Supergroup not found")
    if not group.is_forum:
        raise HTTPException(status_code=400, detail="Group is not configured as forum")

    topic = ForumTopic(
        group_id=group_id,
        title=payload.title,
        icon_emoji=payload.icon_emoji,
        status=TopicStatus.active,
        created_by=None,
    )
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic
