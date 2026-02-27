# ddlk-banda

Базовый серверный каркас безопасного мессенджера на **FastAPI + SQLAlchemy**.

## Почему у вас «не включается приложение»

По вашему логу проблемы были из-за запуска Linux-команд в Windows CMD и отсутствия зависимостей в текущем окружении:
- `source`/`cp` не работают в CMD;
- `uvicorn` не найден, когда не активировано venv или `Scripts` не в PATH;
- `ModuleNotFoundError: fastapi` — пакет не установлен именно в активном окружении;
- `requirements.txt not found` — запуск не из корня проекта.

Ниже — рабочие команды именно для Windows.

---

## Быстрый старт (Windows CMD / PowerShell)

> Выполняйте из корня репозитория (где лежат `README.md` и `requirements.txt`).

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

### 4) Проверить окружение

```bat
python scripts\doctor.py
```

### 5) Запустить API

```bat
python -m uvicorn ddlk_banda.main:app --reload
```

### 6) Проверить healthcheck

```bat
curl http://127.0.0.1:8000/health
```

Ожидаемый ответ:
```json
{"status":"ok","app":"ddlk-banda"}
```

---

## One-click для Windows

Можно просто выполнить:

```bat
scripts\start_windows.bat
```

Скрипт создаст venv (если нет), установит зависимости, создаст `.env` и запустит сервер.

---

## Быстрый старт (Linux/macOS)

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
python scripts/doctor.py
python -m uvicorn ddlk_banda.main:app --reload
```

---

## Ключевые endpoints

- `GET /health` — проверка состояния API.
- `POST /groups/{group_id}/topics` — создать тему форума в супергруппе с `is_forum=true`.
- `PATCH /groups/{group_id}/topics/{topic_id}` — архивировать/разархивировать тему.
- `DELETE /groups/{group_id}/topics/{topic_id}` — мягкое удаление темы (`status=deleted`).

## Примечание по E2EE

Сервер хранит только шифртекст и заголовки шифрования. Доступ к содержимому сообщений у сервера отсутствует по модели Zero-Knowledge.
