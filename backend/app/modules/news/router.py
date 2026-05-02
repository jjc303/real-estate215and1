from __future__ import annotations

from flask import Blueprint, g, request

from app.common.dependencies import get_optional_current_user_id, get_required_current_user_id
from app.container.services import get_news_service
from app.core.response import success
from app.modules.news.schema import NewsCreateSchema, NewsListQuerySchema, NewsUpdateSchema


bp = Blueprint("news", __name__)


@bp.post("")
def create_news():
    current_user_id = get_required_current_user_id()
    data = NewsCreateSchema(**(request.get_json() or {}))
    service = get_news_service()
    result = service.create_news(g.db, current_user_id=current_user_id, data=data)
    return success(data=result, status_code=201)


@bp.get("")
def list_news():
    current_user_id = get_optional_current_user_id()
    query = NewsListQuerySchema(**request.args.to_dict())
    service = get_news_service()
    result = service.list_news(
        g.db,
        current_user_id=current_user_id,
        page=query.page,
        page_size=query.page_size,
        status=query.status,
    )
    return success(data=result)


@bp.get("/<int:news_id>")
def get_news_detail(news_id: int):
    current_user_id = get_optional_current_user_id()
    service = get_news_service()
    result = service.get_news_detail(g.db, news_id=news_id, current_user_id=current_user_id)
    return success(data=result)


@bp.patch("/<int:news_id>")
def update_news(news_id: int):
    current_user_id = get_required_current_user_id()
    data = NewsUpdateSchema(**(request.get_json() or {}))
    service = get_news_service()
    result = service.update_news(g.db, current_user_id=current_user_id, news_id=news_id, data=data)
    return success(data=result)


@bp.delete("/<int:news_id>")
def delete_news(news_id: int):
    current_user_id = get_required_current_user_id()
    service = get_news_service()
    service.delete_news(g.db, current_user_id=current_user_id, news_id=news_id)
    return success(data=None)
