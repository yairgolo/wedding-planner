from flask import Blueprint, render_template, request
from flask_login import login_required
from sqlalchemy import or_

from app.extensions import db
from app.models import Document, Gift, Guest, ShoppingItem, Task, Vendor, Wedding

search_bp = Blueprint("search", __name__, url_prefix="/search")


@search_bp.get("")
@login_required
def index():
    query = request.args.get("q", "").strip()
    wedding = db.session.scalar(db.select(Wedding).order_by(Wedding.id).limit(1))
    results = {
        "guests": [],
        "vendors": [],
        "tasks": [],
        "shopping": [],
        "gifts": [],
        "documents": [],
    }
    if query and wedding:
        like = f"%{query}%"
        results["guests"] = db.session.scalars(
            db.select(Guest)
            .where(
                Guest.wedding_id == wedding.id,
                Guest.deleted_at.is_(None),
                or_(
                    Guest.first_name.ilike(like),
                    Guest.last_name.ilike(like),
                    Guest.phone.ilike(like),
                    Guest.email.ilike(like),
                    Guest.group_name.ilike(like),
                ),
            )
            .limit(20)
        ).all()
        results["vendors"] = db.session.scalars(
            db.select(Vendor)
            .where(
                Vendor.wedding_id == wedding.id,
                Vendor.deleted_at.is_(None),
                or_(
                    Vendor.name.ilike(like),
                    Vendor.contact_name.ilike(like),
                    Vendor.phone.ilike(like),
                ),
            )
            .limit(20)
        ).all()
        results["tasks"] = db.session.scalars(
            db.select(Task)
            .where(
                Task.wedding_id == wedding.id,
                Task.deleted_at.is_(None),
                or_(Task.title.ilike(like), Task.notes.ilike(like)),
            )
            .limit(20)
        ).all()
        results["shopping"] = db.session.scalars(
            db.select(ShoppingItem)
            .where(
                ShoppingItem.wedding_id == wedding.id,
                ShoppingItem.deleted_at.is_(None),
                or_(ShoppingItem.name.ilike(like), ShoppingItem.store_name.ilike(like)),
            )
            .limit(20)
        ).all()
        results["gifts"] = db.session.scalars(
            db.select(Gift)
            .where(
                Gift.wedding_id == wedding.id,
                Gift.deleted_at.is_(None),
                Gift.guest_name.ilike(like),
            )
            .limit(20)
        ).all()
        results["documents"] = db.session.scalars(
            db.select(Document)
            .where(
                Document.wedding_id == wedding.id,
                Document.deleted_at.is_(None),
                or_(Document.title.ilike(like), Document.original_filename.ilike(like)),
            )
            .limit(20)
        ).all()
    return render_template("search/index.html", query=query, results=results)
