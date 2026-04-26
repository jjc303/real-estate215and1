from __future__ import annotations

import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.core.database import Base
from app.modules.appointment.model import Appointment
from app.modules.contract.model import Contract
from app.modules.conversation.model import Conversation, Message
from app.modules.favorite.model import Favorite
from app.modules.house.model import House
from app.modules.user.model import User


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

database_uri = os.getenv("DATABASE_URI")
if not database_uri:
    raise RuntimeError("DATABASE_URI environment variable is required for Alembic")

config.set_main_option("sqlalchemy.url", database_uri)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
