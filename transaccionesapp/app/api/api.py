from decimal import Decimal
from uuid import UUID

from flask import request
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
    # @token_required
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
        
        #aqui va el codigo para hacer la solicitud de pago al proveedor http,
        #el proveedor debe retornar un provider_payment_id y una url (si aplica)
        #para redirigir al usuario a completar el pago
        #Si la solicitud al proveedor falla, se almacena el pago con status "failed" y url null,
        #y se puede retornar un error 400 con un mensaje indicando que no fue posible crear el pago
        #Si la solicitud al proveedor es exitosa, se almacena el pago con el provider_payment_id y la url
        #con estado "pending" y se retorna el pago creado con un status 201

        payment = payment_crud.create_payment(payload)
        if not payment:
            return {"message": "No fue posible crear el pago"}, 400

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
