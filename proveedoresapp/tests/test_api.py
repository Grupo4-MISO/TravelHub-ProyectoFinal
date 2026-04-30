from datetime import datetime
import importlib
from pathlib import Path
import sys
from types import SimpleNamespace
from uuid import uuid4

import jwt
from sqlalchemy.exc import IntegrityError

APP_ROOT = Path(__file__).resolve().parents[1]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from app.api import api as api_module
from app.services.manager_crud import ManagerCrud
from app.utils import token_helper
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


def make_manager(manager_id=None, provider_id=None, user_id=None, email="tester@example.com"):
    return SimpleNamespace(
        id=manager_id or uuid4(),
        provider_id=provider_id or uuid4(),
        userId=user_id or uuid4(),
        email=email,
        first_name="Test",
        last_name="User",
        phone="3001234567",
        created_at=datetime(2026, 4, 6, 12, 0, 0),
        updated_at=datetime(2026, 4, 6, 12, 30, 0),
    )


def make_provider(provider_id=None):
    return SimpleNamespace(
        id=provider_id or uuid4(),
        name="Proveedor Test",
        documentNumber="900123456",
        providerStatus=SimpleNamespace(name="Pending"),
        created_at=datetime(2026, 4, 6, 12, 0, 0),
        updated_at=datetime(2026, 4, 6, 12, 30, 0),
    )


def make_provider_address(provider_id):
    return SimpleNamespace(
        id=uuid4(),
        provider_id=provider_id,
        line1="Calle 123",
        line2="Apto 456",
        city="Bogota",
        state="Cundinamarca",
        country="Colombia",
        countryCode="CO",
        postal_code="110111",
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
    monkeypatch.setattr(
        api_module.manager_crud,
        "get_manager_by_id",
        lambda manager_uuid: manager if manager_uuid == manager_id else None,
    )

    resp = client.get(f"/api/v1/Managers/{manager_id}", headers=auth_headers())

    assert resp.status_code == 200
    assert resp.get_json() == {
        "id": str(manager.id),
        "provider_id": str(manager.provider_id),
        "userId": str(manager.userId),
        "email": manager.email,
        "first_name": manager.first_name,
        "last_name": manager.last_name,
        "phone": manager.phone,
        "created_at": manager.created_at.isoformat(),
        "updated_at": manager.updated_at.isoformat(),
    }


def test_get_manager_by_id_requires_token(client):
    resp = client.get(f"/api/v1/Managers/{uuid4()}")
    assert resp.status_code == 401
    assert resp.get_json() == {"message": "Token missing"}


def test_get_managers_by_provider_ok(client, monkeypatch):
    provider_id = uuid4()
    managers = [
        make_manager(provider_id=provider_id, email="ana@example.com"),
        make_manager(provider_id=provider_id, email="luis@example.com"),
    ]
    monkeypatch.setattr(
        api_module.manager_crud,
        "get_all_managers_by_provider_id",
        lambda value: managers if value == provider_id else [],
    )

    resp = client.get(
        f"/api/v1/Managers/providers/{provider_id}",
        headers=auth_headers(),
    )

    assert resp.status_code == 200
    body = resp.get_json()
    assert len(body["managers"]) == 2
    assert body["managers"][0]["provider_id"] == str(provider_id)


def test_get_managers_by_provider_not_found(client, monkeypatch):
    monkeypatch.setattr(api_module.manager_crud, "get_all_managers_by_provider_id", lambda value: [])

    resp = client.get(
        f"/api/v1/Managers/providers/{uuid4()}",
        headers=auth_headers(),
    )

    assert resp.status_code == 404
    assert resp.get_json() == {"message": "Managers no encontrados"}


def test_get_manager_by_userid_ok(client, monkeypatch):
    user_id = uuid4()
    manager = make_manager(user_id=user_id)
    monkeypatch.setattr(
        api_module.manager_crud,
        "get_manager_by_userid",
        lambda value: manager if value == user_id else None,
    )

    resp = client.get(
        f"/api/v1/Managers/users/{user_id}",
        headers=auth_headers(),
    )

    assert resp.status_code == 200
    assert resp.get_json()["userId"] == str(user_id)


def test_get_provider_by_userid_includes_addresses(client, monkeypatch):
    user_id = uuid4()
    provider = make_provider()
    address = make_provider_address(provider.id)

    monkeypatch.setattr(
        api_module.manager_crud,
        "get_provider_by_userid",
        lambda value: (provider, [address]) if value == user_id else None,
    )

    resp = client.get(f"/api/v1/Managers/Providers/users/{user_id}")

    assert resp.status_code == 200
    body = resp.get_json()
    assert body["id"] == str(provider.id)
    assert len(body["addresses"]) == 1
    assert body["addresses"][0]["provider_id"] == str(provider.id)
    assert body["addresses"][0]["countryCode"] == "CO"


def test_create_manager_missing_nested_fields(client):
    resp = client.post(
        "/api/v1/Managers",
        json={"name": "Proveedor X", "documentNumber": "123", "manager": {}},
    )

    assert resp.status_code == 400
    assert "Faltan campos requeridos en manager" in resp.get_json()["message"]


def test_create_manager_ok(client, monkeypatch):
    provider = make_provider()
    manager = make_manager(provider_id=provider.id)
    user_id = uuid4()

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
                "username": "manager.test",
                "email": "manager@test.com",
            },
            None,
        ),
    )
    monkeypatch.setattr(api_module.manager_crud, "create_manager", lambda data: (provider, manager))

    address_payload = {
        "line1": "Calle 123",
        "line2": "Apto 456",
        "city": "Bogotá",
        "state": "Cundinamarca",
        "country": "Colombia",
        "countryCode": "CO",
        "postal_code": "110111",
    }

    resp = client.post(
        "/api/v1/Managers",
        json={
            "name": "Proveedor X",
            "documentNumber": "123456",
            "currency": "COP",
            "providerStatus": "pending",
            "description": "Pago hotel",
            "provider_payment_id": None,
            "url": None,
            "manager": {
                "first_name": "Ana",
                "last_name": "Lopez",
                "email": "manager@test.com",
                "phone": "3001234567",
                "password": "Pass12345",
            },
            "address": address_payload,
        },
    )

    body = resp.get_json()
    assert resp.status_code == 201
    assert body["message"] == "Provider, manager y dirección creados exitosamente"
    assert body["provider"]["id"] == str(provider.id)
    assert body["provider"]["name"] == provider.name
    assert body["provider"]["documentNumber"] == provider.documentNumber
    assert body["provider"]["providerStatus"] == provider.providerStatus.name
    assert body["manager"]["provider_id"] == str(provider.id)
    assert body["user"]["id"] == str(user_id)
    assert body["address"] == address_payload


