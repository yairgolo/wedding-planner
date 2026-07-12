from flask import Blueprint, render_template
from flask_login import login_required

from app.extensions import db
from app.models import Wedding

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    wedding = db.session.scalar(db.select(Wedding).order_by(Wedding.id).limit(1))
    metrics = {
        "guests": 0,
        "confirmed": 0,
        "pending": 0,
        "tasks": 0,
        "unseated": 0,
        "purchases": 0,
    }
    return render_template("dashboard/index.html", wedding=wedding, metrics=metrics)


@dashboard_bp.get("/health")
def health():
    return {"status": "ok"}, 200
