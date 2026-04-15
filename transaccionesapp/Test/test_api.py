import json
from pathlib import Path
import sys
from uuid import uuid4

import jwt
import pytest

APP_ROOT = Path(__file__).resolve().parents[1]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from app.db.models import db
from main import app


def _auth_headers(role="User"):
    token = jwt.encode(
        {"sub": str(uuid4()), "username": "tester", "role": role},
        app.config["JWT_SECRET_KEY"],
        algorithm="HS256",
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client():
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


@pytest.fixture
def user_headers():
    return _auth_headers("User")


@pytest.fixture
def admin_headers():
    return _auth_headers("Admin")


class TestHealth:
    def test_health_check(self, client):
        response = client.get("/api/v1/Transactions/health")
        assert response.status_code == 200
        assert response.json == {"status": "healthy"}


class TestAuthGuards:
    def test_protected_endpoint_without_token_returns_401(self, client):
        response = client.get("/api/v1/Transactions/providers")
        assert response.status_code == 401
        assert response.json["message"] == "Token missing"

    def test_admin_endpoint_with_non_admin_role_returns_403(self, client, user_headers):
        payload = {"name": "Stripe"}
        response = client.post(
            "/api/v1/Transactions/providers",
            data=json.dumps(payload),
            content_type="application/json",
            headers=user_headers,
        )
        assert response.status_code == 403
        assert response.json["message"] == "Unauthorized"


class TestPaymentProviders:
    def test_create_provider(self, client, admin_headers):
        payload = {
            "name": "Stripe",
            "config": {"apiKey": "test_123"},
            "is_active": True,
            "logo": "https://example.com/stripe.png",
        }
        response = client.post(
            "/api/v1/Transactions/providers",
            data=json.dumps(payload),
            content_type="application/json",
            headers=admin_headers,
        )
        assert response.status_code == 201
        data = response.json
        assert data["name"] == "Stripe"
        assert data["is_active"] is True
        assert "id" in data

    def test_create_provider_missing_name(self, client, admin_headers):
        payload = {"config": {}}
        response = client.post(
            "/api/v1/Transactions/providers",
            data=json.dumps(payload),
            content_type="application/json",
            headers=admin_headers,
        )
        assert response.status_code == 400
        assert "name" in response.json["message"].lower()

    def test_get_provider_by_id(self, client, admin_headers, user_headers):
        payload = {"name": "PayPal", "config": {}}
        response_create = client.post(
            "/api/v1/Transactions/providers",
            data=json.dumps(payload),
            content_type="application/json",
            headers=admin_headers,
        )
        provider_id = response_create.json["id"]

        response = client.get(
            f"/api/v1/Transactions/providers/{provider_id}",
            headers=user_headers,
        )
        assert response.status_code == 200
        assert response.json["id"] == provider_id
        assert response.json["name"] == "PayPal"

    def test_get_provider_not_found(self, client, user_headers):
        fake_id = str(uuid4())
        response = client.get(
            f"/api/v1/Transactions/providers/{fake_id}",
            headers=user_headers,
        )
        assert response.status_code == 404

    def test_update_provider(self, client, admin_headers):
        payload = {"name": "MercadoPago", "is_active": True}
        response_create = client.post(
            "/api/v1/Transactions/providers",
            data=json.dumps(payload),
            content_type="application/json",
            headers=admin_headers,
        )
        provider_id = response_create.json["id"]

        update_payload = {"is_active": False, "name": "MercadoPago Updated"}
        response = client.put(
            f"/api/v1/Transactions/providers/{provider_id}",
            data=json.dumps(update_payload),
            content_type="application/json",
            headers=admin_headers,
        )
        assert response.status_code == 200
        assert response.json["is_active"] is False
        assert response.json["name"] == "MercadoPago Updated"

    def test_delete_provider(self, client, admin_headers, user_headers):
        payload = {"name": "test_provider"}
        response_create = client.post(
            "/api/v1/Transactions/providers",
            data=json.dumps(payload),
            content_type="application/json",
            headers=admin_headers,
        )
        provider_id = response_create.json["id"]

        response = client.delete(
            f"/api/v1/Transactions/providers/{provider_id}",
            headers=admin_headers,
        )
        assert response.status_code == 200

        response = client.get(
            f"/api/v1/Transactions/providers/{provider_id}",
            headers=user_headers,
        )
        assert response.status_code == 404


class TestPayments:
    def test_create_payment(self, client, user_headers):
        payload = {
            "reserva_id": str(uuid4()),
            "amount": 100.50,
            "currency": "COP",
            "provider_id": str(uuid4()),
            "url": "https://pay.example/checkout/abc123",
            "description": "Pago de reserva",
        }
        response = client.post(
            "/api/v1/Transactions/payments",
            data=json.dumps(payload),
            content_type="application/json",
            headers=user_headers,
        )
        assert response.status_code == 201
        data = response.json
        assert data["reserva_id"] == payload["reserva_id"]
        assert float(data["amount"]) == 100.50
        assert data["currency"] == "COP"
        assert data["url"] == payload["url"]
        assert data["status"] == "pending"

    def test_create_payment_missing_required(self, client, user_headers):
        payload = {"reserva_id": str(uuid4())}
        response = client.post(
            "/api/v1/Transactions/payments",
            data=json.dumps(payload),
            content_type="application/json",
            headers=user_headers,
        )
        assert response.status_code == 400
        assert "requeridos" in response.json["message"].lower()

    def test_get_payment_by_id(self, client, user_headers):
        payload = {
            "reserva_id": str(uuid4()),
            "amount": 50.00,
            "currency": "USD",
        }
        response_create = client.post(
            "/api/v1/Transactions/payments",
            data=json.dumps(payload),
            content_type="application/json",
            headers=user_headers,
        )
        payment_id = response_create.json["id"]

        response = client.get(
            f"/api/v1/Transactions/payments/{payment_id}",
            headers=user_headers,
        )
        assert response.status_code == 200
        assert response.json["id"] == payment_id

    def test_get_payment_not_found(self, client, user_headers):
        fake_id = str(uuid4())
        response = client.get(
            f"/api/v1/Transactions/payments/{fake_id}",
            headers=user_headers,
        )
        assert response.status_code == 404

    def test_update_payment(self, client, user_headers, admin_headers):
        payload = {
            "reserva_id": str(uuid4()),
            "amount": 75.00,
            "currency": "EUR",
        }
        response_create = client.post(
            "/api/v1/Transactions/payments",
            data=json.dumps(payload),
            content_type="application/json",
            headers=user_headers,
        )
        payment_id = response_create.json["id"]

        update_payload = {
            "status": "captured",
            "description": "Pago capturado",
            "url": "https://pay.example/checkout/updated",
        }
        response = client.put(
            f"/api/v1/Transactions/payments/{payment_id}",
            data=json.dumps(update_payload),
            content_type="application/json",
            headers=admin_headers,
        )
        assert response.status_code == 200
        assert response.json["status"] == "captured"
        assert response.json["description"] == "Pago capturado"
        assert response.json["url"] == "https://pay.example/checkout/updated"

    def test_delete_payment(self, client, user_headers, admin_headers):
        payload = {
            "reserva_id": str(uuid4()),
            "amount": 25.00,
            "currency": "GBP",
        }
        response_create = client.post(
            "/api/v1/Transactions/payments",
            data=json.dumps(payload),
            content_type="application/json",
            headers=user_headers,
        )
        payment_id = response_create.json["id"]

        response = client.delete(
            f"/api/v1/Transactions/payments/{payment_id}",
            headers=admin_headers,
        )
        assert response.status_code == 200

        response = client.get(
            f"/api/v1/Transactions/payments/{payment_id}",
            headers=user_headers,
        )
        assert response.status_code == 404

    def test_get_payments_by_reserva_id(self, client, user_headers):
        reserva_1 = str(uuid4())
        reserva_2 = str(uuid4())

        for i in range(2):
            payload = {"reserva_id": reserva_1, "amount": 10.0 + i, "currency": "COP"}
            client.post(
                "/api/v1/Transactions/payments",
                data=json.dumps(payload),
                content_type="application/json",
                headers=user_headers,
            )

        payload = {"reserva_id": reserva_2, "amount": 50.0, "currency": "COP"}
        client.post(
            "/api/v1/Transactions/payments",
            data=json.dumps(payload),
            content_type="application/json",
            headers=user_headers,
        )

        response = client.get(
            f"/api/v1/Transactions/payments/reserva/{reserva_1}",
            headers=user_headers,
        )
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) == 2

    def test_get_payments_by_provider_id(self, client, user_headers, admin_headers):
        provider_resp = client.post(
            "/api/v1/Transactions/providers",
            data=json.dumps({"name": "TestProvider"}),
            content_type="application/json",
            headers=admin_headers,
        )
        provider_id = provider_resp.json["id"]

        for i in range(2):
            payload = {
                "reserva_id": str(uuid4()),
                "amount": 10.0 + i,
                "currency": "COP",
                "provider_id": provider_id,
            }
            client.post(
                "/api/v1/Transactions/payments",
                data=json.dumps(payload),
                content_type="application/json",
                headers=user_headers,
            )

        response = client.get(
            f"/api/v1/Transactions/payments/provider/{provider_id}",
            headers=user_headers,
        )
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) == 2


