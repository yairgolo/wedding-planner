from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required

from app.extensions import db
from app.models import Wedding
from app.services.audit import log_action
from app.services.guest_roundtrip import import_guest_rows, read_uploaded_rows

from .forms import GuestImportForm

imports_bp = Blueprint("imports", __name__, url_prefix="/imports")


@imports_bp.route("", methods=["GET", "POST"])
@login_required
def index():
    form = GuestImportForm()
    if form.validate_on_submit():
        wedding = db.session.scalar(db.select(Wedding).order_by(Wedding.id).limit(1))
        if not wedding:
            flash("לא נמצא פרופיל חתונה.", "danger")
            return redirect(url_for("settings.wedding_profile"))

        try:
            rows = read_uploaded_rows(form.file.data)
            result = import_guest_rows(wedding.id, rows, form.duplicate_mode.data)
        except Exception as exc:  # Keep the whole import safe and report a useful error.
            db.session.rollback()
            flash(f"לא ניתן לקרוא את הקובץ: {exc}", "danger")
            return render_template("imports/index.html", form=form)

        description = (
            f"ייבוא מוזמנים: {result.created} נוספו, {result.updated} עודכנו, "
            f"{result.skipped} דולגו, {result.warning_count} אזהרות"
        )
        log_action("guest_import", None, "imported", description)

        if result.warning_count:
            flash(
                f"הייבוא הושלם: {result.created} נוספו, {result.updated} עודכנו, "
                f"{result.skipped} דולגו. נמצאו {result.warning_count} אזהרות — "
                "הרשומות התקינות יובאו בכל זאת.",
                "warning",
            )
        else:
            flash(
                f"הייבוא הושלם: {result.created} נוספו, {result.updated} עודכנו, "
                f"{result.skipped} דולגו.",
                "success",
            )

        return render_template(
            "imports/result.html",
            result=result,
            filename=form.file.data.filename,
        )
    return render_template("imports/index.html", form=form)
