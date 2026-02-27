"""Simple startup diagnostics for ddlk-banda."""

from __future__ import annotations

import importlib
import pathlib
import platform
import sys

REQUIRED_IMPORTS = ["fastapi", "uvicorn", "sqlalchemy", "pydantic", "pydantic_settings"]


def main() -> int:
    root = pathlib.Path(__file__).resolve().parents[1]
    print(f"[ddlk-banda doctor] python={sys.version.split()[0]} os={platform.system()}")
    print(f"[ddlk-banda doctor] cwd={pathlib.Path.cwd()}")

    req = root / "requirements.txt"
    if not req.exists():
        print("[ERROR] requirements.txt not found. Run commands from repository root.")
        return 1

    missing: list[str] = []
    for module in REQUIRED_IMPORTS:
        try:
            importlib.import_module(module)
        except Exception:
            missing.append(module)

    if missing:
        print(f"[ERROR] Missing packages: {', '.join(missing)}")
        print("Install them with: python -m pip install -r requirements.txt")
        return 1

    print("[OK] Base dependencies are importable.")
    print("Run server with: python -m uvicorn ddlk_banda.main:app --reload")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
