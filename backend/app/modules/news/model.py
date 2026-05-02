from __future__ import annotations

from typing import Literal

from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.common.base_model import BaseModel
from app.common.enums import NewsStatus as NewsStatusValues


NewsStatus = Literal[
    NewsStatusValues.DRAFT,
    NewsStatusValues.PUBLISHED,
]


class News(BaseModel):
    __tablename__ = "news"
    __table_args__ = (
        Index("ix_news_created_at", "created_at"),
    )

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    status: Mapped[NewsStatus] = mapped_column(
        String(20),
        nullable=False,
        server_default=NewsStatusValues.DRAFT,
        index=True,
    )
