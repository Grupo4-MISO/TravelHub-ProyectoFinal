from datetime import datetime
import importlib
from types import SimpleNamespace
from uuid import uuid4
import sys
from pathlib import Path
from sqlalchemy.exc import IntegrityError

import jwt

APP_ROOT = Path(__file__).resolve().parents[1]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from app.api import api as api_module
from main import app
from app.services.manager_crud import ManagerCrud
from app.utils import token_helper


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


def make_manager(manager_id=None, hospedaje_id=None, user_id=None, username="tester", email="tester@example.com"):
    return SimpleNamespace(
        id=manager_id or uuid4(),
        hospedajeId=hospedaje_id or uuid4(),
        userId=user_id or uuid4(),
        userName=username,
        email=email,
        first_name="Test",
        last_name="User",
        created_at=datetime(2026, 4, 6, 12, 0, 0),
        updated_at=datetime(2026, 4, 6, 12, 30, 0),
    )


def test_health_ok(client):
    resp = client.get("/api/v1/Managers/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "healthy"}


def test_get_manager_by_id_ok(client, monkeypatch):
    manager_id = uuid4()
    manager = make_manager(manager_id=manager_id)
    monkeypatch.setattr(api_module.manager_crud, "get_manager_by_id", lambda manager_uuid: manager if manager_uuid == manager_id else None)

    resp = client.get(f"/api/v1/Managers/{manager_id}", headers=auth_headers())

    assert resp.status_code == 200
    assert resp.get_json() == {
        "id": str(manager.id),
        "hospedajeId": str(manager.hospedajeId),
        "userName": manager.userName,
        "userId": str(manager.userId),
        "email": manager.email,
        "first_name": manager.first_name,
        "last_name": manager.last_name,
        "created_at": manager.created_at.isoformat(),
        "updated_at": manager.updated_at.isoformat(),
    }


def test_get_manager_by_id_requires_token(client):
    manager_id = uuid4()

    resp = client.get(f"/api/v1/Managers/{manager_id}")

    assert resp.status_code == 401
    assert resp.get_json() == {"message": "Token missing"}


def test_get_managers_by_hospedaje_ok(client, monkeypatch):
    hospedaje_id = uuid4()
    managers = [
        make_manager(hospedaje_id=hospedaje_id, username="ana"),
        make_manager(hospedaje_id=hospedaje_id, username="luis"),
    ]
    monkeypatch.setattr(api_module.manager_crud, "get_all_managers_by_hospedaje_id", lambda value: managers if value == hospedaje_id else [])

    resp = client.get(
        f"/api/v1/Managers/hospedajes/{hospedaje_id}",
        headers=auth_headers(),
    )

    assert resp.status_code == 200
    body = resp.get_json()
    assert len(body["managers"]) == 2
    assert body["managers"][0]["userName"] == "ana"
    assert body["managers"][1]["userName"] == "luis"


def test_get_managers_by_hospedaje_not_found(client, monkeypatch):
    hospedaje_id = uuid4()
    monkeypatch.setattr(api_module.manager_crud, "get_all_managers_by_hospedaje_id", lambda value: [])

    resp = client.get(
        f"/api/v1/Managers/hospedajes/{hospedaje_id}",
        headers=auth_headers(),
    )

    assert resp.status_code == 404
    assert resp.get_json() == {"message": "Managers no encontrados"}


def test_create_manager_ok(client, monkeypatch):
    hospedaje_id = uuid4()
    user_id = uuid4()
    manager = make_manager(hospedaje_id=hospedaje_id, user_id=user_id, username="marco")

    monkeypatch.setattr(
        api_module.AsyncUserService,
        "validate_user_creation_data",
        lambda email, password, first_name, last_name: (True, None),
    )
    monkeypatch.setattr(
        api_module.AsyncUserService,
        "create_user_in_auth_service",
        lambda email, password, first_name, last_name, role="Manager": (
            {
                "id": str(user_id),
                "username": "marco",
                "email": "marco@example.com",
            },
            None,
        ),
    )
    monkeypatch.setattr(api_module.manager_crud, "create_manager", lambda data: manager)

    resp = client.post(
        "/api/v1/Managers",
        json={
            "hospedajeId": str(hospedaje_id),
            "email": "marco@example.com",
            "password": "Pass12345",
            "first_name": "Marco",
            "last_name": "User",
        },
    )

    assert resp.status_code == 201
    assert resp.get_json() == {
        "message": "Manager y usuario creados exitosamente",
        "manager": {
            "id": str(manager.id),
            "hospedajeId": str(manager.hospedajeId),
            "userName": manager.userName,
            "userId": str(manager.userId),
            "email": manager.email,
            "first_name": manager.first_name,
            "last_name": manager.last_name,
            "created_at": manager.created_at.isoformat(),
            "updated_at": manager.updated_at.isoformat(),
        },
        "user": {
            "id": str(user_id),
            "username": "marco",
            "email": "marco@example.com",
        },
    }


def test_update_manager_ok(client, monkeypatch):
    manager_id = uuid4()
    monkeypatch.setattr(api_module.manager_crud, "update_manager", lambda manager_uuid, data: True if manager_uuid == manager_id else None)

    resp = client.put(
        f"/api/v1/Managers/{manager_id}",
        json={"comment": "Comentario actualizado", "rating": 4},
        headers=auth_headers(role="Administrator"),
    )

    assert resp.status_code == 200
    assert resp.get_json() == {"message": "Manager updated"}


def test_update_manager_forbidden_for_non_admin(client):
    manager_id = uuid4()

    resp = client.put(
        f"/api/v1/Managers/{manager_id}",
        json={"comment": "Manager actualizado", "rating": 4},
        headers=auth_headers(role="User"),
    )

    assert resp.status_code == 403
    assert resp.get_json() == {"message": "Unauthorized"}


def test_delete_manager_ok(client, monkeypatch):
    manager_id = uuid4()
    monkeypatch.setattr(api_module.manager_crud, "delete_manager", lambda manager_uuid: manager_uuid == manager_id)

    resp = client.delete(
        f"/api/v1/Managers/{manager_id}",
        headers=auth_headers(role="Administrator"),
    )

    assert resp.status_code == 200
    assert resp.get_json() == {"message": "Manager deleted"}


def test_main_module_reload(monkeypatch):
    import main as main_module

    monkeypatch.setattr(main_module.db, "init_app", lambda _app: None)
    monkeypatch.setattr(main_module.db, "create_all", lambda: None)

    reloaded = importlib.reload(main_module)

    assert reloaded.app.config["JWT_SECRET_KEY"]
    assert reloaded.app.config["SECRET_KEY"] == reloaded.app.config["JWT_SECRET_KEY"]
    assert any(rule.rule == "/api/v1/Managers/health" for rule in reloaded.app.url_map.iter_rules())


def test_manager_crud_create_get_update_delete(monkeypatch):
    crud = ManagerCrud()

    fake_manager = make_manager()
    fake_manager_id = fake_manager.id

    class FakeQuery:
        def __init__(self, result):
            self.result = result

        def get(self, _id):
            return self.result if _id == fake_manager_id else None

        def filter(self, *args, **kwargs):
            return self

        def all(self):
            return [fake_manager]

    class FakeSession:
        def __init__(self):
            self.added = []
            self.committed = 0
            self.rolled_back = 0
            self.deleted = []

        def add(self, obj):
            self.added.append(obj)

        def commit(self):
            self.committed += 1

        def rollback(self):
            self.rolled_back += 1

        def delete(self, obj):
            self.deleted.append(obj)

    class FakeManagerModel:
        query = FakeQuery(fake_manager)
        hospedajeId = fake_manager.hospedajeId

        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
            self.created_at = datetime(2026, 4, 6, 12, 0, 0)
            self.updated_at = datetime(2026, 4, 6, 12, 30, 0)

    fake_session = FakeSession()
    monkeypatch.setattr("app.services.manager_crud.db.session", fake_session)
    monkeypatch.setattr("app.services.manager_crud.Manager", FakeManagerModel)

    created = crud.create_manager(
        {
            "hospedajeId": str(uuid4()),
            "userId": str(uuid4()),
            "userName": "tester",
            "email": "tester@example.com",
            "first_name": "Test",
            "last_name": "User",
        }
    )
    assert created is not None
    assert fake_session.committed == 1

    assert crud.get_manager_by_id(fake_manager_id) == fake_manager
    assert crud.get_all_managers_by_hospedaje_id(fake_manager.hospedajeId) == [fake_manager]

    updated = crud.update_manager(fake_manager_id, {"first_name": "Nuevo", "last_name": "Apellido"})
    assert updated.first_name == "Nuevo"
    assert updated.last_name == "Apellido"

    assert crud.update_manager(uuid4(), {"first_name": "X"}) is None
    assert crud.delete_manager(fake_manager_id) is True
    assert crud.delete_manager(uuid4()) is False


def test_manager_crud_error_branches(monkeypatch):
    crud = ManagerCrud()

    class FakeSession:
        def __init__(self):
            self.rolled_back = 0

        def add(self, obj):
            raise IntegrityError("stmt", "params", Exception("dup"))

        def commit(self):
            raise IntegrityError("stmt", "params", Exception("dup"))

        def rollback(self):
            self.rolled_back += 1

        def delete(self, obj):
            raise IntegrityError("stmt", "params", Exception("dup"))

    class FakeQuery:
        def get(self, _id):
            return None

        def filter(self, *args, **kwargs):
            return self

        def all(self):
            return []

    class FakeManagerModel:
        query = FakeQuery()

        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    monkeypatch.setattr("app.services.manager_crud.db.session", FakeSession())
    monkeypatch.setattr("app.services.manager_crud.Manager", FakeManagerModel)

    assert crud.create_manager(
        {
            "hospedajeId": str(uuid4()),
            "userId": str(uuid4()),
            "userName": "tester",
            "email": "tester@example.com",
            "first_name": "Test",
            "last_name": "User",
        }
    ) is None

    assert crud.update_manager(uuid4(), {"first_name": "X"}) is None
    assert crud.delete_manager(uuid4()) is False


def test_token_helper_functions(monkeypatch, client):
    fake_payload = {"sub": "123", "username": "tester", "role": "Manager"}

    monkeypatch.setattr("app.utils.token_helper.jwt.decode", lambda token, secret, algorithms: fake_payload)

    app_ctx = client.application
    with app_ctx.app_context():
        app_ctx.config["SECRET_KEY"] = app_ctx.config.get("SECRET_KEY") or app_ctx.config["JWT_SECRET_KEY"]

        with app_ctx.test_request_context(
            "/api/v1/Managers/health",
            headers={"Authorization": "Bearer fake-token"},
        ):
            assert token_helper.get_userId_from_token() == "123"
            assert token_helper.get_userName_from_token() == "tester"