class TestPaymentTransactions:
    def test_create_transaction(self, client, user_headers, admin_headers):
        payment_payload = {"reserva_id": str(uuid4()), "amount": 100.00, "currency": "COP"}
        payment_resp = client.post(
            "/api/v1/Transactions/payments",
            data=json.dumps(payment_payload),
            content_type="application/json",
            headers=user_headers,
        )
        payment_id = payment_resp.json["id"]

        tx_payload = {
            "payment_id": payment_id,
            "provider_transaction_id": "stripe_tx_123",
            "status": "pending",
        }
        response = client.post(
            "/api/v1/Transactions/attempts",
            data=json.dumps(tx_payload),
            content_type="application/json",
            headers=admin_headers,
        )
        assert response.status_code == 201
        data = response.json
        assert data["payment_id"] == payment_id
        assert data["provider_transaction_id"] == "stripe_tx_123"
        assert "url" not in data

    def test_create_transaction_missing_required(self, client, admin_headers):
        payload = {"payment_id": str(uuid4())}
        response = client.post(
            "/api/v1/Transactions/attempts",
            data=json.dumps(payload),
            content_type="application/json",
            headers=admin_headers,
        )
        assert response.status_code == 400
        assert "requeridos" in response.json["message"].lower()

    def test_get_transaction_by_id(self, client, user_headers, admin_headers):
        payment_payload = {"reserva_id": str(uuid4()), "amount": 50.00, "currency": "COP"}
        payment_resp = client.post(
            "/api/v1/Transactions/payments",
            data=json.dumps(payment_payload),
            content_type="application/json",
            headers=user_headers,
        )
        payment_id = payment_resp.json["id"]

        tx_payload = {"payment_id": payment_id, "provider_transaction_id": "pay_456"}
        tx_resp = client.post(
            "/api/v1/Transactions/attempts",
            data=json.dumps(tx_payload),
            content_type="application/json",
            headers=admin_headers,
        )
        tx_id = tx_resp.json["id"]

        response = client.get(
            f"/api/v1/Transactions/attempts/{tx_id}",
            headers=user_headers,
        )
        assert response.status_code == 200
        assert response.json["id"] == tx_id
        assert response.json["payment_id"] == payment_id

    def test_get_transaction_not_found(self, client, user_headers):
        fake_id = str(uuid4())
        response = client.get(
            f"/api/v1/Transactions/attempts/{fake_id}",
            headers=user_headers,
        )
        assert response.status_code == 404

    def test_update_transaction(self, client, user_headers, admin_headers):
        payment_payload = {"reserva_id": str(uuid4()), "amount": 75.00, "currency": "COP"}
        payment_resp = client.post(
            "/api/v1/Transactions/payments",
            data=json.dumps(payment_payload),
            content_type="application/json",
            headers=user_headers,
        )
        payment_id = payment_resp.json["id"]

        tx_payload = {"payment_id": payment_id, "provider_transaction_id": "tx_789"}
        tx_resp = client.post(
            "/api/v1/Transactions/attempts",
            data=json.dumps(tx_payload),
            content_type="application/json",
            headers=admin_headers,
        )
        tx_id = tx_resp.json["id"]

        response = client.put(
            f"/api/v1/Transactions/attempts/{tx_id}",
            data=json.dumps({"status": "success"}),
            content_type="application/json",
            headers=admin_headers,
        )
        assert response.status_code == 200
        assert response.json["status"] == "success"

    def test_delete_transaction(self, client, user_headers, admin_headers):
        payment_payload = {"reserva_id": str(uuid4()), "amount": 25.00, "currency": "COP"}
        payment_resp = client.post(
            "/api/v1/Transactions/payments",
            data=json.dumps(payment_payload),
            content_type="application/json",
            headers=user_headers,
        )
        payment_id = payment_resp.json["id"]

        tx_payload = {"payment_id": payment_id, "provider_transaction_id": "tx_delete"}
        tx_resp = client.post(
            "/api/v1/Transactions/attempts",
            data=json.dumps(tx_payload),
            content_type="application/json",
            headers=admin_headers,
        )
        tx_id = tx_resp.json["id"]

        response = client.delete(
            f"/api/v1/Transactions/attempts/{tx_id}",
            headers=admin_headers,
        )
        assert response.status_code == 200

        response = client.get(
            f"/api/v1/Transactions/attempts/{tx_id}",
            headers=user_headers,
        )
        assert response.status_code == 404

    def test_get_transactions_by_payment_id(self, client, user_headers, admin_headers):
        payment_payload = {"reserva_id": str(uuid4()), "amount": 100.00, "currency": "COP"}
        payment_resp = client.post(
            "/api/v1/Transactions/payments",
            data=json.dumps(payment_payload),
            content_type="application/json",
            headers=user_headers,
        )
        payment_id = payment_resp.json["id"]

        for i in range(3):
            tx_payload = {"payment_id": payment_id, "provider_transaction_id": f"tx_{i}"}
            client.post(
                "/api/v1/Transactions/attempts",
                data=json.dumps(tx_payload),
                content_type="application/json",
                headers=admin_headers,
            )

        response = client.get(
            f"/api/v1/Transactions/attempts/payment/{payment_id}",
            headers=user_headers,
        )
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) == 3

    def test_get_empty_transactions_for_payment(self, client, user_headers):
        fake_payment_id = str(uuid4())
        response = client.get(
            f"/api/v1/Transactions/attempts/payment/{fake_payment_id}",
            headers=user_headers,
        )
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) == 0


