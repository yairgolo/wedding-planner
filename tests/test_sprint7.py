from io import BytesIO

from app.extensions import db
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


def test_upload_pdf_with_hebrew_filename(client, app):
    client.post(
        "/auth/login",
        data={"email": "admin@example.com", "password": "password123"},
    )
    response = client.post(
        "/documents/new",
        data={
            "title": "חוזה אולם",
            "category": "contract",
            "vendor_id": "0",
            "file": (BytesIO(b"%PDF-1.7\n%%EOF"), "חוזה אולם.pdf"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "המסמך הועלה".encode() in response.data
    with app.app_context():
        document = db.session.scalar(db.select(Document))
        assert document is not None
        assert document.original_filename == "חוזה אולם.pdf"
        assert document.mime_type == "application/pdf"
