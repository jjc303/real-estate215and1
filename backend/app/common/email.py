from __future__ import annotations

import smtplib
from email.message import EmailMessage

from flask import current_app

from app.core.exceptions import BadRequestException, InternalServerException


def normalize_email(email: str | None) -> str | None:
    if email is None:
        return None

    normalized = email.strip().lower()
    if normalized == "":
        return None
    return normalized


def send_verification_email(*, to_email: str, code: str, biz_type: str) -> None:
    smtp_server = current_app.config.get("SMTP_SERVER", "").strip()
    smtp_port = int(current_app.config.get("SMTP_PORT", 0))
    smtp_user = current_app.config.get("SMTP_USER", "").strip()
    smtp_pass = current_app.config.get("SMTP_PASS", "").strip()
    smtp_use_ssl = bool(current_app.config.get("SMTP_USE_SSL", False))
    smtp_use_tls = bool(current_app.config.get("SMTP_USE_TLS", False))
    expire_minutes = int(current_app.config.get("EMAIL_CODE_EXPIRE_MINUTES", 5))

    if smtp_use_ssl and smtp_use_tls:
        raise BadRequestException(message="invalid smtp config")
    if not smtp_server or smtp_port <= 0 or not smtp_user or not smtp_pass:
        raise InternalServerException(message="email service is not configured")

    subject_prefix = "Register" if biz_type == "register" else "Login"
    message = EmailMessage()
    message["Subject"] = f"{subject_prefix} verification code"
    message["From"] = smtp_user
    message["To"] = to_email
    message.set_content(
        f"Your verification code is {code}. "
        f"It will expire in {expire_minutes} minutes."
    )

    if smtp_use_ssl:
        with smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=20) as smtp:
            smtp.login(smtp_user, smtp_pass)
            smtp.send_message(message)
        return

    with smtplib.SMTP(smtp_server, smtp_port, timeout=20) as smtp:
        if smtp_use_tls:
            smtp.starttls()
        smtp.login(smtp_user, smtp_pass)
        smtp.send_message(message)
