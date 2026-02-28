from sqlalchemy import select
from sqlalchemy.orm import Session

from ddlk_banda.db.models import Message, OutboxQueue, SyncState


class SyncService:
    """Implements optimistic-send acknowledgement and seq/state reconciliation."""

    @staticmethod
    def enqueue_local_message(db: Session, user_id, device_id, chat_id, client_msg_id: str, payload: dict) -> OutboxQueue:
        item = OutboxQueue(
            user_id=user_id,
            device_id=device_id,
            chat_id=chat_id,
            client_msg_id=client_msg_id,
            payload=payload,
            state="pending",
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def ack_server_seq(db: Session, user_id, device_id, chat_id, chat_seq: int) -> None:
        state = db.execute(
            select(SyncState).where(
                SyncState.user_id == user_id,
                SyncState.device_id == device_id,
                SyncState.chat_id == chat_id,
            )
        ).scalar_one_or_none()
        if not state:
            state = SyncState(user_id=user_id, device_id=device_id, chat_id=chat_id, last_acked_chat_seq=chat_seq)
            db.add(state)
        else:
            state.last_acked_chat_seq = max(state.last_acked_chat_seq, chat_seq)
        db.commit()

    @staticmethod
    def get_gap_messages(db: Session, chat_id, last_acked_seq: int, limit: int = 500):
        return db.execute(
            select(Message)
            .where(Message.chat_id == chat_id, Message.chat_seq > last_acked_seq)
            .order_by(Message.chat_seq.asc())
            .limit(limit)
        ).scalars().all()