def test_create_manager_returns_409_on_auth_duplicate(client, monkeypatch):
    monkeypatch.setattr(
        api_module.AsyncUserService,
        "validate_user_creation_data",
        lambda email, password, first_name, last_name: (True, None),
    )
    monkeypatch.setattr(
        api_module.AsyncUserService,
        "create_user_in_auth_service",
        lambda email, password, first_name, last_name, role="Manager": (None, "email ya registrado"),
    )

    resp = client.post(
        "/api/v1/Managers",
        json={
            "name": "Proveedor X",
            "documentNumber": "123456",
            "manager": {
                "first_name": "Ana",
                "last_name": "Lopez",
                "email": "manager@test.com",
                "password": "Pass12345",
            },
        },
    )

    assert resp.status_code == 409


def test_update_manager_ok(client, monkeypatch):
    manager_id = uuid4()
    monkeypatch.setattr(
        api_module.manager_crud,
        "update_manager",
        lambda manager_uuid, data: True if manager_uuid == manager_id else None,
    )

    resp = client.put(
        f"/api/v1/Managers/{manager_id}",
        json={"first_name": "Nuevo", "last_name": "Nombre"},
        headers=auth_headers(role="Admin"),
    )

    assert resp.status_code == 200
    assert resp.get_json() == {"message": "Manager updated"}


def test_update_manager_forbidden_for_non_admin(client):
    resp = client.put(
        f"/api/v1/Managers/{uuid4()}",
        json={"first_name": "Nuevo"},
        headers=auth_headers(role="User"),
    )

    assert resp.status_code == 403
    assert resp.get_json() == {"message": "Unauthorized"}


