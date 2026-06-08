"""自动检测逾期账单并发送催缴通知。

用法：
  python scripts/check_overdue_bills.py

可添加到 crontab 定期执行（如每天 9:00）：
  0 9 * * * cd /app && python scripts/check_overdue_bills.py >> logs/check_overdue.log 2>&1
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.factory import create_app
from app.container.services import get_bill_service


def main() -> None:
    app = create_app()

    with app.app_context():
        service = get_bill_service()
        from app.core.database import SessionLocal
        db = SessionLocal()
        try:
            count = service.check_overdue_bills(db)
            print(f"[{__import__('datetime').datetime.now()}] Overdue check completed. {count} bill(s) processed.")
        finally:
            db.close()


if __name__ == "__main__":
    main()
