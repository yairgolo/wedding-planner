from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import (
    AuditLog,
    BudgetItem,
    Document,
    Gift,
    Guest,
    ShoppingItem,
    Task,
    Vendor,
    Wedding,
)

activity_bp = Blueprint("activity", __name__, url_prefix="/activity")
trash_bp = Blueprint("trash", __name__, url_prefix="/trash")


def current_wedding():
    w = db.session.scalar(db.select(Wedding).order_by(Wedding.id).limit(1))
    if not w:
        abort(404)
    return w


@activity_bp.get("")
@login_required
def index():
    w = current_wedding()
    entity = request.args.get("entity", "")
    stmt = db.select(AuditLog).where(AuditLog.wedding_id == w.id)
    if entity:
        stmt = stmt.where(AuditLog.entity_type == entity)
    logs = db.session.scalars(stmt.order_by(AuditLog.created_at.desc()).limit(250)).all()
    return render_template("activity/index.html", logs=logs, entity=entity)


MODEL_MAP = {
    "guest": Guest,
    "vendor": Vendor,
    "task": Task,
    "shopping": ShoppingItem,
    "budget": BudgetItem,
    "gift": Gift,
    "document": Document,
}


@trash_bp.get("", endpoint="index")
@login_required
def trash_index():
    w = current_wedding()
    groups = {}
    for name, model in MODEL_MAP.items():
        if hasattr(model, "deleted_at"):
            groups[name] = db.session.scalars(
                db.select(model)
                .where(model.wedding_id == w.id, model.deleted_at.is_not(None))
                .order_by(model.deleted_at.desc())
            ).all()
    return render_template("trash/index.html", groups=groups)


@trash_bp.post("/<entity>/<int:item_id>/restore")
@login_required
def restore(entity, item_id):
    w = current_wedding()
    model = MODEL_MAP.get(entity)
    if not model:
        abort(404)
    item = db.get_or_404(model, item_id)
    if item.wedding_id != w.id:
        abort(404)
    item.deleted_at = None
    label = (
        getattr(item, "name", None)
        or getattr(item, "title", None)
        or getattr(item, "full_name", None)
        or getattr(item, "guest_name", None)
        or f"#{item.id}"
    )
    db.session.add(
        AuditLog(
            wedding_id=w.id,
            user_id=current_user.id,
            entity_type=entity,
            entity_id=str(item.id),
            action="restore",
            description=f"שוחזר {label} מסל המחזור",
        )
    )
    db.session.commit()
    flash("הפריט שוחזר.", "success")
    return redirect(url_for("trash.index"))
