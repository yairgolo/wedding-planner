from __future__ import annotations

import os
import platform
import sys
from pathlib import Path

from flask import Blueprint, current_app, render_template
from flask_login import current_user, login_required
from sqlalchemy import text

from app.extensions import db

system_bp = Blueprint("system", __name__, url_prefix="/admin/system")


@system_bp.get("")
@login_required
def index():
    if not current_user.is_admin:
        return render_template("errors/error.html", code=403, message="אין הרשאה לצפות בעמוד."), 403

    database_ok = True
    database_error = ""
    try:
        db.session.execute(text("SELECT 1"))
    except Exception as exc:  # pragma: no cover - defensive diagnostics
        database_ok = False
        database_error = str(exc)

    upload_path = Path(current_app.config["UPLOAD_FOLDER"])
    upload_path.mkdir(parents=True, exist_ok=True)
    uploads_writable = os.access(upload_path, os.W_OK)

    instance_path = Path(current_app.instance_path)
    instance_writable = os.access(instance_path, os.W_OK)

    checks = [
        ("מסד נתונים", database_ok, database_error or "החיבור פעיל"),
        ("תיקיית העלאות", uploads_writable, str(upload_path)),
        ("תיקיית instance", instance_writable, str(instance_path)),
        ("Python", sys.version_info >= (3, 10), platform.python_version()),
        (
            "מצב ייצור",
            not current_app.debug,
            "Production" if not current_app.debug else "Development",
        ),
        (
            "HTTPS מוכנות",
            current_app.config.get("SESSION_COOKIE_SECURE", False),
            "Cookie מאובטח"
            if current_app.config.get("SESSION_COOKIE_SECURE", False)
            else "כבוי בפיתוח",
        ),
    ]
    return render_template(
        "system/index.html",
        checks=checks,
        python_version=platform.python_version(),
        platform_name=platform.platform(),
        database_uri=current_app.config["SQLALCHEMY_DATABASE_URI"].split("@")[-1],
    )
