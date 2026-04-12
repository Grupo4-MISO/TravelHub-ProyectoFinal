from types import SimpleNamespace
from uuid import uuid4
from werkzeug.security import generate_password_hash
from app.api import api as api_module
from app.services.user_crud import UserCrud
from app.utils.seedHelper import SeedHelper
from app.utils.token_helper import generate_token
from sqlalchemy.exc import IntegrityError



def test_health_ok(client):
    resp = client.get("/api/v1/auth/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "healthy"}


def test_login_missing_credentials(client):
    resp = client.post("/api/v1/auth/login", json={})
    assert resp.status_code == 400
    assert resp.get_json()["message"] == "Missing credentials"


def test_login_invalid_credentials_user_not_found(client, monkeypatch):
    monkeypatch.setattr(api_module.user_crud, "get_user_by_email", lambda email: None)

    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "noexiste@travelhub.com", "password": "secret123"},
    )
    assert resp.status_code == 401
    assert resp.get_json()["message"] == "Invalid credentials"

def test_login_invalid_credentials_wrong_password(client, monkeypatch):
    fake_user = SimpleNamespace(
        id=uuid4(),
        username="admin",
        password_hash=generate_password_hash("secret123"),
        role=SimpleNamespace(value="Administrator"),
    )
    monkeypatch.setattr(api_module.user_crud, "get_user_by_email", lambda email: fake_user)
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@travelhub.com", "password": "wrongpassword"},
    )
    assert resp.status_code == 401
    assert resp.get_json()["message"] == "Invalid credentials"

def test_login_success(client, monkeypatch):
    fake_user = SimpleNamespace(
        id=uuid4(),
        username="admin",
        password_hash=generate_password_hash("secret123"),
        role=SimpleNamespace(value="Administrator"),
    )
    monkeypatch.setattr(api_module.user_crud, "get_user_by_email", lambda email: fake_user)

    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@travelhub.com", "password": "secret123"},
    )

    body = resp.get_json()
    assert resp.status_code == 200
    assert "token" in body
    assert body["user"]["username"] == "admin"
    assert body["user"]["role"] == "Administrator"


def test_create_user_missing_password(client):
    resp = client.post(
        "/api/v1/auth/users",
        json={"username": "u1", "email": "u1@x.com", "role": "Traveler"},
    )
    assert resp.status_code == 400
    assert resp.get_json()["message"] == "Missing password"


def test_create_user_invalid_role(client):
    resp = client.post(
        "/api/v1/auth/users",
        json={
            "username": "u1",
            "email": "u1@x.com",
            "password": "abc123",
            "role": "NoExiste",
        },
    )
    assert resp.status_code == 400
    assert "Invalid role" in resp.get_json()["message"]


def test_create_user_success_hashes_password(client, monkeypatch):
    captured = {}

    def fake_create_user(payload):
        captured["payload"] = payload
        return SimpleNamespace(
            id=uuid4(),
            username=payload["username"],
            email=payload["email"],
        )

    monkeypatch.setattr(api_module.user_crud, "create_user", fake_create_user)

    resp = client.post(
        "/api/v1/auth/users",
        json={
            "username": "nuevo",
            "email": "nuevo@travelhub.com",
            "password": "abc123",
            "role": "Traveler",
        },
    )

    body = resp.get_json()
    assert resp.status_code == 201
    assert body["username"] == "nuevo"
    assert "password" not in captured["payload"]
    assert "password_hash" in captured["payload"]
    assert captured["payload"]["role"].value == "Traveler"


def test_seed_users_success(client, monkeypatch):
    monkeypatch.setattr(api_module.SeedHelper, "create_default_users", lambda: None)

    resp = client.post("/api/v1/auth/user")

    assert resp.status_code == 200
    assert resp.get_json() == {"message": "Default users created"}

def test_seed_users_error(client, monkeypatch):
    def _raise_error():
        raise Exception("fallo seed")

    monkeypatch.setattr(api_module.SeedHelper, "create_default_users", _raise_error)

    resp = client.post("/api/v1/auth/user")
    body = resp.get_json()

    assert resp.status_code == 500
    assert body["message"] == "Error creating default users"
    assert "fallo seed" in body["error"]


def test_create_user_success(monkeypatch):
    crud = UserCrud()

    calls = {"add": 0, "commit": 0}

    def fake_add(_obj):
        calls["add"] += 1

    def fake_commit():
        calls["commit"] += 1

    monkeypatch.setattr("app.services.user_crud.db.session.add", fake_add)
    monkeypatch.setattr("app.services.user_crud.db.session.commit", fake_commit)

    user = crud.create_user({
        "username": "u1",
        "email": "u1@x.com",
        "password_hash": "hash",
        "role": None,
    })

    assert user is not None
    assert calls["add"] == 1
    assert calls["commit"] == 1


