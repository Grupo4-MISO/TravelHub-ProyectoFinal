from flask_restful import Resource
from flask import request, current_app
from uuid import UUID
import jwt
from datetime import datetime, timedelta, timezone

from app.utils import token_helper
from app.services.comment_crud import ReviewCrud
from app.utils.seedHelper import SeedHelper
from app.utils.token_helper import token_required, roles_required

comment_crud = ReviewCrud()

def _serialize_review(review):
  return {
    "id": str(review.id),
    "hospedajeId": str(review.hospedajeId),
    "userName": review.userName,
    "userId": str(review.userId),
    "rating": review.rating,
    "comment": review.comment,
    "created_at": review.created_at.isoformat() if hasattr(review.created_at, "isoformat") else review.created_at,
    "updated_at": review.updated_at.isoformat() if hasattr(review.updated_at, "isoformat") else review.updated_at,
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

class ReviewResource(Resource):
    @token_required
    def post(current_user, self):
        """
        Crear Reviews
        ---
        tags:
          - Reviews
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              required: [hospedajeId, comment, rating]
              properties:
                hospedajeId:
                  type: string
                  format: uuid
                comment:
                  type: string
                rating:
                  type: number
                  minimum: 1
                  maximum: 5
        security:
          - Bearer: []
        responses:
          201:
            description: Commentario creado
          400:
            description: Datos inválidos
        """
        payload = request.get_json()
        userId = token_helper.get_userId_from_token()
        userName = token_helper.get_userName_from_token()
        
        payload["userName"] = userName
        payload["userId"] = userId

        review = comment_crud.create_review(payload)

        if not review:
            return {"message": "Error creating review (duplicate?)"}, 409

        return _serialize_review(review), 201


class ReviewResourceById(Resource):
    @token_required
    def get(current_user, self, id):
        """
        Obtener Review por ID
        ---
        tags:
          - Reviews
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
            description: Review encontrado
          404:
            description: Review no encontrado
        """
        review = comment_crud.get_review_by_id(UUID(id))

        if not review:
            return {"message": "Review not found"}, 404

        return _serialize_review(review), 200

    @token_required
    @roles_required("Administrator")
    def put(current_user, self, id):
        """
        Actualizar review
        ---
        tags:
          - Reviews
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
                comment:
                  type: string
                rating:
                  type: number
                  minimum: 1
                  maximum: 5
        security:
          - Bearer: []
        responses:
          200:
            description: Comentario actualizado
          400:
            description: Error al actualizar
        """
        data = request.get_json()

        review = comment_crud.update_review(UUID(id), data)

        if not review:
            return {"message": "Error updating comment"}, 400

        return {"message": "Comment updated"}, 200

    @token_required
    @roles_required("Administrator")
    def delete(current_user, self, id):
        """
        Eliminar comentario
        ---
        tags:
          - Reviews
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
            description: Comentario eliminado
          404:
            description: Comentario no encontrado
        """
        success = comment_crud.delete_review(UUID(id))

        if not success:
            return {"message": "Comment not found"}, 404

        return {"message": "Comment deleted"}, 200

class ReviewByHospedajeResource(Resource):
  def get(self, id):
        """
        Obtener reviews por ID de hospedaje
        ---
        tags:
          - ReviewsByHospedaje
        parameters:
          - in: path
            name: id
            required: true
            type: string
            format: uuid
        responses:
          200:
            description: Reviews encontrados
          404:
            description: Reviews no encontrados
        """
        reviews = comment_crud.get_all_reviews_by_hospedaje_id(UUID(id))

        if not reviews:
          return {"message": "Commentarios no encontrados"}, 404

        return [
          {
            "id": str(review.id),
            "hospedajeId": str(review.hospedajeId),
            "userName": review.userName,
            "userId": str(review.userId),
            "comment": review.comment,
            "rating": review.rating,
          }
          for review in reviews
        ], 200

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
            'Comentarios insertados': result['reviews_insertados'],
            'Hospedajes procesados': result['hospedajes_procesados']
        }, 200
