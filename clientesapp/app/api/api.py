from flask_restful import Resource
from flask import request
from uuid import UUID

from app.utils import token_helper
from app.services.traveler_crud import TravelerCrud
from app.services.async_user_service import AsyncUserService
from app.utils.seedHelper import SeedHelper
from app.utils.token_helper import token_required, roles_required

traveler_crud = TravelerCrud()
async_user_service = AsyncUserService()
TRAVELER_UPDATABLE_FIELDS = {"documentNumber", "first_name", "last_name", "phone", "gender"}


def _serialize_traveler(traveler):
    return {
        "id": str(traveler.id),
        "documentNumber": getattr(traveler, "documentNumber", getattr(traveler, "DocumentNumber", None)),
        "userId": str(traveler.userId) if traveler.userId else None,
        "first_name": traveler.first_name,
        "last_name": traveler.last_name,
        "phone": traveler.phone,
        "gender": traveler.gender,
        "photo": traveler.photo,
        "email": traveler.email,
        "travelerStatus": traveler.travelerStatus.name if traveler.travelerStatus else None,
        "created_at": traveler.created_at.isoformat() if hasattr(traveler.created_at, "isoformat") else traveler.created_at,
        "updated_at": traveler.updated_at.isoformat() if hasattr(traveler.updated_at, "isoformat") else traveler.updated_at,
    }


