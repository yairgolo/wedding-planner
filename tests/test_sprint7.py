from app.models import Document, Gift


def test_sprint7_models_exist(app):
    with app.app_context():
        assert Gift.__tablename__ == "gifts"
        assert Document.__tablename__ == "documents"


def test_gifts_requires_login(client):
    response = client.get("/gifts")
    assert response.status_code in {302, 401}


def test_documents_requires_login(client):
    response = client.get("/documents")
    assert response.status_code in {302, 401}
