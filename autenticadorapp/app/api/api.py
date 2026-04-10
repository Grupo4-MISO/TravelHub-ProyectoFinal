from flask_restful import Resource
from flask import request, current_app
from uuid import UUID
from werkzeug.security import check_password_hash, generate_password_hash
from app.db.models import UserRole
import jwt
from datetime import datetime, timedelta, timezone

from app.services.user_crud import UserCrud
from app.utils.token_helper import token_required, roles_required
from app.utils.seedHelper import SeedHelper

user_crud = UserCrud()

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
    
class Login(Resource):
    def post(self):
        """
        Login de usuario
        ---
        tags:
          - Auth
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              required: [email, password]
              properties:
                email:
                  type: string
                  example: admin@travelhub.com
                password:
                  type: string
                  example: secret123
        responses:
          200:
            description: Login exitoso
          400:
            description: Credenciales incompletas
          401:
            description: Credenciales inválidas
          500:
            description: JWT secret key is not configured correctly
        """
        data = request.get_json()
        if not data or not data.get("email") or not data.get("password"):
            return {"message": "Missing credentials"}, 400

        user = user_crud.get_user_by_email(data.get("email"))

        if not user:
            return {"message": "Invalid credentials"}, 401

        if not check_password_hash(user.password_hash, data.get("password")):
            return {"message": "Invalid credentials"}, 401

        jwt_secret = current_app.config.get("JWT_SECRET_KEY")
        if not isinstance(jwt_secret, str) or not jwt_secret.strip():
            return {"message": "JWT secret key is not configured correctly"}, 500

        exp_seconds = int(current_app.config.get("JWT_ACCESS_TOKEN_EXPIRES", 3600))
        token_payload = {
            "sub": str(user.id),
            "username": user.username,
            "role": user.role.value,
            "exp": datetime.now(timezone.utc) + timedelta(seconds=exp_seconds),
        }

        token = jwt.encode(token_payload, jwt_secret, algorithm="HS256")

        return {
            "token": token,
            "user": {
                "id": str(user.id),
                "username": user.username,
                "role": user.role.value
            }
        }, 200

class UserCollectionResource(Resource):
    def post(self):
        """
        Crear usuario
        ---
        tags:
          - Users
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              required: [email, password, role]
              properties:
                email:
                  type: string
                password:
                  type: string
                role:
                  type: string
                  example: Traveler
        responses:
          201:
            description: Usuario creado
          400:
            description: Datos inválidos
          409:
            description: Usuario duplicado
        """
        data = request.get_json()

        if not data or not data.get("password"):
            return {"message": "Missing password"}, 400

        payload = dict(data)
        payload.pop("password_hash", None)  # no confiar en hash enviado por cliente

        if not payload.get("role"):
            return {"message": "Missing role"}, 400

        try:
            payload["role"] = UserRole(payload["role"])
            payload["username"] = payload["email"].split("@")[0]
        except ValueError as exc:
            return {
                "message": f"Invalid role '{payload.get('role')}'. Allowed roles: {[r.value for r in UserRole]}",
                "error": str(exc)
            }, 400

        payload["password_hash"] = generate_password_hash(payload.pop("password"))

        user = user_crud.create_user(payload)

        if not user:
            return {"message": "Error creating user (duplicate?)"}, 409

        return {
            "id": str(user.id),
            "username": user.username,
            "email": user.email
        }, 201

class UserDetailResource(Resource):
    @token_required
    def get(current_user, self, user_id):
        """
        Obtener usuario por ID
        ---
        tags:
          - Users
        parameters:
          - in: path
            name: user_id
            required: true
            type: string
            format: uuid
        security:
          - Bearer: []
        responses:
          200:
            description: Usuario encontrado
          404:
            description: Usuario no encontrado
        """
        user = user_crud.get_user_by_id(UUID(user_id))

        if not user:
            return {"message": "User not found"}, 404

        return {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": user.role.value
        }, 200

    @token_required
    @roles_required("Administrator", "Manager")
    def put(current_user, self, user_id):
        """
        Actualizar usuario
        ---
        tags:
          - Users
        parameters:
          - in: path
            name: user_id
            required: true
            type: string
            format: uuid
          - in: body
            name: body
            required: true
            schema:
              type: object
              properties:
                username:
                  type: string
                email:
                  type: string
                role:
                  type: string
        security:
          - Bearer: []
        responses:
          200:
            description: Usuario actualizado
          400:
            description: Error al actualizar
        """
        data = request.get_json()

        user = user_crud.update_user(UUID(user_id), data)

        if not user:
            return {"message": "Error updating user"}, 400

        return {"message": "User updated"}, 200

    @token_required
    @roles_required("Administrator")
    def delete(current_user, self, user_id):
        """
        Eliminar usuario
        ---
        tags:
          - Users
        parameters:
          - in: path
            name: user_id
            required: true
            type: string
            format: uuid
        security:
          - Bearer: []
        responses:
          200:
            description: Usuario eliminado
          404:
            description: Usuario no encontrado
        """
        success = user_crud.delete_user(UUID(user_id))

        if not success:
            return {"message": "User not found"}, 404

        return {"message": "User deleted"}, 200


class SeedDB(Resource):
    def post(self):
        """
        Ejecutar seed para poblar la base de datos
        ---
        tags:
          - Users
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
            'Usuarios insertados': result['users_insertados'],
        }, 200