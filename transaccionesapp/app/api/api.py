from decimal import Decimal
from uuid import UUID, uuid4

import requests
from flask import current_app, request
from flask_restful import Resource

from app.services.transactions_crud import (
    payment_crud,
    payment_provider_crud,
    payment_transaction_crud,
)
from app.utils.seedHelper import SeedHelper
from app.utils.token_helper import roles_required, token_required


def _parse_uuid(value):
    if value is None:
        return None
    return UUID(str(value))


def _serialize_payment_provider(payment_provider):
    return {
        "id": str(payment_provider.id),
        "name": payment_provider.name,
        "config": payment_provider.config,
        "is_active": payment_provider.is_active,
        "logo": payment_provider.logo,
        "created_at": payment_provider.created_at.isoformat() if payment_provider.created_at else None,
        "updated_at": payment_provider.updated_at.isoformat() if payment_provider.updated_at else None,
    }


def _serialize_payment(payment):
    amount = payment.amount
    if isinstance(amount, Decimal):
        amount = float(amount)

    return {
        "id": str(payment.id),
        "reserva_id": str(payment.reserva_id) if payment.reserva_id else None,
        "provider_id": str(payment.provider_id) if payment.provider_id else None,
        "amount": amount,
        "currency": payment.currency,
        "status": payment.status.value if payment.status else None,
        "provider_payment_id": payment.provider_payment_id,
        "url": payment.url,
        "description": payment.description,
        "metadata": payment.payment_metadata,
        "created_at": payment.created_at.isoformat() if payment.created_at else None,
        "updated_at": payment.updated_at.isoformat() if payment.updated_at else None,
    }


def _serialize_payment_transaction(payment_transaction):
    return {
        "id": str(payment_transaction.id),
        "payment_id": str(payment_transaction.payment_id) if payment_transaction.payment_id else None,
        "status": payment_transaction.status.value if payment_transaction.status else None,
        "provider_transaction_id": payment_transaction.provider_transaction_id,
        "response": payment_transaction.response,
        "created_at": payment_transaction.created_at.isoformat() if payment_transaction.created_at else None,
        "updated_at": payment_transaction.updated_at.isoformat() if payment_transaction.updated_at else None,
    }


def _extract_session_url(session_response: dict):
    if not isinstance(session_response, dict):
        return None

    for key in ("url", "payment_url", "checkout_url", "session_url", "redirect_url"):
        value = session_response.get(key)
        if value:
            return value

    return None


def _map_session_status_to_payment_status(session_status: str):
    if not session_status:
        return None

    normalized_status = str(session_status).strip().lower()
    status_mapping = {
        "created": "pending",
        "pending": "pending",
        "authorized": "authorized",
        "captured": "captured",
        "failed": "failed",
        "cancelled": "cancelled",
        "refunded": "refunded",
    }
    return status_mapping.get(normalized_status)


def _create_external_payment_session(payment_id: str, payload: dict):
    if current_app.config.get("TESTING"):
        fake_session_id = f"ps_{uuid4().hex[:16]}"
        return {
            "ok": True,
            "session_response": {
                "session_id": fake_session_id,
                "payment_id": payment_id,
                "checkout_url": payload.get("url") or f"https://external-payment-provider.onrender.com/checkout/{fake_session_id}",
                "status": "created",
            },
        }

    session_payload = {
        "payment_id": payment_id,
        "amount": payload.get("amount"),
        "webhook_url": current_app.config.get("PAYMENT_WEBHOOK_URL"),
        "currency": payload.get("currency"),
        "customer_id": payload.get("customer_id") or str(payload.get("reserva_id")),
        "simulate_outcome": current_app.config.get("PAYMENT_SIMULATE_OUTCOME", "success"),
        "callback_delay_seconds": current_app.config.get("PAYMENT_CALLBACK_DELAY_SECONDS", 20),
    }

    try:
        response = requests.post(
            current_app.config.get("EXTERNAL_PAYMENT_SESSION_URL"),
            json=session_payload,
            timeout=current_app.config.get("PAYMENT_SESSION_TIMEOUT_SECONDS", 10),
        )
    except requests.RequestException as exc:
        return {"ok": False, "error": f"No fue posible crear la sesion de pago: {str(exc)}"}

    if response.status_code not in (200, 201):
        return {
            "ok": False,
            "error": "El proveedor externo no pudo crear la sesion de pago",
            "status_code": response.status_code,
            "response_text": response.text,
        }

    try:
        session_response = response.json()
    except ValueError:
        session_response = {}

    return {"ok": True, "session_response": session_response}

class Health(Resource):
    def get(self):
        """
        Health check del servicio
        ---
        tags:
          - Health
        responses:
          200:
            description: Servicio operativo
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: healthy
        """
        return {"status": "healthy"}, 200


