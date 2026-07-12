from datetime import date, time

from app.extensions import db
from app.models import Guest, SeatingAssignment, SeatingTable, Task, Vendor, Wedding


def login(client):
    return client.post(
        "/auth/login",
        data={"email": "admin@example.com", "password": "password123"},
        follow_redirects=True,
    )


def test_event_day_page_and_guest_table_search(client, app):
    login(client)
    with app.app_context():
        wedding = db.session.scalar(db.select(Wedding).limit(1))
        wedding.event_date = date.today()
        wedding.ceremony_time = time(19, 30)
        guest = Guest(wedding_id=wedding.id, first_name="דוד", last_name="לוי")
        table = SeatingTable(wedding_id=wedding.id, number="12", capacity=10)
        db.session.add_all([guest, table])
        db.session.flush()
        db.session.add(
            SeatingAssignment(
                wedding_id=wedding.id,
                guest_id=guest.id,
                table_id=table.id,
                seat_count=1,
            )
        )
        db.session.commit()
    response = client.get("/event-day?q=דוד")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "דוד לוי" in body
    assert "12" in body


def test_event_day_shows_vendor_and_tasks(client, app):
    login(client)
    with app.app_context():
        wedding = db.session.scalar(db.select(Wedding).limit(1))
        db.session.add(
            Vendor(
                wedding_id=wedding.id,
                name="DJ בדיקה",
                status="booked",
                arrival_time=time(17, 0),
                phone="0500000000",
            )
        )
        db.session.add(
            Task(
                wedding_id=wedding.id,
                title="לא לשכוח טבעות",
                category="wedding",
            )
        )
        db.session.commit()
    response = client.get("/event-day")
    body = response.get_data(as_text=True)
    assert "DJ בדיקה" in body
    assert "לא לשכוח טבעות" in body


def test_admin_system_health(client):
    login(client)
    response = client.get("/admin/system")
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "מצב המערכת" in body
    assert "מסד נתונים" in body


def test_manifest_available(client):
    response = client.get("/static/manifest.webmanifest")
    assert response.status_code == 200
    assert "Wedding Planner" in response.get_data(as_text=True)
