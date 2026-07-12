from app.models import Wedding


def test_wedding_profile_fields_exist(app):
    with app.app_context():
        wedding = Wedding.query.first()
        wedding.hebrew_date = "ח' בחשון תשפ\"ז"
        wedding.venue_capacity = 500
        assert wedding.hebrew_date
        assert wedding.venue_capacity == 500


def test_sprint8_pages_require_login(client):
    for path in ("/settings/wedding", "/search", "/notifications", "/imports", "/exports"):
        response = client.get(path)
        assert response.status_code in {302, 401}