class PaymentProviderResource(Resource):
    def get(self):
        """
        Listar proveedores de pago
        ---
        tags:
          - PaymentProviders
        security:
          - Bearer: []
        responses:
          200:
            description: Lista de proveedores de pago
          401:
            description: Token faltante o invalido
        """
        providers = payment_provider_crud.get_all_payment_providers()
        return [_serialize_payment_provider(provider) for provider in providers], 200

    @token_required
    @roles_required("Admin")
    def post(current_user, self):
        """
        Crear proveedor de pago
        ---
        tags:
          - PaymentProviders
        security:
          - Bearer: []
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              required: [name]
              properties:
                name:
                  type: string
                config:
                  type: object
                is_active:
                  type: boolean
                logo:
                  type: string
        responses:
          201:
            description: Proveedor creado
          400:
            description: Datos invalidos
          401:
            description: Token faltante o invalido
          403:
            description: Rol no autorizado
        """
        payload = request.get_json() or {}
        if not payload.get("name"):
            return {"message": "El campo name es requerido"}, 400

        provider = payment_provider_crud.create_payment_provider(payload)
        if not provider:
            return {"message": "No fue posible crear el proveedor de pago"}, 400

        return _serialize_payment_provider(provider), 201


class PaymentProviderByIdResource(Resource):
    @token_required
    def get(current_user, self, id):
        """
        Obtener proveedor de pago por id
        ---
        tags:
          - PaymentProviders
        security:
          - Bearer: []
        parameters:
          - in: path
            name: id
            type: string
            required: true
        responses:
          200:
            description: Proveedor encontrado
          400:
            description: Id invalido
          401:
            description: Token faltante o invalido
          404:
            description: No encontrado
        """
        try:
            provider_id = _parse_uuid(id)
        except ValueError:
            return {"message": "provider_id invalido"}, 400

        provider = payment_provider_crud.get_payment_provider_by_id(provider_id)
        if not provider:
            return {"message": "Proveedor de pago no encontrado"}, 404

        return _serialize_payment_provider(provider), 200

    @token_required
    @roles_required("Admin")
    def put(current_user, self, id):
        """
        Actualizar proveedor de pago
        ---
        tags:
          - PaymentProviders
        security:
          - Bearer: []
        parameters:
          - in: path
            name: id
            type: string
            required: true
          - in: body
            name: body
            required: true
            schema:
              type: object
              properties:
                name:
                  type: string
                config:
                  type: object
                is_active:
                  type: boolean
                logo:
                  type: string
        responses:
          200:
            description: Proveedor actualizado
          400:
            description: Error de validacion o actualizacion
          401:
            description: Token faltante o invalido
          403:
            description: Rol no autorizado
          404:
            description: No encontrado
        """
        try:
            provider_id = _parse_uuid(id)
        except ValueError:
            return {"message": "provider_id invalido"}, 400

        payload = request.get_json() or {}
        provider = payment_provider_crud.update_payment_provider(provider_id, payload)
        if not provider:
            return {"message": "No fue posible actualizar el proveedor de pago"}, 400

        return _serialize_payment_provider(provider), 200

    @token_required
    @roles_required("Admin")
    def delete(current_user, self, id):
        """
        Eliminar proveedor de pago
        ---
        tags:
          - PaymentProviders
        security:
          - Bearer: []
        parameters:
          - in: path
            name: id
            type: string
            required: true
        responses:
          200:
            description: Proveedor eliminado
          400:
            description: Id invalido
          401:
            description: Token faltante o invalido
          403:
            description: Rol no autorizado
          404:
            description: No encontrado
        """
        try:
            provider_id = _parse_uuid(id)
        except ValueError:
            return {"message": "provider_id invalido"}, 400

        deleted = payment_provider_crud.delete_payment_provider(provider_id)
        if not deleted:
            return {"message": "Proveedor de pago no encontrado"}, 404

        return {"message": "Proveedor de pago eliminado"}, 200


class PaymentResource(Resource):
    @token_required
    def post(current_user, self):
        """
        Crear pago
        ---
        tags:
          - Payments
        security:
          - Bearer: []
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              required: [reserva_id, amount, currency]
              properties:
                reserva_id:
                  type: string
                provider_id:
                  type: string
                amount:
                  type: number
                currency:
                  type: string
                status:
                  type: string
                provider_payment_id:
                  type: string
                url:
                  type: string
                description:
                  type: string
                metadata:
                  type: object
        responses:
          201:
            description: Pago creado
          400:
            description: Datos invalidos
          401:
            description: Token faltante o invalido
        """
        payload = request.get_json() or {}

        required_fields = ["reserva_id", "amount", "currency"]
        missing_fields = [field for field in required_fields if payload.get(field) in (None, "")]
        if missing_fields:
            return {"message": f"Faltan campos requeridos: {', '.join(missing_fields)}"}, 400

        provider_payment_id = payload.get("provider_payment_id") or f"pay_{uuid4().hex[:12]}"
        session_result = _create_external_payment_session(provider_payment_id, payload)

        payload_to_store = dict(payload)
        payload_to_store["provider_payment_id"] = provider_payment_id

        if session_result["ok"]:
            session_response = session_result.get("session_response") or {}
            session_payment_status = _map_session_status_to_payment_status(session_response.get("status"))
            payload_to_store["status"] = payload.get("status") or session_payment_status or "pending"
            payload_to_store["url"] = _extract_session_url(session_response)

            metadata = payload_to_store.get("metadata") if isinstance(payload_to_store.get("metadata"), dict) else {}
            metadata["payment_session_response"] = session_response
            payload_to_store["metadata"] = metadata
        else:
            payload_to_store["status"] = "failed"
            payload_to_store["url"] = None

            metadata = payload_to_store.get("metadata") if isinstance(payload_to_store.get("metadata"), dict) else {}
            metadata["payment_session_error"] = session_result
            payload_to_store["metadata"] = metadata

        payment = payment_crud.create_payment(payload_to_store)
        if not payment:
            return {"message": "No fue posible crear el pago"}, 400

        if not session_result["ok"]:
            return {
                "message": "No fue posible crear la sesion en el proveedor externo",
                "payment": _serialize_payment(payment),
            }, 400

        return _serialize_payment(payment), 201

