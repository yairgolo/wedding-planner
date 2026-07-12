from app.extensions import db
from app.models import BudgetItem, ShoppingItem


def login(client):
    return client.post(
        "/auth/login",
        data={"email": "admin@example.com", "password": "password123"},
        follow_redirects=True,
    )


def test_shopping_crud_and_toggle(client, app):
    login(client)
    response = client.post(
        "/shopping/new",
        data={
            "name": "קומקום",
            "category": "home",
            "status": "planned",
            "priority": "medium",
            "quantity": 1,
            "estimated_price": "150",
            "actual_price": "0",
            "store_name": "חנות",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "קומקום" in response.get_data(as_text=True)
    with app.app_context():
        item = db.session.scalar(db.select(ShoppingItem).where(ShoppingItem.name == "קומקום"))
        item_id = item.id
    response = client.post(f"/shopping/{item_id}/toggle", follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        item = db.session.get(ShoppingItem, item_id)
        assert item.status == "purchased"
        assert float(item.actual_price) == 150


def test_budget_create_and_mark_paid(client, app):
    login(client)
    response = client.post(
        "/budget/new",
        data={
            "name": "DJ",
            "category": "music",
            "supplier_name": "ישראל",
            "planned_amount": "7000",
            "actual_amount": "6800",
            "paid_amount": "1000",
            "status": "agreed",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "DJ" in response.get_data(as_text=True)
    with app.app_context():
        item = db.session.scalar(db.select(BudgetItem).where(BudgetItem.name == "DJ"))
        item_id = item.id
        assert item.status == "partial"
    client.post(f"/budget/{item_id}/paid", follow_redirects=True)
    with app.app_context():
        item = db.session.get(BudgetItem, item_id)
        assert item.status == "paid"
        assert item.balance == 0


def test_exports_require_login(client):
    assert client.get("/shopping/export.xlsx").status_code == 302
    assert client.get("/budget/export.xlsx").status_code == 302