class TestSeed:
    def test_seed_db(self, client):
        response = client.post("/api/v1/Transactions/seed")
        assert response.status_code == 200
        data = response.json
        assert "msg" in data
        assert "Proveedores procesados" in data
        assert data["Proveedores procesados"] == 3


class TestInvalidUUIDs:
    def test_invalid_uuid_format_provider(self, client, user_headers):
        response = client.get(
            "/api/v1/Transactions/providers/not-a-uuid",
            headers=user_headers,
        )
        assert response.status_code == 400

    def test_invalid_uuid_format_payment(self, client, user_headers):
        response = client.get(
            "/api/v1/Transactions/payments/invalid-uuid",
            headers=user_headers,
        )
        assert response.status_code == 400

    def test_invalid_uuid_format_transaction(self, client, user_headers):
        response = client.get(
            "/api/v1/Transactions/attempts/bad-uuid",
            headers=user_headers,
        )
        assert response.status_code == 400

    def test_invalid_uuid_filter_reserva(self, client, user_headers):
        response = client.get(
            "/api/v1/Transactions/payments/reserva/not-uuid",
            headers=user_headers,
        )
        assert response.status_code == 400

    def test_invalid_uuid_filter_provider(self, client, user_headers):
        response = client.get(
            "/api/v1/Transactions/payments/provider/not-uuid",
            headers=user_headers,
        )
        assert response.status_code == 400

    def test_invalid_uuid_filter_payment(self, client, user_headers):
        response = client.get(
            "/api/v1/Transactions/attempts/payment/not-uuid",
            headers=user_headers,
        )
        assert response.status_code == 400
