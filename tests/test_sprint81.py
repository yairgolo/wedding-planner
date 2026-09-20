from app.models import AuditLog, Wedding


def login(client):
    return client.post(
        "/auth/login",
        data={"email": "admin@example.com", "password": "password123"},
        follow_redirects=True,
    )


def test_dashboard_polish_renders_for_authenticated_user(client):
    login(client)
    response = client.get("/")
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "העדיפות עכשיו" in body
    assert "מה כדאי לעשות עכשיו" in body
    assert "משימות קרובות" in body
    assert "הוספה מהירה" in body


def test_recent_activity_is_visible_on_dashboard(app, client):
    with app.app_context():
        wedding = Wedding.query.first()
        from app.extensions import db

        db.session.add(
            AuditLog(
                wedding_id=wedding.id,
                user_id=None,
                entity_type="task",
                entity_id="999",
                action="create",
                description="נוספה משימת בדיקה",
            )
        )
        db.session.commit()
    login(client)
    response = client.get("/activity")
    assert "נוספה משימת בדיקה" in response.get_data(as_text=True)
