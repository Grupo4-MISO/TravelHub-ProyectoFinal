from app.services.user_crud import UserCrud
from app.db.models import User
from werkzeug.security import check_password_hash, generate_password_hash

class SeedHelper:
    @staticmethod
    def create_default_users():

        User.query.delete()  # Elimina todos los usuarios existentes

        user_crud = UserCrud()

        default_users = [
            {
                "username": "Hotel Las Colinas Manizales",
                "email": "alojamiento_prueba@gmail.com",
                "password_hash": generate_password_hash("alojamiento"),
                "first_name": "Nombre del Admin",
                "last_name": "Apellido del Admin",
                "role": "ACCOMODATION",
                "is_active": True,
                "is_verified": True
            },
            {
                "username": "Maria Garcia",
                "email": "usuario_prueba@gmail.com",
                "password_hash": generate_password_hash("usuario"),
                "first_name": "Maria",
                "last_name": "Garcia",
                "role": "TRAVELER",
                "is_active": True,
                "is_verified": True
            }]
        
        for user in default_users:
            user_crud.create_user(user)