def test_create_user_mock_integrity(monkeypatch):
    crud = UserCrud()
    rolled_back = {"ok": False}

    def fake_commit():
        raise IntegrityError("stmt", "params", Exception("dup"))

    def fake_rollback():
        rolled_back["ok"] = True

    monkeypatch.setattr("app.services.user_crud.db.session.add", lambda _obj: None)
    monkeypatch.setattr("app.services.user_crud.db.session.commit", fake_commit)
    monkeypatch.setattr("app.services.user_crud.db.session.rollback", fake_rollback)

    user = crud.create_user({
        "username": "u1",
        "email": "u1@x.com",
        "password_hash": "hash",
        "role": None,
    })

    assert user is None
    assert rolled_back["ok"] is True

def test_get_user(monkeypatch):
    crud = UserCrud()
    fake_user = SimpleNamespace(id=uuid4(), username="u1", email="u1@x.com")
    fake_users = [fake_user]
    def fake_get(id):
        for user in fake_users:
            if user.id == id:
                return user
    
    def fake_filter_by(**kwargs):
        for user in fake_users:
            if user.username == kwargs.get("username"):
                return SimpleNamespace(first=lambda: user)
            if user.email == kwargs.get("email"):
                return SimpleNamespace(first=lambda: user)
        return SimpleNamespace(first=lambda: None)

    def fake_all():
        return fake_users
            
    mock_query = SimpleNamespace(get=fake_get, filter_by=fake_filter_by, all=fake_all)
    mock_user_db = SimpleNamespace(query=mock_query)

    monkeypatch.setattr("app.services.user_crud.User", mock_user_db)

    assert crud.get_user_by_id(fake_user.id) == fake_user
    assert crud.get_user_by_username(username=fake_user.username) == fake_user
    assert crud.get_user_by_email(email=fake_user.email) == fake_user
    assert crud.get_all_users() == fake_users
    assert crud.get_user_by_id(uuid4()) is None

def test_update_user(monkeypatch):
    crud = UserCrud()
    fake_user = SimpleNamespace(id=uuid4(), username="u1", email="u1@x.com")

    def fake_get(id):
        if id == fake_user.id:
            return fake_user
        return None
    
    monkeypatch.setattr(crud, "get_user_by_id", fake_get)
    monkeypatch.setattr("app.services.user_crud.db.session.commit", lambda: None)
    

    updated = crud.update_user(fake_user.id, {"username": "u2"})
    assert updated.username == "u2"
    assert crud.update_user(uuid4(), {"username": "u3"}) is None

def test_rollback_update_user(monkeypatch):
    crud = UserCrud()
    fake_user = SimpleNamespace(id=uuid4(), username="u1", email="u1@x.com")

    def fake_get(id):
        if id == fake_user.id:
            return fake_user
        return None
    
    def fake_raise():
        raise IntegrityError("stmt", "params", Exception("dup"))
    
    monkeypatch.setattr(crud, "get_user_by_id", fake_get)
    monkeypatch.setattr("app.services.user_crud.db.session.commit", fake_raise)
    monkeypatch.setattr("app.services.user_crud.db.session.rollback", lambda: None)

    updated = crud.update_user(fake_user.id, {"username": "u2"})
    assert updated is None

def test_delete_user(monkeypatch):
    crud = UserCrud()
    fake_user = SimpleNamespace(id=uuid4(), username="u1", email="u1@x.com")
    fake_users = [fake_user]

    def fake_get(id):
        if id == fake_user.id:
            return fake_user
        return None

    def fake_delete(user):
        fake_users.remove(user)
    
    monkeypatch.setattr(crud, "get_user_by_id", fake_get)
    monkeypatch.setattr("app.services.user_crud.db.session.commit", lambda: None)
    monkeypatch.setattr("app.services.user_crud.db.session.delete", fake_delete)

    crud.delete_user(fake_user.id)
    assert len(fake_users) == 0
    assert crud.delete_user(uuid4()) is False

def test_seed_users(monkeypatch):
    users = []

    def fake_create_user(self, payload):
        users.append(payload)

    mock_user = SimpleNamespace(
    query=SimpleNamespace(delete=lambda: None))

    monkeypatch.setattr("app.utils.seedHelper.User", mock_user)
    monkeypatch.setattr(UserCrud, "create_user", fake_create_user)
    
    SeedHelper.create_default_users()

    assert len(users) > 0

def test_generate_token(monkeypatch, client):
    fake_user = SimpleNamespace(id=uuid4(), username="u1", role=SimpleNamespace(value="Traveler"))
    
    fake_encode = lambda payload, secret, algorithm: "token"

    monkeypatch.setattr("app.utils.token_helper.jwt.encode", fake_encode)


    app = client.application
    with app.app_context():
        app.config["SECRET_KEY"] = "test"
        token = generate_token(fake_user)

    assert token == "token"
    