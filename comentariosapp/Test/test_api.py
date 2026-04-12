from datetime import datetime
from types import SimpleNamespace
from uuid import uuid4
import sys
from pathlib import Path
from app.services.comment_crud import ReviewCrud
from sqlalchemy.exc import IntegrityError

import jwt

APP_ROOT = Path(__file__).resolve().parents[1]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from app.api import api as api_module
from main import app


def build_token(role="User", user_id=None, username="tester"):
    payload = {
        "sub": str(user_id or uuid4()),
        "username": username,
        "role": role,
    }
    return jwt.encode(payload, app.config["SECRET_KEY"], algorithm="HS256")


def auth_headers(role="User", user_id=None, username="tester"):
    return {
        "Authorization": f"Bearer {build_token(role=role, user_id=user_id, username=username)}"
    }


def make_review(review_id=None, hospedaje_id=None, user_id=None, username="tester"):
    return SimpleNamespace(
        id=review_id or uuid4(),
        hospedajeId=hospedaje_id or uuid4(),
        userId=user_id or uuid4(),
        userName=username,
        rating=5,
        comment="Excelente estadia",
        created_at=datetime(2026, 4, 6, 12, 0, 0),
        updated_at=datetime(2026, 4, 6, 12, 30, 0),
    )


def test_health_ok(client):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "healthy"}


def test_get_review_by_id_ok(client, monkeypatch):
    review_id = uuid4()
    review = make_review(review_id=review_id)
    monkeypatch.setattr(api_module.comment_crud, "get_review_by_id", lambda review_uuid: review if review_uuid == review_id else None)

    resp = client.get(f"/api/v1/reviews/{review_id}", headers=auth_headers())

    assert resp.status_code == 200
    assert resp.get_json() == {
        "id": str(review.id),
        "hospedajeId": str(review.hospedajeId),
        "userName": review.userName,
        "userId": str(review.userId),
        "rating": review.rating,
        "comment": review.comment,
        "created_at": review.created_at.isoformat(),
        "updated_at": review.updated_at.isoformat(),
    }


def test_get_review_by_id_requires_token(client):
    review_id = uuid4()

    resp = client.get(f"/api/v1/reviews/{review_id}")

    assert resp.status_code == 401
    assert resp.get_json() == {"message": "Token missing"}


def test_get_reviews_by_hospedaje_ok(client, monkeypatch):
    hospedaje_id = uuid4()
    reviews = [
        make_review(hospedaje_id=hospedaje_id, username="ana"),
        make_review(hospedaje_id=hospedaje_id, username="luis"),
    ]
    monkeypatch.setattr(api_module.comment_crud, "get_all_reviews_by_hospedaje_id", lambda value: reviews if value == hospedaje_id else [])

    resp = client.get(
        f"/api/v1/reviews/hospedajes/{hospedaje_id}",
        headers=auth_headers(),
    )

    assert resp.status_code == 200
    body = resp.get_json()
    assert len(body["comments"]) == 2
    assert body["comments"][0]["userName"] == "ana"
    assert body["comments"][1]["userName"] == "luis"


def test_get_reviews_by_hospedaje_not_found(client, monkeypatch):
    hospedaje_id = uuid4()
    monkeypatch.setattr(api_module.comment_crud, "get_all_reviews_by_hospedaje_id", lambda value: [])

    resp = client.get(
        f"/api/v1/reviews/hospedajes/{hospedaje_id}",
        headers=auth_headers(),
    )

    assert resp.status_code == 404
    assert resp.get_json() == {"message": "Commentarios no encontrados"}


