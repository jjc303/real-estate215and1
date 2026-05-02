from __future__ import annotations

from sqlalchemy.orm import Session

from app.common.enums import NewsStatus
from app.common.pagination import build_page_result, get_offset
from app.core.exceptions import ForbiddenException, NewsNotFoundException, UnauthorizedException
from app.modules.news.model import News
from app.modules.news.repository import NewsRepository
from app.modules.news.schema import NewsCreateSchema, NewsReadSchema, NewsUpdateSchema
from app.modules.notification.service import NotificationService
from app.modules.user.model import User
from app.modules.user.repository import UserRepository


class NewsService:
    def __init__(
        self,
        news_repository: NewsRepository,
        user_repository: UserRepository,
        notification_service: NotificationService,
    ) -> None:
        self.news_repository = news_repository
        self.user_repository = user_repository
        self.notification_service = notification_service

    def create_news(self, db: Session, current_user_id: int, data: NewsCreateSchema) -> dict[str, object]:
        admin_user = self._require_admin(db, current_user_id)
        news = News(
            title=data.title,
            content=data.content,
            author_id=admin_user.id,
            status=data.status,
        )

        try:
            self.news_repository.create(db, news)
            db.flush()
            if news.status == NewsStatus.PUBLISHED:
                self._notify_published_news(
                    db,
                    news,
                    title=news.title,
                    message="A new announcement has been published.",
                )
            db.commit()
            db.refresh(news)
        except Exception:
            db.rollback()
            raise

        return self._serialize(news)

    def list_news(
        self,
        db: Session,
        current_user_id: int | None,
        page: int,
        page_size: int,
        status: str | None = None,
    ) -> dict[str, object]:
        offset = get_offset(page, page_size)
        current_user = self._get_current_user_or_none(db, current_user_id)

        if current_user is not None and current_user.role == "admin":
            items = self.news_repository.list_all(db, offset=offset, limit=page_size, status=status)
            total = self.news_repository.count_all(db, status=status)
        else:
            items = self.news_repository.list_published(db, offset=offset, limit=page_size)
            total = self.news_repository.count_published(db)

        return build_page_result(
            items=[self._serialize(news) for news in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_news_detail(
        self,
        db: Session,
        news_id: int,
        current_user_id: int | None = None,
    ) -> dict[str, object]:
        news = self.news_repository.get_by_id(db, news_id)
        if news is None:
            raise NewsNotFoundException()

        current_user = self._get_current_user_or_none(db, current_user_id)
        if news.status != NewsStatus.PUBLISHED and (current_user is None or current_user.role != "admin"):
            raise NewsNotFoundException()

        return self._serialize(news)

    def update_news(
        self,
        db: Session,
        current_user_id: int,
        news_id: int,
        data: NewsUpdateSchema,
    ) -> dict[str, object]:
        admin_user = self._require_admin(db, current_user_id)
        news = self.news_repository.get_by_id(db, news_id)
        if news is None:
            raise NewsNotFoundException()

        if data.title is not None:
            news.title = data.title
        if data.content is not None:
            news.content = data.content
        if data.status is not None:
            news.status = data.status
        news.author_id = admin_user.id

        try:
            if news.status == NewsStatus.PUBLISHED:
                self._notify_published_news(
                    db,
                    news,
                    title=news.title,
                    message="An announcement has been updated.",
                )
            db.commit()
            db.refresh(news)
        except Exception:
            db.rollback()
            raise

        return self._serialize(news)

    def delete_news(self, db: Session, current_user_id: int, news_id: int) -> None:
        self._require_admin(db, current_user_id)
        news = self.news_repository.get_by_id(db, news_id)
        if news is None:
            raise NewsNotFoundException()

        try:
            self.news_repository.delete(db, news)
            db.commit()
        except Exception:
            db.rollback()
            raise

    def _notify_published_news(self, db: Session, news: News, title: str, message: str) -> None:
        recipients = self.user_repository.list_active_by_roles(db, roles=("tenant", "landlord"))
        for recipient in recipients:
            self.notification_service.create_notification(
                db,
                user_id=recipient.id,
                source_type="news",
                source_id=news.id,
                title=title,
                message=message,
                auto_commit=False,
            )

    def _require_admin(self, db: Session, current_user_id: int) -> User:
        user = self.user_repository.get_by_id(db, current_user_id)
        if user is None:
            raise UnauthorizedException(message="unauthorized")
        if user.role != "admin":
            raise ForbiddenException()
        return user

    def _get_current_user_or_none(self, db: Session, current_user_id: int | None) -> User | None:
        if current_user_id is None:
            return None
        return self.user_repository.get_by_id(db, current_user_id)

    def _serialize(self, news: News) -> dict[str, object]:
        return NewsReadSchema.model_validate(news).model_dump(mode="json")
