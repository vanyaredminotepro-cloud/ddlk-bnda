from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base for ddlk-banda ORM models."""


class ChatType(str, enum.Enum):
    direct = "direct"
    group = "group"
    supergroup = "supergroup"
    channel = "channel"


class MembershipRole(str, enum.Enum):
    owner = "owner"
    admin = "admin"
    member = "member"
    readonly = "readonly"


class TopicStatus(str, enum.Enum):
    active = "active"
    archived = "archived"
    deleted = "deleted"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    devices: Mapped[list["Device"]] = relationship(back_populates="user")


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    device_label: Mapped[str] = mapped_column(String(128))
    identity_key_public: Mapped[bytes] = mapped_column(LargeBinary)
    signed_prekey_public: Mapped[bytes] = mapped_column(LargeBinary)
    signed_prekey_signature: Mapped[bytes] = mapped_column(LargeBinary)
    pq_kyber_public: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="devices")


class OneTimePreKey(Base):
    __tablename__ = "one_time_prekeys"
    __table_args__ = (UniqueConstraint("device_id", "key_id", name="uq_prekey_device_key"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), index=True)
    key_id: Mapped[int] = mapped_column(Integer)
    prekey_public: Mapped[bytes] = mapped_column(LargeBinary)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type: Mapped[ChatType] = mapped_column(Enum(ChatType), index=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    linked_discussion_chat_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("chats.id"), nullable=True)
    is_forum: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class ChatMembership(Base):
    __tablename__ = "chat_memberships"
    __table_args__ = (UniqueConstraint("chat_id", "user_id", name="uq_chat_user"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chats.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    role: Mapped[MembershipRole] = mapped_column(Enum(MembershipRole), default=MembershipRole.member)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    can_manage_topics: Mapped[bool] = mapped_column(Boolean, default=False)


class ForumTopic(Base):
    __tablename__ = "forum_topics"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    group_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chats.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    icon_emoji: Mapped[str | None] = mapped_column(String(16), nullable=True)
    last_message_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("messages.id"), nullable=True)
    status: Mapped[TopicStatus] = mapped_column(Enum(TopicStatus), default=TopicStatus.active)
    created_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chats.id", ondelete="CASCADE"), index=True)
    sender_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    topic_id: Mapped[int | None] = mapped_column(ForeignKey("forum_topics.id", ondelete="SET NULL"), index=True, nullable=True)
    client_msg_id: Mapped[str] = mapped_column(String(72), index=True)
    sender_seq: Mapped[int] = mapped_column(BigInteger)
    chat_seq: Mapped[int] = mapped_column(BigInteger, index=True)
    ciphertext: Mapped[bytes] = mapped_column(LargeBinary)
    encryption_header: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    edited_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class MessageReaction(Base):
    __tablename__ = "message_reactions"
    __table_args__ = (UniqueConstraint("message_id", "user_id", "emoji", name="uq_reaction_once"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    message_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("messages.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    emoji: Mapped[str] = mapped_column(String(64))
    custom_emoji_file_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class OutboxQueue(Base):
    __tablename__ = "outbox_queue"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    device_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), index=True)
    chat_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chats.id", ondelete="CASCADE"), index=True)
    client_msg_id: Mapped[str] = mapped_column(String(72), index=True)
    payload: Mapped[dict] = mapped_column(JSON)
    state: Mapped[str] = mapped_column(String(24), default="pending")
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    next_retry_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class SyncState(Base):
    __tablename__ = "sync_states"
    __table_args__ = (UniqueConstraint("user_id", "device_id", "chat_id", name="uq_sync_state"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    device_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), index=True)
    chat_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chats.id", ondelete="CASCADE"), index=True)
    last_acked_chat_seq: Mapped[int] = mapped_column(BigInteger, default=0)
    local_clock: Mapped[int] = mapped_column(BigInteger, default=0)


class GroupKeyEpoch(Base):
    __tablename__ = "group_key_epochs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chats.id", ondelete="CASCADE"), index=True)
    epoch: Mapped[int] = mapped_column(Integer)
    rotated_by_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    server_signed_envelope: Mapped[bytes] = mapped_column(LargeBinary)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class GroupKeyDistribution(Base):
    __tablename__ = "group_key_distribution"
    __table_args__ = (UniqueConstraint("epoch_id", "recipient_device_id", name="uq_epoch_device"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    epoch_id: Mapped[int] = mapped_column(ForeignKey("group_key_epochs.id", ondelete="CASCADE"), index=True)
    recipient_device_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), index=True)
    encrypted_group_key: Mapped[bytes] = mapped_column(LargeBinary)


class CallSession(Base):
    __tablename__ = "call_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chats.id", ondelete="CASCADE"), index=True)
    started_by_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    call_type: Mapped[str] = mapped_column(String(16))
    status: Mapped[str] = mapped_column(String(16), default="new")
    sfu_room_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class CallParticipant(Base):
    __tablename__ = "call_participants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    call_session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("call_sessions.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    device_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), index=True)
    webrtc_offer: Mapped[Text | None] = mapped_column(Text, nullable=True)
    webrtc_answer: Mapped[Text | None] = mapped_column(Text, nullable=True)
    ice_candidates: Mapped[list | None] = mapped_column(JSON, nullable=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
