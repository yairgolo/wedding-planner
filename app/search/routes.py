from flask import Blueprint, jsonify, render_template, request, url_for
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


@search_bp.get("/api")
@login_required
def api():
    query = request.args.get("q", "").strip()
    wedding = db.session.scalar(db.select(Wedding).order_by(Wedding.id).limit(1))
    if not query or not wedding:
        return jsonify({"results": []})
    like = f"%{query}%"
    results = []
    guests = db.session.scalars(
        db.select(Guest).where(
            Guest.wedding_id == wedding.id, Guest.deleted_at.is_(None),
            or_(Guest.first_name.ilike(like), Guest.last_name.ilike(like), Guest.phone.ilike(like))
        ).limit(5)
    ).all()
    for item in guests:
        results.append({"type": "מוזמן", "icon": "👤", "title": item.full_name,
                        "subtitle": item.phone or "ללא טלפון",
                        "url": url_for("guests.edit", guest_id=item.id)})
    vendors = db.session.scalars(
        db.select(Vendor).where(
            Vendor.wedding_id == wedding.id, Vendor.deleted_at.is_(None),
            or_(Vendor.name.ilike(like), Vendor.contact_name.ilike(like), Vendor.phone.ilike(like))
        ).limit(5)
    ).all()
    for item in vendors:
        results.append({"type": "ספק", "icon": "🤝", "title": item.name,
                        "subtitle": item.contact_name or item.phone or "ספק",
                        "url": url_for("vendors.detail", vendor_id=item.id)})
    tasks = db.session.scalars(
        db.select(Task).where(
            Task.wedding_id == wedding.id, Task.deleted_at.is_(None),
            or_(Task.title.ilike(like), Task.notes.ilike(like))
        ).limit(5)
    ).all()
    for item in tasks:
        results.append({"type": "משימה", "icon": "📋", "title": item.title,
                        "subtitle": (
                            item.due_date.strftime("%d/%m/%Y")
                            if item.due_date
                            else "ללא תאריך"
                        ),
                        "url": url_for("tasks.edit", task_id=item.id)})
    documents = db.session.scalars(
        db.select(Document).where(
            Document.wedding_id == wedding.id, Document.deleted_at.is_(None),
            or_(Document.title.ilike(like), Document.original_filename.ilike(like))
        ).limit(5)
    ).all()
    for item in documents:
        results.append({"type": "מסמך", "icon": "📂", "title": item.title,
                        "subtitle": item.original_filename,
                        "url": url_for("documents.index", q=item.title)})
    return jsonify({"results": results[:12]})
