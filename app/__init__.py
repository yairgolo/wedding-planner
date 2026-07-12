from __future__ import annotations

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from config import CONFIG_MAP

from .extensions import csrf, db, limiter, login_manager, migrate, talisman


def create_app(config_name: str | None = None) -> Flask:
    load_dotenv()
    selected = config_name or os.getenv("FLASK_ENV", "development")

    app = Flask(__name__, instance_relative_config=True)
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,
        x_proto=1,
        x_host=1,
        x_port=1,
    )
    app.config.from_object(CONFIG_MAP.get(selected, CONFIG_MAP["development"]))

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "יש להתחבר כדי להמשיך."
    login_manager.login_message_category = "warning"

    if app.config.get("TALISMAN_ENABLED"):
        talisman.init_app(
            app,
            content_security_policy={
                "default-src": "'self'",
                "style-src": ["'self'", "'unsafe-inline'"],
                "script-src": ["'self'", "'unsafe-inline'"],
                "img-src": ["'self'", "data:", "blob:"],
            },
            force_https=True,
        )

    from .auth.routes import auth_bp
    from .budget.routes import budget_bp
    from .core.errors import errors_bp
    from .dashboard.routes import dashboard_bp
    from .guests.routes import guests_bp, rsvp_bp
    from .invitations.routes import invitations_bp
    from .seating.routes import seating_bp
    from .shopping.routes import shopping_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(guests_bp)
    app.register_blueprint(rsvp_bp)
    app.register_blueprint(invitations_bp)
    app.register_blueprint(seating_bp)
    app.register_blueprint(shopping_bp)
    app.register_blueprint(budget_bp)
    app.register_blueprint(errors_bp)

    from .models import (  # noqa: F401
        AuditLog,
        BudgetItem,
        Family,
        Guest,
        InvitationActivity,
        InvitationSettings,
        SeatingAssignment,
        SeatingTable,
        ShoppingItem,
        User,
        Wedding,
    )

    configure_logging(app)
    register_commands(app)
    return app


def configure_logging(app: Flask) -> None:
    if app.testing:
        return
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def register_commands(app: Flask) -> None:
    import click
    from werkzeug.security import generate_password_hash

    from .models import User, Wedding

    @app.cli.command("init-db")
    def init_db() -> None:
        """Create tables and seed the first administrator and wedding."""
        db.create_all()
        email = os.getenv("ADMIN_EMAIL", "admin@example.com").strip().lower()
        password = os.getenv("ADMIN_PASSWORD", "change-me-now")
        user = db.session.scalar(db.select(User).where(User.email == email))
        if not user:
            user = User(
                email=email,
                display_name="מנהל המערכת",
                password_hash=generate_password_hash(password),
                is_admin=True,
            )
            db.session.add(user)
        wedding = db.session.scalar(db.select(Wedding).limit(1))
        if not wedding:
            db.session.add(Wedding(partner_one="יאיר", partner_two="רבקה"))
        db.session.commit()
        click.echo(f"Database initialized. Admin: {email}")
