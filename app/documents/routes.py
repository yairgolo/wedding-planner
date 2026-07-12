from __future__ import annotations

import mimetypes
import secrets
from pathlib import Path

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_login import current_user, login_required
from sqlalchemy import or_
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import AuditLog, Document, Vendor, Wedding

from .forms import DocumentForm

documents_bp = Blueprint("documents", __name__, url_prefix="/documents")
ALLOWED = {"pdf", "png", "jpg", "jpeg", "webp", "doc", "docx", "xls", "xlsx", "txt"}
CATEGORY_LABELS = {
    "contract": "חוזה",
    "receipt": "קבלה",
    "quote": "הצעת מחיר",
    "image": "תמונה",
    "invitation": "הזמנה",
    "other": "אחר",
}


def current_wedding():
    w = db.session.scalar(db.select(Wedding).order_by(Wedding.id).limit(1))
    if not w:
        abort(404)
    return w


def folder():
    path = Path(current_app.config["UPLOAD_FOLDER"]) / "documents"
    path.mkdir(parents=True, exist_ok=True)
    return path


def audit(wedding_id, document, action, text):
    db.session.add(
        AuditLog(
            wedding_id=wedding_id,
            user_id=current_user.id,
            entity_type="document",
            entity_id=str(document.id or "new"),
            action=action,
            description=text,
        )
    )


@documents_bp.get("")
@login_required
def index():
    w = current_wedding()
    q = request.args.get("q", "").strip()
    category = request.args.get("category", "")
    stmt = db.select(Document).where(Document.wedding_id == w.id, Document.deleted_at.is_(None))
    if q:
        stmt = stmt.where(
            or_(
                Document.title.ilike(f"%{q}%"),
                Document.original_filename.ilike(f"%{q}%"),
                Document.notes.ilike(f"%{q}%"),
            )
        )
    if category:
        stmt = stmt.where(Document.category == category)
    docs = db.session.scalars(stmt.order_by(Document.created_at.desc())).all()
    vendors = {
        v.id: v.name
        for v in db.session.scalars(db.select(Vendor).where(Vendor.wedding_id == w.id)).all()
    }
    stats = {
        "total": len(
            db.session.scalars(
                db.select(Document).where(
                    Document.wedding_id == w.id, Document.deleted_at.is_(None)
                )
            ).all()
        ),
        "contracts": sum(1 for d in docs if d.category == "contract"),
        "receipts": sum(1 for d in docs if d.category == "receipt"),
    }
    return render_template(
        "documents/index.html",
        documents=docs,
        vendors=vendors,
        category_labels=CATEGORY_LABELS,
        stats=stats,
        q=q,
    )


@documents_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    w = current_wedding()
    form = DocumentForm()
    form.vendor_id.choices = [(0, "ללא ספק")] + [
        (v.id, v.name)
        for v in db.session.scalars(
            db.select(Vendor)
            .where(Vendor.wedding_id == w.id, Vendor.deleted_at.is_(None))
            .order_by(Vendor.name)
        ).all()
    ]
    if form.validate_on_submit():
        upload = form.file.data
        original = secure_filename(upload.filename or "")
        ext = Path(original).suffix.lower().lstrip(".")
        if ext not in ALLOWED:
            flash("סוג הקובץ אינו מורשה.", "danger")
            return render_template("documents/form.html", form=form, title="העלאת מסמך")
        stored = f"{secrets.token_hex(16)}.{ext}"
        target = folder() / stored
        upload.save(target)
        mime = upload.mimetype or mimetypes.guess_type(original)[0] or "application/octet-stream"
        doc = Document(
            wedding_id=w.id,
            title=form.title.data.strip(),
            category=form.category.data,
            original_filename=original,
            stored_filename=stored,
            mime_type=mime,
            size_bytes=target.stat().st_size,
            vendor_id=form.vendor_id.data or None,
            notes=(form.notes.data or "").strip() or None,
        )
        db.session.add(doc)
        db.session.flush()
        audit(w.id, doc, "create", f"הועלה המסמך {doc.title}")
        db.session.commit()
        flash("המסמך הועלה.", "success")
        return redirect(url_for("documents.index"))
    return render_template("documents/form.html", form=form, title="העלאת מסמך")


@documents_bp.get("/<int:document_id>/download")
@login_required
def download(document_id):
    w = current_wedding()
    doc = db.get_or_404(Document, document_id)
    if doc.wedding_id != w.id or doc.is_deleted:
        abort(404)
    return send_from_directory(
        folder(), doc.stored_filename, as_attachment=True, download_name=doc.original_filename
    )


@documents_bp.post("/<int:document_id>/delete")
@login_required
def delete(document_id):
    w = current_wedding()
    doc = db.get_or_404(Document, document_id)
    if doc.wedding_id != w.id:
        abort(404)
    doc.soft_delete()
    audit(w.id, doc, "delete", f"המסמך {doc.title} הועבר לסל המחזור")
    db.session.commit()
    flash("המסמך הועבר לסל המחזור.", "success")
    return redirect(url_for("documents.index"))
