# ddlk-banda

Базовый серверный каркас безопасного мессенджера на **FastAPI + SQLAlchemy**.

## Как включить мессенджер локально

1. Установить зависимости:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Подготовить конфиг:
   ```bash
   cp .env.example .env
   ```
3. Запустить API:
   ```bash
   uvicorn ddlk_banda.main:app --reload
   ```
4. Проверить, что сервер поднялся:
   ```bash
   curl http://127.0.0.1:8000/health
   ```

> По умолчанию используется SQLite (`ddlk_banda.db`) и таблицы создаются автоматически при старте.

## Ключевые endpoints

- `POST /groups/{group_id}/topics` — создать тему форума в супергруппе с `is_forum=true`.
- `PATCH /groups/{group_id}/topics/{topic_id}` — архивировать/разархивировать тему.
- `DELETE /groups/{group_id}/topics/{topic_id}` — мягкое удаление темы (`status=deleted`).

## Примечание по E2EE

Сервер хранит только шифртекст и заголовки шифрования. Доступ к содержимому сообщений у сервера отсутствует по модели Zero-Knowledge.
