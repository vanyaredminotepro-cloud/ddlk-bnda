import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ddlk_banda.db.models import Chat, ChatType
from ddlk_banda.db.session import get_db
from ddlk_banda.schemas.demo import DemoBootstrapResponse, GroupRead

router = APIRouter(prefix="/demo", tags=["demo"])


@router.post("/bootstrap", response_model=DemoBootstrapResponse)
def bootstrap_demo(db: Session = Depends(get_db)):
    chat = db.execute(
        select(Chat).where(Chat.type == ChatType.supergroup, Chat.is_forum.is_(True)).limit(1)
    ).scalar_one_or_none()
    if not chat:
        chat = Chat(
            id=uuid.uuid4(),
            type=ChatType.supergroup,
            title="ddlk-banda Forum Demo",
            is_forum=True,
        )
        db.add(chat)
        db.commit()
        db.refresh(chat)

    return DemoBootstrapResponse(group_id=chat.id, title=chat.title or "Forum", is_forum=chat.is_forum)


@router.get("/groups", response_model=list[GroupRead])
def list_groups(db: Session = Depends(get_db)):
    groups = db.execute(select(Chat).where(Chat.type == ChatType.supergroup).order_by(Chat.created_at.desc())).scalars().all()
    return [GroupRead.model_validate(group) for group in groups]
