from app.extensions import db
from app.models import Document, Family, Guest, Task, Vendor, Wedding


def login(client):
    return client.post(
        "/auth/login",
        data={"email": "admin@example.com", "password": "password123"},
        follow_redirects=True,
    )


def test_search_api_returns_entities(client, app):
    login(client)
    with app.app_context():
        wedding = db.session.scalar(db.select(Wedding).limit(1))
        db.session.add(
            Guest(wedding_id=wedding.id, first_name="דוד", last_name="כהן")
        )
        db.session.commit()
    response = client.get("/search/api?q=כהן")
    assert response.status_code == 200
    assert any(
        item["type"] == "מוזמן" for item in response.get_json()["results"]
    )


def test_family_view(client, app):
    login(client)
    with app.app_context():
        wedding = db.session.scalar(db.select(Wedding).limit(1))
        family = Family(wedding_id=wedding.id, name="משפחת לוי")
        db.session.add(family)
        db.session.flush()
        db.session.add(
            Guest(
                wedding_id=wedding.id,
                family_id=family.id,
                first_name="משה",
                invited_count=2,
            )
        )
        db.session.commit()
    response = client.get("/guests?view=family")
    assert response.status_code == 200
    assert "משפחת לוי" in response.get_data(as_text=True)


def test_vendor_relations_page(client, app):
    login(client)
    with app.app_context():
        wedding = db.session.scalar(db.select(Wedding).limit(1))
        vendor = Vendor(wedding_id=wedding.id, name="DJ בדיקה", status="booked")
        db.session.add(vendor)
        db.session.flush()
        db.session.add(
            Task(
                wedding_id=wedding.id,
                title="לתאם מוזיקה",
                related_vendor_id=vendor.id,
            )
        )
        db.session.add(
            Document(
                wedding_id=wedding.id,
                title="חוזה",
                original_filename="contract.pdf",
                stored_filename="test-contract.pdf",
                mime_type="application/pdf",
                vendor_id=vendor.id,
            )
        )
        db.session.commit()
        vendor_id = vendor.id
    response = client.get(f"/vendors/{vendor_id}")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "לתאם מוזיקה" in body
    assert "חוזה" in body
