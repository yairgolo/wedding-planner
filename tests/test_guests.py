from app.extensions import db
from app.models import Guest


def login(client):
    return client.post(
        "/auth/login",
        data={"email": "admin@example.com", "password": "password123"},
        follow_redirects=True,
    )


def test_guest_crud(client, app):
    login(client)
    response = client.post(
        "/guests/new",
        data={
            "first_name": "משה",
            "last_name": "כהן",
            "phone": "0501234567",
            "side": "groom",
            "family_id": 0,
            "invited_count": 2,
            "confirmed_count": 0,
            "rsvp_status": "pending",
            "diet": "regular",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "משה כהן" in response.get_data(as_text=True)
    with app.app_context():
        guest = db.session.scalar(db.select(Guest).where(Guest.first_name == "משה"))
        assert guest is not None
        token = guest.rsvp_token
    response = client.get(f"/rsvp/{token}")
    assert response.status_code == 200
    assert "שלום משה" in response.get_data(as_text=True)


def test_rsvp_update(client, app):
    with app.app_context():
        from app.models import Wedding

        wedding = db.session.scalar(db.select(Wedding).limit(1))
        guest = Guest(wedding_id=wedding.id, first_name="שרה", invited_count=3)
        db.session.add(guest)
        db.session.commit()
        token = guest.rsvp_token
    response = client.post(
        f"/rsvp/{token}",
        data={
            "status": "confirmed",
            "confirmed_count": 2,
            "diet_notes": "ללא גלוטן",
            "message": "מזל טוב",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "תודה" in response.get_data(as_text=True)
    with app.app_context():
        guest = db.session.scalar(db.select(Guest).where(Guest.rsvp_token == token))
        assert guest.confirmed_count == 2
        assert guest.rsvp_status == "confirmed"
