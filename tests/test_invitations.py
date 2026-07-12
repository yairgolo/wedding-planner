from io import BytesIO

from PIL import Image

from app.extensions import db
from app.models import Guest, InvitationActivity, InvitationSettings, Wedding


def login(client):
    return client.post(
        "/auth/login",
        data={"email": "admin@example.com", "password": "password123"},
        follow_redirects=True,
    )


def image_file():
    stream = BytesIO()
    Image.new("RGB", (80, 120), "white").save(stream, "PNG")
    stream.seek(0)
    return stream


def test_invitation_settings_and_share_data(client, app):
    login(client)
    response = client.post(
        "/invitations",
        data={
            "message_template": "שלום {name}\n{rsvp_url}",
            "image": (image_file(), "invitation.png"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "הגדרות ההזמנה נשמרו" in response.get_data(as_text=True)

    with app.app_context():
        wedding = db.session.scalar(db.select(Wedding).limit(1))
        settings = db.session.scalar(
            db.select(InvitationSettings).where(InvitationSettings.wedding_id == wedding.id)
        )
        assert settings.image_filename.endswith(".jpg")
        guest = Guest(wedding_id=wedding.id, first_name="משה", invited_count=2)
        db.session.add(guest)
        db.session.commit()
        guest_id = guest.id

    response = client.get(f"/invitations/guest/{guest_id}/share-data")
    assert response.status_code == 200
    payload = response.get_json()
    assert "שלום משה" in payload["text"]
    assert "/rsvp/" in payload["text"]
    assert payload["image_url"]


def test_mark_shared(client, app):
    login(client)
    with app.app_context():
        wedding = db.session.scalar(db.select(Wedding).limit(1))
        guest = Guest(wedding_id=wedding.id, first_name="שרה")
        db.session.add(guest)
        db.session.commit()
        guest_id = guest.id

    response = client.post(f"/invitations/guest/{guest_id}/shared", data={"type": "sent"})
    assert response.status_code == 200
    with app.app_context():
        guest = db.session.get(Guest, guest_id)
        assert guest.invitation_sent is True
        assert guest.invitation_attempts == 1
        assert db.session.scalar(db.select(InvitationActivity)) is not None
