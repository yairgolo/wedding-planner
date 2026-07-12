from app.extensions import db
from app.models import Task, Vendor


def login(client):
    return client.post(
        "/auth/login",
        data={"email": "admin@example.com", "password": "password123"},
        follow_redirects=True,
    )


def test_vendor_crud_and_mark_paid(client, app):
    login(client)
    response = client.post(
        "/vendors/new",
        data={
            "name": "ישראל צילום",
            "category": "photography",
            "status": "booked",
            "contact_name": "ישראל",
            "phone": "0501234567",
            "agreed_amount": "9000",
            "paid_amount": "2000",
            "rating": "5",
            "contract_signed": "y",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "ישראל צילום" in response.get_data(as_text=True)
    with app.app_context():
        vendor = db.session.scalar(db.select(Vendor).where(Vendor.name == "ישראל צילום"))
        vendor_id = vendor.id
        assert float(vendor.balance) == 7000
    client.post(f"/vendors/{vendor_id}/mark-paid", follow_redirects=True)
    with app.app_context():
        vendor = db.session.get(Vendor, vendor_id)
        assert vendor.is_paid
        assert float(vendor.balance) == 0


def test_task_crud_and_status(client, app):
    login(client)
    response = client.post(
        "/tasks/new",
        data={
            "title": "לסגור תפריט",
            "category": "wedding",
            "status": "todo",
            "priority": "urgent",
            "assigned_to": "יאיר",
            "related_vendor_id": "0",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "לסגור תפריט" in response.get_data(as_text=True)
    with app.app_context():
        task = db.session.scalar(db.select(Task).where(Task.title == "לסגור תפריט"))
        task_id = task.id
    client.post(f"/tasks/{task_id}/status/done", follow_redirects=True)
    with app.app_context():
        task = db.session.get(Task, task_id)
        assert task.status == "done"
        assert task.completed_at is not None


def test_vendor_and_task_exports_require_login(client):
    assert client.get("/vendors/export.xlsx").status_code == 302
    assert client.get("/tasks/export.xlsx").status_code == 302
