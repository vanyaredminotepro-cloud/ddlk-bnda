# ddlk-banda

Базовый серверный каркас безопасного мессенджера на **FastAPI + SQLAlchemy**.

## Быстрый старт (Windows CMD / PowerShell)

> Все команды ниже выполняйте **из корня репозитория** (там, где лежат `README.md` и `requirements.txt`).

### 1) Создать и активировать виртуальное окружение

**CMD:**
```bat
python -m venv .venv
.venv\Scripts\activate
```

**PowerShell:**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Установить зависимости

```bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 3) Подготовить `.env`

**CMD:**
```bat
copy .env.example .env
```

**PowerShell:**
```powershell
Copy-Item .env.example .env
```

### 4) Запустить API

```bat
python -m uvicorn ddlk_banda.main:app --reload
```

### 5) Проверить healthcheck

```bat
curl http://127.0.0.1:8000/health
```

Ожидаемый ответ:
```json
{"status":"ok","app":"ddlk-banda"}
```

---

### Альтернатива: один bat-скрипт

Можно запустить `scripts\start_windows.bat` — он создаст venv (если нет), поставит зависимости, создаст `.env` и поднимет сервер.

## Быстрый старт (Linux/macOS)

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
python -m uvicorn ddlk_banda.main:app --reload
```

---

## Почему у вас были ошибки

- `source ...` и `cp ...` — это Unix-команды, в Windows CMD они не работают.
- `uvicorn не является ... командой` — обычно `uvicorn` не в PATH. Решение: запускать `python -m uvicorn ...`.
- `No module named 'fastapi'` — зависимости не установлены в активированное окружение.
- `requirements.txt not found` — команда выполнена не из корня проекта.

---

## Ключевые endpoints

- `POST /groups/{group_id}/topics` — создать тему форума в супергруппе с `is_forum=true`.
- `PATCH /groups/{group_id}/topics/{topic_id}` — архивировать/разархивировать тему.
- `DELETE /groups/{group_id}/topics/{topic_id}` — мягкое удаление темы (`status=deleted`).
- `GET /health` — проверка состояния API.

## Примечание по E2EE

Сервер хранит только шифртекст и заголовки шифрования. Доступ к содержимому сообщений у сервера отсутствует по модели Zero-Knowledge.
