"""Isolated local UI test server; never opens the real database or sends messages."""

import tempfile
from pathlib import Path

from PIL import Image, ImageDraw
from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import InvitationPortalGuest, InvitationPortalSettings, InvitationSender, User


def main():
    app = create_app("testing")
    app.config.update(WTF_CSRF_ENABLED=True, RATELIMIT_ENABLED=False)
    folder = tempfile.TemporaryDirectory(prefix="invitation-qa-")
    app.config["UPLOAD_FOLDER"] = Path(folder.name)
    image = Image.new("RGB", (500, 700), "#f8f7f3")
    draw = ImageDraw.Draw(image)
    draw.rectangle((25, 25, 475, 675), outline="#81989d", width=3)
    draw.text((180, 270), "INVITATION", fill="#334f65")
    draw.text((180, 310), "QA PREVIEW", fill="#334f65")
    image.save(Path(folder.name) / "demo.jpg")
    with app.app_context():
        db.create_all()
        db.session.add(
            User(
                email="qa@example.com",
                display_name="QA",
                password_hash=generate_password_hash("preview-only"),
                is_admin=True,
            )
        )
        db.session.add(InvitationPortalSettings(id=1, image_filename="demo.jpg"))
        db.session.add_all(
            [
                InvitationSender(
                    name="אבא של החתן",
                    role="אבא של החתן",
                    side="groom",
                    access_token="qa-groom",
                    male_template="{name} היקר, נשמח להזמינך לחתונת בננו.",
                    female_template="{name} היקרה, נשמח להזמינך לחתונת בננו.",
                    plural_template="{name} היקרים, נשמח להזמינכם לחתונת בננו.",
                ),
                InvitationSender(
                    name="אמא של הכלה",
                    role="אמא של הכלה",
                    side="bride",
                    access_token="qa-bride",
                    male_template="{name} היקר",
                    female_template="{name} היקרה",
                    plural_template="{name} היקרים",
                ),
            ]
        )
        for name, last, side, salutation, phone, group in [
            ("משה", "לוי", "groom", "male", "0501234567", "חברים"),
            ("מרים", "כהן", "bride", "female", "0521234567", "משפחה"),
            ("יצחק והילה", "לוי", "groom", "plural", "0541234567", "משפחה"),
            ("ללא טלפון", "בדיקה", "groom", "male", "", "חברים"),
        ]:
            db.session.add(
                InvitationPortalGuest(
                    first_name=name,
                    last_name=last,
                    side=side,
                    salutation=salutation,
                    phone=phone,
                    group_name=group,
                )
            )
        db.session.commit()
    app.run(host="127.0.0.1", port=5055, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
