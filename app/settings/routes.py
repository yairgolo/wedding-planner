from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required

from app.extensions import db
from app.models import Wedding
from app.services.audit import log_action

from .forms import WeddingProfileForm

settings_bp = Blueprint("settings", __name__, url_prefix="/settings")


def current_wedding() -> Wedding | None:
    return db.session.scalar(db.select(Wedding).order_by(Wedding.id).limit(1))


@settings_bp.route("/wedding", methods=["GET", "POST"])
@login_required
def wedding_profile():
    wedding = current_wedding()
    if not wedding:
        wedding = Wedding(partner_one="יאיר", partner_two="רבקה")
        db.session.add(wedding)
        db.session.flush()
    form = WeddingProfileForm(obj=wedding)
    if form.validate_on_submit():
        form.populate_obj(wedding)
        db.session.commit()
        log_action("wedding", wedding.id, "updated", "פרופיל החתונה עודכן")
        flash("פרופיל החתונה נשמר בהצלחה.", "success")
        return redirect(url_for("settings.wedding_profile"))
    return render_template("settings/wedding_profile.html", form=form, wedding=wedding)
