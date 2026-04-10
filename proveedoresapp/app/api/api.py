from flask_restful import Resource
from flask import request
from uuid import UUID

from app.utils import token_helper
from app.services.manager_crud import ManagerCrud
from app.utils.seedHelper import SeedHelper
from app.utils.token_helper import token_required, roles_required

manager_crud = ManagerCrud()


def _serialize_manager(manager):
  return {
    "id": str(manager.id),
    "hospedajeId": str(manager.hospedajeId),
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
    @token_required
    def post(current_user, self):
        """
        Crear manager
        ---
        tags:
          - Managers
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              required: [hospedajeId, first_name, last_name, email]
              properties:
                hospedajeId:
                  type: string
                  format: uuid
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
          201:
            description: Manager creado
          400:
            description: Datos inválidos
        """
        payload = request.get_json()
        userId = token_helper.get_userId_from_token()
        userName = token_helper.get_userName_from_token()

        payload["userName"] = userName
        payload["userId"] = userId

        manager = manager_crud.create_manager(payload)

        if not manager:
            return {"message": "Error creating manager (duplicate?)"}, 409

        return _serialize_manager(manager), 201


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