def test_delete_manager_ok(client, monkeypatch):
    manager_id = uuid4()
    monkeypatch.setattr(api_module.manager_crud, "delete_manager", lambda manager_uuid: manager_uuid == manager_id)

    resp = client.delete(
        f"/api/v1/Managers/{manager_id}",
        headers=auth_headers(role="Admin"),
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
    assert any(rule.rule == "/api/v1/Managers/providers/<string:id>" for rule in reloaded.app.url_map.iter_rules())


def test_manager_crud_create_get_update_delete(monkeypatch):
    crud = ManagerCrud()

    fake_provider_id = uuid4()
    fake_manager_id = uuid4()
    fake_user_id = uuid4()
    fake_manager = make_manager(manager_id=fake_manager_id, provider_id=fake_provider_id, user_id=fake_user_id)

    class FakeQuery:
        def __init__(self, result):
            self.result = result

        def get(self, _id):
            return self.result if _id == fake_manager_id else None

        def filter(self, *args, **kwargs):
            return self

        def all(self):
            return [self.result]

        def first(self):
            return self.result

    class FakeSession:
        def __init__(self):
            self.added = []
            self.committed = 0
            self.rolled_back = 0
            self.deleted = []

        def add(self, obj):
            self.added.append(obj)

        def flush(self):
            return None

        def commit(self):
            self.committed += 1

        def rollback(self):
            self.rolled_back += 1

        def delete(self, obj):
            self.deleted.append(obj)

    class FakeProviderModel:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
            self.id = fake_provider_id

    class FakeManagerModel:
        query = FakeQuery(fake_manager)
        provider_id = fake_provider_id
        userId = fake_user_id

        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
            self.id = fake_manager_id

    fake_session = FakeSession()
    monkeypatch.setattr("app.services.manager_crud.db.session", fake_session)
    monkeypatch.setattr("app.services.manager_crud.Provider", FakeProviderModel)
    monkeypatch.setattr("app.services.manager_crud.Manager", FakeManagerModel)

    created = crud.create_manager(
        {
            "name": "Proveedor Test",
            "documentNumber": "123456",
            "providerStatus": "pending",
            "userId": str(fake_user_id),
            "email": "tester@example.com",
            "first_name": "Test",
            "last_name": "User",
            "phone": "3001234567",
            "address": {
                "line1": "Calle 123",
                "city": "Bogotá",
                "state": "Cundinamarca",
                "country": "Colombia",
                "countryCode": "CO",
                "postal_code": "110111",
            },
        }
    )
    assert created is not None
    provider, manager = created
    assert provider.id == fake_provider_id
    assert manager.id == fake_manager_id
    assert fake_session.committed == 1

    assert crud.get_manager_by_id(fake_manager_id) == fake_manager
    assert crud.get_manager_by_userid(fake_user_id) == fake_manager
    assert crud.get_all_managers_by_provider_id(fake_provider_id) == [fake_manager]

    updated = crud.update_manager(fake_manager_id, {"first_name": "Nuevo", "last_name": "Apellido"})
    assert updated.first_name == "Nuevo"
    assert updated.last_name == "Apellido"

    assert crud.update_manager(uuid4(), {"first_name": "X"}) is None
    assert crud.delete_manager(fake_manager_id) is True
    assert crud.delete_manager(uuid4()) is False


def test_manager_crud_error_branches(monkeypatch):
    crud = ManagerCrud()

    class FakeSession:
        def add(self, obj):
            raise IntegrityError("stmt", "params", Exception("dup"))

        def flush(self):
            return None

        def commit(self):
            raise IntegrityError("stmt", "params", Exception("dup"))

        def rollback(self):
            return None

        def delete(self, obj):
            raise IntegrityError("stmt", "params", Exception("dup"))

    class FakeQuery:
        def get(self, _id):
            return None

        def filter(self, *args, **kwargs):
            return self

        def all(self):
            return []

        def first(self):
            return None

    class FakeProviderModel:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
            self.id = uuid4()

    class FakeManagerModel:
        query = FakeQuery()
        provider_id = uuid4()
        userId = uuid4()

        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    monkeypatch.setattr("app.services.manager_crud.db.session", FakeSession())
    monkeypatch.setattr("app.services.manager_crud.Provider", FakeProviderModel)
    monkeypatch.setattr("app.services.manager_crud.Manager", FakeManagerModel)

    assert crud.create_manager(
        {
            "name": "Proveedor Test",
            "documentNumber": "123456",
            "providerStatus": "pending",
            "userId": str(uuid4()),
            "email": "tester@example.com",
            "first_name": "Test",
            "last_name": "User",
            "phone": "3001234567",
            "address": {
                "line1": "Calle 123",
                "city": "Bogotá",
                "state": "Cundinamarca",
                "country": "Colombia",
                "countryCode": "CO",
                "postal_code": "110111",
            },
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

