from __future__ import annotations

from flask import Blueprint, g

from app.common.dependencies import get_required_current_user_id
from app.container.services import get_statistics_service
from app.core.response import success


bp = Blueprint("statistics", __name__)


@bp.get("/house-utilization")
def get_house_utilization():
    current_user_id = get_required_current_user_id()
    service = get_statistics_service()
    result = service.get_house_utilization(g.db, current_user_id=current_user_id)
    return success(data=result)


@bp.get("/rent-income")
def get_rent_income():
    current_user_id = get_required_current_user_id()
    service = get_statistics_service()
    result = service.get_rent_income(g.db, current_user_id=current_user_id)
    return success(data=result)


@bp.get("/active-users")
def get_active_users():
    current_user_id = get_required_current_user_id()
    service = get_statistics_service()
    result = service.get_active_users(g.db, current_user_id=current_user_id)
    return success(data=result)


@bp.get("/complaint-repair-count")
def get_complaint_repair_count():
    current_user_id = get_required_current_user_id()
    service = get_statistics_service()
    result = service.get_complaint_repair_count(g.db, current_user_id=current_user_id)
    return success(data=result)
