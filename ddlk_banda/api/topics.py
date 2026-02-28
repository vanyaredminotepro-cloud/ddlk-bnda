from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ddlk_banda.db.models import Chat, ChatType, ForumTopic, TopicStatus
from ddlk_banda.db.session import get_db
from ddlk_banda.schemas.topics import TopicArchive, TopicCreate, TopicDelete, TopicRead

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
    )
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic


@router.get("/{group_id}/topics", response_model=list[TopicRead])
def list_topics(group_id: UUID, db: Session = Depends(get_db)):
    topics = db.execute(
        select(ForumTopic)
        .where(ForumTopic.group_id == group_id, ForumTopic.status != TopicStatus.deleted)
        .order_by(ForumTopic.id.asc())
    ).scalars().all()
    return topics


@router.patch("/{group_id}/topics/{topic_id}", response_model=TopicRead)
def archive_topic(group_id: UUID, topic_id: int, payload: TopicArchive, db: Session = Depends(get_db)):
    topic = db.execute(
        select(ForumTopic).where(ForumTopic.id == topic_id, ForumTopic.group_id == group_id)
    ).scalar_one_or_none()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    topic.status = TopicStatus.archived if payload.archived else TopicStatus.active
    db.commit()
    db.refresh(topic)
    return topic


@router.delete("/{group_id}/topics/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_topic(group_id: UUID, topic_id: int, payload: TopicDelete, db: Session = Depends(get_db)):
    topic = db.execute(
        select(ForumTopic).where(ForumTopic.id == topic_id, ForumTopic.group_id == group_id)
    ).scalar_one_or_none()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    topic.status = TopicStatus.deleted
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
