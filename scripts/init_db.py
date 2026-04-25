#临时开发脚本
from __future__ import annotations

import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.factory import create_app
from app.core import database
import app.modules.house.model  # noqa: F401
import app.modules.user.model  # noqa: F401


def main() -> None:
    app = create_app()

    with app.app_context():
        database.Base.metadata.create_all(bind=database.engine)

    print("Database tables initialized.")


if __name__ == "__main__":
    main()
