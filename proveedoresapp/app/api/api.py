from flask_restful import Resource
from flask import request
from uuid import UUID

from app.utils import token_helper
from app.services.manager_crud import ManagerCrud
from app.services.async_user_service import AsyncUserService
from app.utils.seedHelper import SeedHelper
from app.utils.token_helper import token_required, roles_required

manager_crud = ManagerCrud()
async_user_service = AsyncUserService()


def _serialize_manager(manager):
    return {
        "id": str(manager.id),
        "provider_id": str(manager.provider_id) if manager.provider_id else None,
        "userId": str(manager.userId) if manager.userId else None,
        "email": manager.email,
        "first_name": manager.first_name,
        "last_name": manager.last_name,
        "phone": manager.phone,
        "created_at": manager.created_at.isoformat() if hasattr(manager.created_at, "isoformat") else manager.created_at,
        "updated_at": manager.updated_at.isoformat() if hasattr(manager.updated_at, "isoformat") else manager.updated_at,
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
        return {'status': 'healthy'}, 200

class ManagerResource(Resource):
    def post(self):
        """
        Crear provider y manager con usuario en autenticadorapp
        ---
        tags:
          - Managers
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              required: [name, DocumentNumber, manager]
              properties:
                name:
                  type: string
                  example: Hotel Las Colinas
                DocumentNumber:
                  type: string
                  example: 900123456
                currency:
                  type: string
                  example: COP
                status:
                  type: string
                  example: pending
                description:
                  type: string
                provider_payment_id:
                  type: string
                  nullable: true
                url:
                  type: string
                  nullable: true
                manager:
                  type: object
                  required: [first_name, last_name, email, password]
                  properties:
                    first_name:
                      type: string
                    last_name:
                      type: string
                    email:
                      type: string
                      format: email
                    phone:
                      type: string
                    password:
                      type: string
                      minLength: 8
                address:
                  type: object
                  properties:
                    line1:
                      type: string
                    line2:
                      type: string
                      nullable: true
                    city:
                      type: string
                    state:
                      type: string
                    country:
                      type: string
                    countryCode:
                      type: string
                    postal_code:
                      type: string
        security:
          - Bearer: []
        responses:
          201:
            description: Provider, manager y usuario creados exitosamente
            schema:
              type: object
              properties:
                provider:
                  type: object
                manager:
                  type: object
                user:
                  type: object
                  properties:
                    id:
                      type: string
                    username:
                      type: string
                    email:
                      type: string
          400:
            description: Datos inválidos o faltantes
          409:
            description: Email duplicado en el sistema de autenticación
          500:
            description: Error al conectar con autenticadorapp
        """
        payload = request.get_json() or {}
        manager_data = payload.get("manager") or {}
        address_data = payload.get("address") or {}

        # Validar datos requeridos para Provider y su Manager
        required_fields = ["name", "DocumentNumber", "manager"]
        missing_fields = [field for field in required_fields if not payload.get(field)]

        manager_required_fields = ["first_name", "last_name", "email", "password"]
        missing_manager_fields = [
          field for field in manager_required_fields if not manager_data.get(field)
        ]

        if missing_manager_fields:
          return {
            "message": f"Faltan campos requeridos en manager: {', '.join(missing_manager_fields)}"
          }, 400

        if missing_fields:
            return {
                "message": f"Faltan campos requeridos: {', '.join(missing_fields)}"
            }, 400

        # Validar datos del usuario
        is_valid, validation_error = AsyncUserService.validate_user_creation_data(
          email=manager_data.get("email"),
          password=manager_data.get("password"),
          first_name=manager_data.get("first_name"),
          last_name=manager_data.get("last_name")
        )

        if not is_valid:
            return {"message": validation_error}, 400

        # Crear usuario en autenticadorapp de forma asincrónica
        user_data, user_error = AsyncUserService.create_user_in_auth_service(
          email=manager_data.get("email"),
          password=manager_data.get("password"),
          first_name=manager_data.get("first_name"),
          last_name=manager_data.get("last_name"),
          role="Manager"
        )

        if user_error:
            # Retornar error del servicio de autenticación
          is_conflict = "duplicado" in user_error.lower() or "registrado" in user_error.lower()
          return {"message": user_error}, 409 if is_conflict else 500

        # Si la creación del usuario fue exitosa, crear Provider + Manager
        manager_payload = {
          "name": payload.get("name"),
          "DocumentNumber": payload.get("DocumentNumber"),
          "status": payload.get("status", "pending"),
          "userId": user_data["id"],
          "email": manager_data.get("email") or user_data.get("email"),
          "first_name": manager_data.get("first_name"),
          "last_name": manager_data.get("last_name"),
          "phone": manager_data.get("phone"),
          "address": address_data,
        }

        created = manager_crud.create_manager(manager_payload)

        if not created:
            return {
            "message": "Error creating provider and manager"
            }, 409

        provider, manager = created

        return {
          "message": "Provider, manager y dirección creados exitosamente",
          "provider": {
            "id": str(provider.id),
            "name": provider.Name,
            "DocumentNumber": provider.DocumentNumber,
            "status": provider.ProviderStatus.name if provider.ProviderStatus else None,
            "currency": payload.get("currency"),
            "description": payload.get("description"),
            "provider_payment_id": payload.get("provider_payment_id"),
            "url": payload.get("url"),
            "created_at": provider.created_at.isoformat() if hasattr(provider.created_at, "isoformat") else provider.created_at,
            "updated_at": provider.updated_at.isoformat() if hasattr(provider.updated_at, "isoformat") else provider.updated_at,
          },
            "manager": _serialize_manager(manager),
            "address": address_data if address_data else None,
            "user": user_data
        }, 201

class ManagerResourceById(Resource):
    @token_required
    def get(current_user, self, id):
        """
        Obtener Manager por ID
        ---
        tags:
          - Managers
        parameters:
          - in: path
            name: id
            required: true
            type: string
            format: uuid
        security:
          - Bearer: []
        responses:
          200:
            description: Manager encontrado
          404:
            description: Manager no encontrado
        """
        manager = manager_crud.get_manager_by_id(UUID(id))

        if not manager:
            return {"message": "Manager not found"}, 404

        return _serialize_manager(manager), 200

    @token_required
    @roles_required("Admin")
    def put(current_user, self, id):
        """
        Actualizar manager
        ---
        tags:
          - Managers
        parameters:
          - in: path
            name: id
            required: true
            type: string
            format: uuid
          - in: body
            name: body
            required: true
            schema:
              type: object
              properties:
                first_name:
                  type: string
                last_name:
                  type: string
                email:
                  type: string
                  format: email
        security:
          - Bearer: []
        responses:
          200:
            description: manager actualizado
          400:
            description: Error al actualizar
        """
        data = request.get_json()

        manager = manager_crud.update_manager(UUID(id), data)

        if not manager:
            return {"message": "Error updating manager"}, 400

        return {"message": "Manager updated"}, 200

    @token_required
    @roles_required("Admin")
    def delete(current_user, self, id):
        """
        Eliminar manager
        ---
        tags:
          - Managers
        parameters:
          - in: path
            name: id
            required: true  
            type: string
            format: uuid
        security:
          - Bearer: []
        responses:
          200:
            description: manager eliminado
          404:
            description: manager no encontrado
        """
        success = manager_crud.delete_manager(UUID(id))

        if not success:
            return {"message": "Manager not found"}, 404

        return {"message": "Manager deleted"}, 200

class ManagerByProviderResource(Resource):
    @token_required
    def get(current_user, self, id):
        """
        Obtener managers por provider_id
        ---
        tags:
          - ManagersByProvider
        parameters:
          - in: path
            name: id
            required: true
            type: string
            format: uuid
        security:
          - Bearer: []
        responses:
          200:
            description: managers encontrados
          404:
            description: managers no encontrados
        """
        managers = manager_crud.get_all_managers_by_provider_id(UUID(id))

        if not managers:
            return {"message": "Managers no encontrados"}, 404

        return {
            "managers": [
                {
                    "id": str(manager.id),
                    "provider_id": str(manager.provider_id),
                    "userId": str(manager.userId),
                    "email": manager.email,
                    "first_name": manager.first_name,
                    "last_name": manager.last_name,
                    "phone": manager.phone,
                    "created_at": manager.created_at.isoformat() if hasattr(manager.created_at, "isoformat") else manager.created_at,
                }
                for manager in managers
            ]
        }, 200

class ManagerByUserIdResource(Resource):
    @token_required
    def get(current_user, self, id):
        """
        Obtener manager por userId
        ---
        tags:
          - ManagerByUserId 
        parameters:
          - in: path
            name: id
            required: true
            type: string
            format: uuid
        security:
          - Bearer: []
        responses:
          200:
            description: manager encontrado
          404:
            description: manager no encontrado
        """
        manager = manager_crud.get_manager_by_userid(UUID(id))

        if not manager:
            return {"message": "Manager not found"}, 404

        return _serialize_manager(manager), 200

class SeedDB(Resource):
    def post(self):
        """
        Ejecutar seed para poblar la base de datos
        ---
        tags:
          - Seed
        security:
          - Bearer: []
        responses:
          200:
            description: Seed ejecutado correctamente
          500:
            description: Error al ejecutar el seed
        """
        result = SeedHelper.reset_and_seed()

        if not result.get('ok'):
            return {'msg': 'Error al ejecutar el seed', 'error': result.get('error')}, 500

        return {
            'msg': 'Seed ejecutado correctamente',
            'Managers procesados': result['managers_procesados']
        }, 200
