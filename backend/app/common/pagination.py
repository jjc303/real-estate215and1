from __future__ import annotations


def get_offset(page: int, page_size: int) -> int:
    return (page - 1) * page_size


def build_page_result(items: list, total: int, page: int, page_size: int) -> dict[str, object]:
    return {
        "list": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
