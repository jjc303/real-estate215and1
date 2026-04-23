from __future__ import annotations

import os

from app.factory import create_app


app = create_app()


if __name__ == "__main__":
    app.run(
        host=os.getenv("FLASK_RUN_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_RUN_PORT", "8000")),
        debug=bool(app.config.get("DEBUG", False)),
    )
