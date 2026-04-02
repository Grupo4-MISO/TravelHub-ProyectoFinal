from app.services.user_crud import UserCrud
from werkzeug.security import check_password_hash, generate_password_hash


def create_default_users():
    user_crud = UserCrud()

    default_users = [
        {
            "username": "Hotel el retorno",
            "email": "alojamiento_prueba@gmail.com",
            "password_hash": generate_password_hash("alojamiento"),
            "first_name": "John",
            "last_name": "Doe",
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