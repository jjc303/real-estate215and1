from __future__ import annotations

from pathlib import Path
import secrets

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app.core.exceptions import BadRequestException


def save_image_file(
    file: FileStorage,
    *,
    upload_root: str,
    relative_dir: str,
    url_prefix: str,
    max_bytes: int,
    allowed_extensions: set[str],
) -> tuple[str, str, int]:
    filename = secure_filename(file.filename or "")
    if not filename or "." not in filename:
        raise BadRequestException(message="invalid image file")

    extension = filename.rsplit(".", 1)[1].lower()
    if extension not in allowed_extensions:
        raise BadRequestException(message="unsupported image type")

    file.stream.seek(0, 2)
    size_bytes = file.stream.tell()
    file.stream.seek(0)
    if size_bytes <= 0:
        raise BadRequestException(message="empty image file")
    if size_bytes > max_bytes:
        raise BadRequestException(message="image file too large")

    object_name = f"{secrets.token_hex(16)}.{extension}"
    object_key = f"{relative_dir.strip('/')}/{object_name}"
    full_path = Path(upload_root) / object_key
    full_path.parent.mkdir(parents=True, exist_ok=True)
    file.save(full_path)

    url = f"{url_prefix.rstrip('/')}/{object_key}"
    return url, object_key, size_bytes
