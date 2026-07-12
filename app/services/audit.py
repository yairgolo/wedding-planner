from flask_login import current_user

from app.extensions import db
from app.models import AuditLog, Wedding


def log_action(entity_type: str, entity_id: int | None, action: str, description: str) -> None:
    wedding = db.session.scalar(db.select(Wedding).order_by(Wedding.id).limit(1))
    if not wedding:
        return
    user_id = current_user.id if getattr(current_user, "is_authenticated", False) else None
    db.session.add(
        AuditLog(
            wedding_id=wedding.id,
            user_id=user_id,
            entity_type=entity_type,
            entity_id=str(entity_id or "system"),
            action=action,
            description=description,
        )
    )
    db.session.commit()
