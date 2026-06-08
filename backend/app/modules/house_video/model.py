from __future__ import annotations

from typing import Literal

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.common.base_model import BaseModel

HouseVideoStatus = Literal["active", "deleted"]


class HouseVideo(BaseModel):
    __tablename__ = "house_videos"

    house_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("houses.id"),
        nullable=False,
        index=True,
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    object_key: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    duration: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[HouseVideoStatus] = mapped_column(
        String(20), nullable=False, default="active", server_default="active"
    )
