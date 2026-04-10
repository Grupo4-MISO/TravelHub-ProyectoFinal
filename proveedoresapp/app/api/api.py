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
    "hospedajeId": str(manager.hospedajeId) if manager.hospedajeId else None,
    "userId": str(manager.userId),
    "userName": manager.userName,
    "email": manager.email,
    "first_name": manager.first_name,
    "last_name": manager.last_name,
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
        Crear manager con usuario en autenticadorapp
        ---
        tags:
          - Managers
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              required: [first_name, last_name, email, password]
              properties:
                hospedajeId:
                  type: string
                  format: uuid
                  nullable: true
                password:
                  type: string
                  minLength: 8
                first_name:
                  type: string
                  example: Juan
                last_name:
                  type: string
                  example: Pérez
                email:
                  type: string
                  format: email
                  example: juan.perez@example.com
        security:
          - Bearer: []
        responses:
          201:
            description: Manager y usuario creados exitosamente
            schema:
              type: object
              properties:
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
        payload = request.get_json()
        
        # Validar datos requeridos
        required_fields = ["first_name", "last_name", "email", "password"]
        missing_fields = [field for field in required_fields if not payload.get(field)]
        
        if missing_fields:
            return {
                "message": f"Faltan campos requeridos: {', '.join(missing_fields)}"
            }, 400
        
        # Validar datos del usuario
        is_valid, validation_error = AsyncUserService.validate_user_creation_data(
            email=payload.get("email"),
          password=payload.get("password"),
            first_name=payload.get("first_name"),
            last_name=payload.get("last_name")
        )
        
        if not is_valid:
            return {"message": validation_error}, 400
        
        # Crear usuario en autenticadorapp de forma asincrónica
        user_data, user_error = AsyncUserService.create_user_in_auth_service(
            email=payload.get("email"),
          password=payload.get("password"),
            first_name=payload.get("first_name"),
            last_name=payload.get("last_name"),
            role="Manager"
        )
        
        if user_error:
            # Retornar error del servicio de autenticación
            return {"message": user_error}, 409 if "duplicado" in user_error.lower() else 500
        
        # Si la creación del usuario fue exitosa, crear el Manager
        manager_payload = {
            "hospedajeId": payload.get("hospedajeId"),
            "userId": user_data["id"],
            "userName": user_data["username"],
            "email": user_data["email"],
            "first_name": payload.get("first_name"),
            "last_name": payload.get("last_name")
        }
        
        manager = manager_crud.create_manager(manager_payload)
        
        if not manager:
            return {
                "message": "Error creating manager (duplicate email in providers?)"
            }, 409
        
        return {
            "message": "Manager y usuario creados exitosamente",
            "manager": _serialize_manager(manager),
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
    @roles_required("Administrator")
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
    @roles_required("Administrator")
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

class ManagerByHospedajeResource(Resource):
    @token_required
    def get(current_user, self, id):
        """
        Obtener managers por ID de hospedaje
        ---
        tags:
          - ManagersByHospedaje
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
        managers = manager_crud.get_all_managers_by_hospedaje_id(UUID(id))

        if not managers:
            return {"message": "Managers no encontrados"}, 404

        return {
            "managers": [
                {
                    "id": str(manager.id),
                    "hospedajeId": str(manager.hospedajeId),
                    "userName": manager.userName,
                    "userId": str(manager.userId),
                    "email": manager.email,
                    "first_name": manager.first_name,
                    "last_name": manager.last_name,
                    "created_at": manager.created_at.isoformat() if hasattr(manager.created_at, "isoformat") else manager.created_at,
                }
                for manager in managers
            ]
        }, 200

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