class PaymentResourceById(Resource):
    @token_required
    def get(current_user, self, id):
        """
        Obtener pago por id
        ---
        tags:
          - Payments
        security:
          - Bearer: []
        parameters:
          - in: path
            name: id
            type: string
            required: true
        responses:
          200:
            description: Pago encontrado
          400:
            description: Id invalido
          401:
            description: Token faltante o invalido
          404:
            description: No encontrado
        """
        try:
            payment_id = _parse_uuid(id)
        except ValueError:
            return {"message": "payment_id invalido"}, 400

        payment = payment_crud.get_payment_by_id(payment_id)
        if not payment:
            return {"message": "Pago no encontrado"}, 404

        return _serialize_payment(payment), 200

class PaymentByReservaIdResource(Resource):
    @token_required
    def get(current_user, self, reserva_id):
        """
        Listar pagos por reserva
        ---
        tags:
          - Payments
        security:
          - Bearer: []
        parameters:
          - in: path
            name: reserva_id
            type: string
            required: true
        responses:
          200:
            description: Lista de pagos por reserva
          400:
            description: Id invalido
          401:
            description: Token faltante o invalido
        """
        try:
            reserva_uuid = _parse_uuid(reserva_id)
        except ValueError:
            return {"message": "reserva_id invalido"}, 400

        payments = payment_crud.get_all_payments_by_reserva_id(reserva_uuid)
        return [_serialize_payment(payment) for payment in payments], 200

class PaymentByProviderIdResource(Resource):
    @token_required
    def get(current_user, self, provider_id):
        """
        Listar pagos por proveedor
        ---
        tags:
          - Payments
        security:
          - Bearer: []
        parameters:
          - in: path
            name: provider_id
            type: string
            required: true
        responses:
          200:
            description: Lista de pagos por proveedor
          400:
            description: Id invalido
          401:
            description: Token faltante o invalido
        """
        try:
            provider_uuid = _parse_uuid(provider_id)
        except ValueError:
            return {"message": "provider_id invalido"}, 400

        payments = payment_crud.get_all_payments_by_provider_id(provider_uuid)
        return [_serialize_payment(payment) for payment in payments], 200

class PaymentTransactionByIdResource(Resource):
    @token_required
    def get(current_user, self, id):
        """
        Obtener intento de transaccion por id
        ---
        tags:
          - PaymentTransactions
        security:
          - Bearer: []
        parameters:
          - in: path
            name: id
            type: string
            required: true
        responses:
          200:
            description: Intento encontrado
          400:
            description: Id invalido
          401:
            description: Token faltante o invalido
          404:
            description: No encontrado
        """
        try:
            transaction_id = _parse_uuid(id)
        except ValueError:
            return {"message": "transaction_id invalido"}, 400

        transaction = payment_transaction_crud.get_payment_transaction_by_id(transaction_id)
        if not transaction:
            return {"message": "Transaccion no encontrada"}, 404

        return _serialize_payment_transaction(transaction), 200

class PaymentTransactionByPaymentIdResource(Resource):
    @token_required
    def get(current_user, self, payment_id):
        """
        Listar intentos por pago
        ---
        tags:
          - PaymentTransactions
        security:
          - Bearer: []
        parameters:
          - in: path
            name: payment_id
            type: string
            required: true
        responses:
          200:
            description: Lista de intentos por pago
          400:
            description: Id invalido
          401:
            description: Token faltante o invalido
        """
        try:
            payment_uuid = _parse_uuid(payment_id)
        except ValueError:
            return {"message": "payment_id invalido"}, 400

        transactions = payment_transaction_crud.get_all_transactions_by_payment_id(payment_uuid)
        return [_serialize_payment_transaction(tx) for tx in transactions], 200

class SeedDB(Resource):
    def post(self):
        """
        Ejecutar seed para poblar la base de datos
        ---
        tags:
          - Seed
        responses:
          200:
            description: Seed ejecutado correctamente
          500:
            description: Error al ejecutar el seed
        """
        result = SeedHelper.reset_and_seed()

        if not result.get("ok"):
            return {"msg": "Error al ejecutar el seed", "error": result.get("error")}, 500

        return {
            "msg": "Seed ejecutado correctamente",
            "Proveedores procesados": result["payment_providers_procesados"],
        }, 200
