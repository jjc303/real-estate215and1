from __future__ import annotations

from flask import g
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker


Base = declarative_base()
engine: Engine | None = None
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False)
)


def build_engine(database_uri: str, db_echo: bool) -> Engine:
    engine_options = {
        "echo": db_echo,
        "pool_pre_ping": database_uri.startswith("mysql"),
    }
    return create_engine(database_uri, **engine_options)


def init_database(flask_app) -> None:
    global engine

    engine = build_engine(
        database_uri=flask_app.config["DATABASE_URI"],
        db_echo=flask_app.config.get("DB_ECHO", False),
    )

    SessionLocal.remove()
    SessionLocal.configure(bind=engine)

    register_db_hooks(flask_app)


def register_db_hooks(flask_app) -> None:
    if flask_app.extensions.get("db_hooks_registered"):
        return

    @flask_app.before_request
    def open_db():
        g.db = SessionLocal()

    @flask_app.teardown_request
    def close_db(_exception):
        try:
            db = getattr(g, "db", None)
            if db is not None:
                db.close()
        finally:
            SessionLocal.remove()

    flask_app.extensions["db_hooks_registered"] = True
