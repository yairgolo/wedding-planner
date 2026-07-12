from __future__ import annotations

from urllib.parse import urljoin, urlparse

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import db, limiter
from app.models import User

from .forms import LoginForm

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def is_safe_url(target: str) -> bool:
    host = urlparse(request.host_url)
    redirect_url = urlparse(urljoin(request.host_url, target))
    return redirect_url.scheme in {"http", "https"} and host.netloc == redirect_url.netloc


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = db.session.scalar(db.select(User).where(User.email == email))
        if user and user.verify_password(form.password.data) and user.is_active:
            login_user(user, remember=form.remember.data)
            next_url = request.args.get("next")
            flash("ברוכים הבאים למערכת.", "success")
            if next_url and is_safe_url(next_url):
                return redirect(next_url)
            return redirect(url_for("dashboard.index"))
        flash("האימייל או הסיסמה אינם נכונים.", "danger")
    return render_template("auth/login.html", form=form)


@auth_bp.post("/logout")
@login_required
def logout():
    logout_user()
    flash("התנתקת בהצלחה.", "success")
    return redirect(url_for("auth.login"))
