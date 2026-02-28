# ddlk-banda: secure messenger architecture (FastAPI + SQLAlchemy)

## 1) Zero-Knowledge model
- Server stores only ciphertext (`messages.ciphertext`) and transport metadata (`encryption_header`).
- End-to-end keys are device-bound (`devices.identity_key_public`, `signed_prekey_public`, `one_time_prekeys`).
- Optional post-quantum handshake key is supported (`devices.pq_kyber_public`).
- Group/supergroup E2EE is handled through epoch rotation:
  - `group_key_epochs` stores only server-signed envelopes.
  - `group_key_distribution` stores per-device encrypted group keys.
  - server can verify signatures and deliver blobs but cannot decrypt keys.

## 2) Chat structure
- `chats.type=direct`: one-to-one E2EE.
- `chats.type=group`: classic group up to 200 members (enforce limit in service layer).
- `chats.type=supergroup`: scalable, admin rights, history for new members.
- `chats.type=channel`: one-to-many broadcast.
- `chats.linked_discussion_chat_id`: channel comments in linked supergroup.

## 3) Forums and topics (Telegram-like)
- Forum = supergroup with `chats.is_forum=true`.
- `forum_topics`: `id`, `group_id`, `title`, `icon_emoji`, `last_message_id`, lifecycle `status`.
- Any message in forum mode MUST include `topic_id`.
- Feed isolation rule: timeline query is filtered by both `chat_id` and `topic_id`.

## 4) Reactions
- `message_reactions` supports standard emoji and custom emoji reference (`custom_emoji_file_id`).
- Unique constraint prevents duplicate same-reaction spam by one user.

## 5) Calls (WebRTC coordinator-only server)
- `call_sessions`: room lifecycle and call metadata.
- `call_participants`: SDP offer/answer and ICE candidates relay.
- Media stays peer-to-peer or encrypted SFU path; server coordinates TURN/STUN only.

## 6) Ideal connectivity (optimistic UI + offline queue)
- Client immediately pushes draft to local outbox and UI.
- `outbox_queue` stores pending encrypted payloads for retry.
- `messages.chat_seq` is monotonic chat sequence from server.
- `sync_states.last_acked_chat_seq` tracks per-device checkpoint.
- Recovery:
  1. Client reconnects and sends last acked seq.
  2. Server returns `(last_acked_seq, +delta)` using `chat_seq > ack`.
  3. Client resolves optimistic local items by `client_msg_id`.

## 7) Stage-2 prompt (security core)
```text
Отлично. Теперь реализуй модуль безопасности для мессенджера "ddlk-banda". Напиши код на Python, реализующий протокол на основе двойного Ratcheting (как в Signal/Double Ratchet).

Сгенерируй функции для создания ключей X25519 и Kyber (для пост-квантовой защиты, опционально).

Напиши логику создания сессии: при старте личного чата клиенты обмениваются долговременными ключами через сервер (сервер видит только публичные ключи, подписанные идентификатором).

Реализуй сброс сессии, если что-то пошло не так.

Для супер-групп: продумай схему "сетки ключей" (как в Telegram Secret Chats для групп не предусмотрено, но мы хотим своё). Предложи вариант с единым ключом группы, который обновляется при выходе участника и рассылается подписанным сервером сообщением (но зашифрованным для каждого участника индивидуально, чтобы сервер не знал ключ группы).
```

## 8) Stage-3 prompt (forums/topics)
```text
Теперь сфокусируйся на самой продвинутой фиче — "Форумы".

В таблице супергрупп добавь флаг is_forum = True.

Создай таблицу forum_topics, где будут поля: id, group_id, title, icon_emoji, last_message_id.

Напиши SQLAlchemy модели и Pydantic схемы для создания темы, удаления темы и архивации.

Напиши эндпоинт FastAPI: POST /groups/{group_id}/topics, который создает новую тему.

Объясни, как должно выглядеть тело сообщения, отправленного в тему: обычное сообщение, но с обязательным полем topic_id. Сообщения из разных тем не должны пересекаться в ленте чата.
```

## 9) Topic message body contract
```json
{
  "chat_id": "<uuid>",
  "topic_id": 481,
  "client_msg_id": "dev123-000045",
  "ciphertext": "<base64>",
  "encryption_header": {
    "scheme": "double-ratchet",
    "sender_device_id": "<uuid>",
    "session_id": "<opaque>",
    "message_index": 45
  }
}
```