def test_create_review_ok(client, monkeypatch):
    hospedaje_id = uuid4()
    user_id = uuid4()
    review = make_review(hospedaje_id=hospedaje_id, user_id=user_id, username="marco")

    monkeypatch.setattr(api_module.comment_crud, "create_review", lambda data: review)

    resp = client.post(
        "/api/v1/reviews",
        json={
            "hospedajeId": str(hospedaje_id),
            "comment": "Muy bueno",
            "rating": 5,
        },
        headers=auth_headers(user_id=user_id, username="marco"),
    )

    assert resp.status_code == 201
    assert resp.get_json() == {
        "id": str(review.id),
        "hospedajeId": str(review.hospedajeId),
        "userName": review.userName,
        "userId": str(review.userId),
        "rating": review.rating,
        "comment": review.comment,
        "created_at": review.created_at.isoformat(),
        "updated_at": review.updated_at.isoformat(),
    }


def test_update_review_ok(client, monkeypatch):
    review_id = uuid4()
    monkeypatch.setattr(api_module.comment_crud, "update_review", lambda review_uuid, data: True if review_uuid == review_id else None)

    resp = client.put(
        f"/api/v1/reviews/{review_id}",
        json={"comment": "Comentario actualizado", "rating": 4},
        headers=auth_headers(role="Administrator"),
    )

    assert resp.status_code == 200
    assert resp.get_json() == {"message": "Comment updated"}


def test_update_review_forbidden_for_non_admin(client):
    review_id = uuid4()

    resp = client.put(
        f"/api/v1/reviews/{review_id}",
        json={"comment": "Comentario actualizado", "rating": 4},
        headers=auth_headers(role="User"),
    )

    assert resp.status_code == 403
    assert resp.get_json() == {"message": "Unauthorized"}


def test_delete_review_ok(client, monkeypatch):
    review_id = uuid4()
    monkeypatch.setattr(api_module.comment_crud, "delete_review", lambda review_uuid: review_uuid == review_id)

    resp = client.delete(
        f"/api/v1/reviews/{review_id}",
        headers=auth_headers(role="Administrator"),
    )

    assert resp.status_code == 200
    assert resp.get_json() == {"message": "Comment deleted"}


def test_create_review(monkeypatch):
    review_crud = ReviewCrud()

    reviews = []
    review_data = {
        "hospedajeId": uuid4(),
        "userId": uuid4(),
        "userName": "testuser",
        "rating": 5,
        "comment": "Excelente estadia",
    }

    def fake_add(review):
        reviews.append(review)

    monkeypatch.setattr("app.services.comment_crud.db.session.add", fake_add)
    monkeypatch.setattr("app.services.comment_crud.db.session.commit", lambda: None)

    review = review_crud.create_review(review_data)

    assert reviews == [review]

def test_create_review_integrity_error(monkeypatch):
    review_crud = ReviewCrud()

    review_data = {
        "hospedajeId": uuid4(),
        "userId": uuid4(),
        "userName": "testuser",
        "rating": 5,
        "comment": "Excelente estadia",
    }

    def fake_add(review):
        raise IntegrityError("Integrity error", None, None)

    monkeypatch.setattr("app.services.comment_crud.db.session.add", fake_add)
    monkeypatch.setattr("app.services.comment_crud.db.session.rollback", lambda: None)

    review = review_crud.create_review(review_data)

    assert review is None

def test_get_review_by_id(monkeypatch):
    review_crud = ReviewCrud()
    review = SimpleNamespace(id=uuid4(), hospedaje_id=uuid4())
    reviews = [review]

    def fake_get(review_id):
        for r in reviews:
            if r.id == review_id:
                return r
        return None

    def fake_filter(*args, **kwargs):
        for r in reviews:
            if r.hospedaje_id == kwargs.get("hospedajeId"):
                return [r]
        return []
    
    mock_review_bd = SimpleNamespace(query=SimpleNamespace(get=fake_get),filter=SimpleNamespace(all=fake_filter))
    
    monkeypatch.setattr("app.services.comment_crud.Review", mock_review_bd)

    assert review_crud.get_review_by_id(review.id) == review
    assert review_crud.get_review_by_id(uuid4()) is None