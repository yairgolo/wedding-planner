from app.extensions import db
from app.models import Guest, SeatingAssignment, SeatingTable, Wedding


def login(client):
    return client.post(
        "/auth/login",
        data={"email": "admin@example.com", "password": "password123"},
        follow_redirects=True,
    )


def test_seating_page_requires_login(client):
    response = client.get("/seating")
    assert response.status_code == 302


def test_create_table_and_assign_guest(app, client):
    login(client)
    response = client.post(
        "/seating/tables/new",
        data={"number": "1", "name": "משפחה", "capacity": 10, "shape": "round", "zone": "מרכז"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert response.request.path == "/seating"

    with app.app_context():
        wedding = db.session.scalar(db.select(Wedding).limit(1))
        guest = Guest(
            wedding_id=wedding.id,
            first_name="ישראל",
            last_name="ישראלי",
            invited_count=2,
            confirmed_count=2,
            rsvp_status="confirmed",
        )
        db.session.add(guest)
        db.session.commit()
        guest_id = guest.id
        table = db.session.scalar(db.select(SeatingTable).where(SeatingTable.number == "1"))
        table_id = table.id

    response = client.post("/seating/assign", json={"guest_id": guest_id, "table_id": table_id})
    assert response.status_code == 200
    assert response.get_json()["ok"] is True

    with app.app_context():
        assignment = db.session.scalar(
            db.select(SeatingAssignment).where(SeatingAssignment.guest_id == guest_id)
        )
        assert assignment is not None
        assert assignment.seat_count == 2


def test_capacity_guard(app, client):
    login(client)
    with app.app_context():
        wedding = db.session.scalar(db.select(Wedding).limit(1))
        table = SeatingTable(wedding_id=wedding.id, number="99", capacity=1)
        guest = Guest(
            wedding_id=wedding.id,
            first_name="משפחה",
            invited_count=3,
            confirmed_count=3,
            rsvp_status="confirmed",
        )
        db.session.add_all([table, guest])
        db.session.commit()
        table_id, guest_id = table.id, guest.id
    response = client.post("/seating/assign", json={"guest_id": guest_id, "table_id": table_id})
    assert response.status_code == 409
    assert response.get_json()["ok"] is False