def _serialize_traveler_address(address):
    return {
        "id": str(address.id),
        "traveler_id": str(address.traveler_id),
        "line1": address.line1,
        "line2": address.line2,
        "city": address.city,
        "state": address.state,
        "country": address.country,
        "countryCode": address.countryCode,
        "postal_code": address.postal_code,
        "created_at": address.created_at.isoformat() if hasattr(address.created_at, "isoformat") else address.created_at,
        "updated_at": address.updated_at.isoformat() if hasattr(address.updated_at, "isoformat") else address.updated_at,
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

class TravelerResource(Resource):
    def post(self):
        """
        Crear Traveler con usuario en autenticadorapp
        ---
        tags:
          - Travelers
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              required: [traveler]
              properties:
                traveler:
                  type: object
                  required: [documentNumber, first_name, last_name, email, password]
                  properties:
                    documentNumber:
                      type: string
                      example: 900123456
                    first_name:
                      type: string
                    last_name:
                      type: string
                    email:
                      type: string
                      format: email
                    phone:
                      type: string
                    gender:
                      type: string
                      example: Female
                    photo:
                      type: string
                    password:
                      type: string
                      minLength: 8
                    travelerStatus:
                      type: string
                      example: Pending
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
            description: Traveler y usuario creados exitosamente
            schema:
              type: object
              properties:
                Traveler:
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
        Traveler_data = payload.get("traveler") or {}
        address_data = payload.get("address") or {}
        document_number = Traveler_data.get("documentNumber") or Traveler_data.get("DocumentNumber")

        # Validar datos requeridos para Traveler
        required_fields = ["traveler"]
        missing_fields = [field for field in required_fields if not payload.get(field)]

        Traveler_required_fields = ["documentNumber", "first_name", "last_name", "email", "password"]
        missing_Traveler_fields = [
          field for field in Traveler_required_fields if not Traveler_data.get(field)
        ]

        if missing_Traveler_fields:
          return {
            "message": f"Faltan campos requeridos en Traveler: {', '.join(missing_Traveler_fields)}"
          }, 400

        if missing_fields:
            return {
                "message": f"Faltan campos requeridos: {', '.join(missing_fields)}"
            }, 400

        if not document_number:
          return {
            "message": "Falta el campo requerido documentNumber en Traveler"
          }, 400

        # Validar datos del usuario
        is_valid, validation_error = AsyncUserService.validate_user_creation_data(
          email=Traveler_data.get("email"),
          password=Traveler_data.get("password"),
          first_name=Traveler_data.get("first_name"),
          last_name=Traveler_data.get("last_name")
        )

        if not is_valid:
            return {"message": validation_error}, 400

        # Crear usuario en autenticadorapp de forma asincrónica
        user_data, user_error = AsyncUserService.create_user_in_auth_service(
          email=Traveler_data.get("email"),
          password=Traveler_data.get("password"),
          first_name=Traveler_data.get("first_name"),
          last_name=Traveler_data.get("last_name"),
          role="Traveler"
        )

        if user_error:
          # Retornar error del servicio de autenticación
          is_conflict = "duplicado" in user_error.lower() or "registrado" in user_error.lower()
          return {"message": user_error}, 409 if is_conflict else 500

        # Si la creación del usuario fue exitosa, crear Traveler
        Traveler_payload = {
          "name": payload.get("name"),
          "documentNumber": document_number,
          "travelerStatus": Traveler_data.get("travelerStatus", "Pending"),
          "userId": user_data["id"],
          "email": Traveler_data.get("email") or user_data.get("email"),
          "first_name": Traveler_data.get("first_name"),
          "last_name": Traveler_data.get("last_name"),
          "phone": Traveler_data.get("phone"),
          "gender": Traveler_data.get("gender"),
          "photo": Traveler_data.get("photo"),
          "address": address_data,
        }

        created = traveler_crud.create_traveler(Traveler_payload)

        if not created:
            return {
            "message": "Error creating Traveler"
            }, 409

        Traveler = created

        return {
          "message": "Traveler y dirección creados exitosamente",
            "Traveler": _serialize_traveler(Traveler),
            "address": address_data if address_data else None,
            "user": user_data
        }, 201

class TravelerResourceById(Resource):
    @token_required
    def get(current_user, self, id):
        """
        Obtener Traveler por ID
        ---
        tags:
          - Travelers
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
            description: Traveler encontrado
          404:
            description: Traveler no encontrado
        """
        Traveler = traveler_crud.get_traveler_by_id(UUID(id))

        if not Traveler:
            return {"message": "Traveler not found"}, 404

        return _serialize_traveler(Traveler), 200

    @token_required
    @roles_required("Admin", "Traveler")
    def put(current_user, self, id):
        """
        Actualizar Traveler
        ---
        tags:
          - Travelers
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
                documentNumber:
                  type: string
                first_name:
                  type: string
                last_name:
                  type: string
                phone:
                  type: string
                gender:
                  type: string
              additionalProperties: false
        security:
          - Bearer: []
        responses:
          200:
            description: Traveler actualizado
          403:
            description: No autorizado para actualizar este Traveler
          400:
            description: Error al actualizar
        """
        user_role = current_user.get("role")
        token_user_id = current_user.get("sub")
        if user_role == "Traveler":
            traveler = traveler_crud.get_traveler_by_id(UUID(id))
            if not traveler:
                return {"message": "Traveler not found"}, 404
            if str(traveler.userId) != str(token_user_id):
                return {"message": "Unauthorized"}, 403

        data = request.get_json() or {}
        invalid_fields = [key for key in data.keys() if key not in TRAVELER_UPDATABLE_FIELDS]
        if invalid_fields:
            return {
                "message": (
                    "Campos no permitidos para actualización: "
                    f"{', '.join(sorted(invalid_fields))}"
                )
            }, 400

        allowed_data = {key: value for key, value in data.items() if key in TRAVELER_UPDATABLE_FIELDS}

        Traveler = traveler_crud.update_traveler(UUID(id), allowed_data)

        if not Traveler:
            return {"message": "Error updating Traveler"}, 400

        return {"message": "Traveler updated"}, 200

    @token_required
    @roles_required("Admin")
    def delete(current_user, self, id):
        """
        Eliminar Traveler
        ---
        tags:
          - Travelers
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
            description: Traveler eliminado
          404:
            description: Traveler no encontrado
        """
        success = traveler_crud.delete_traveler(UUID(id))

        if not success:
            return {"message": "Traveler not found"}, 404

        return {"message": "Traveler deleted"}, 200

class TravelerByUserIdResource(Resource):
    @token_required
    def get(current_user, self, id):
        """
        Obtener Traveler por userId
        ---
        tags:
          - TravelerByUserId 
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
            description: Traveler encontrado
            schema:
              type: object
              properties:
                id:
                  type: string
                userId:
                  type: string
                first_name:
                  type: string
                last_name:
                  type: string
                addresses:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: string
                      traveler_id:
                        type: string
                      line1:
                        type: string
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
          404:
            description: Traveler no encontrado
        """
        traveler_data = traveler_crud.get_traveler_by_userid(UUID(id))

        if not traveler_data:
            return {"message": "Traveler not found"}, 404

        traveler, addresses = traveler_data
        response = _serialize_traveler(traveler)
        response["addresses"] = [_serialize_traveler_address(address) for address in addresses]

        return response, 200

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

        travelers_processed = result.get('travelers_procesados', result.get('Travelers_procesados', 0))

        return {
            'msg': 'Seed ejecutado correctamente',
          'Travelers procesados': travelers_processed
        }, 200
