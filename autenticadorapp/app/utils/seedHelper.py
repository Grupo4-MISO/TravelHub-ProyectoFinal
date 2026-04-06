from app.db.models import UserRole, db, User
from werkzeug.security import generate_password_hash

# ---------------------------------------------------------------------------
# Datos de cuentas para autenticación base
# ---------------------------------------------------------------------------
AUTH_SEED = [
    {
        "email": "d.andrades@uniandes.edu.co",
        "password": "12345",
        "first_name": "Daniel",
        "last_name": "Andrade",
        "is_active": True,
        "is_verified": True,
        "role": UserRole.ADMIN,
    },
    {
        "email": "n.fajardo@uniandes.edu.co",
        "password": "12345",
        "first_name": "Neider",
        "last_name": "Fajardo",
        "is_active": True,
        "is_verified": True,
        "role": UserRole.ADMIN,
    },
    {
        "email": "jc.morag12@uniandes.edu.co",
        "password": "12345",
        "first_name": "Juan Camilo",
        "last_name": "Mora",
        "is_active": True,
        "is_verified": True,
        "role": UserRole.ADMIN,
    },
    {
        "email": "d.oicata@uniandes.edu.co",
        "password": "12345",
        "first_name": "Daniel",
        "last_name": "Oicata",
        "is_active": True,
        "is_verified": True,
        "role": UserRole.ADMIN,
    },
    {
        "email": "traveler.ana@yopmail.com",
        "password": "12345",
        "first_name": "Ana",
        "last_name": "Lopez",
        "is_active": True,
        "is_verified": True,
        "role": UserRole.TRAVELER,
    },
    {
        "email": "traveler.luis@yopmail.com",
        "password": "12345",
        "first_name": "Luis",
        "last_name": "Martinez",
        "is_active": True,
        "is_verified": True,
        "role": UserRole.TRAVELER,
    },
    {
        "email": "traveler.sofia@yopmail.com",
        "password": "12345",
        "first_name": "Sofia",
        "last_name": "Ruiz",
        "is_active": True,
        "is_verified": True,
        "role": UserRole.TRAVELER,
    },
    {
        "email": "manager.carla@yopmail.com",
        "password": "12345",
        "first_name": "Carla",
        "last_name": "Gomez",
        "is_active": True,
        "is_verified": True,
        "role": UserRole.MANAGER,
    },
    {
        "email": "manager.diego@yopmail.com",
        "password": "12345",
        "first_name": "Diego",
        "last_name": "Vargas",
        "is_active": True,
        "is_verified": True,
        "role": UserRole.MANAGER,
    },
]


class SeedHelper:
    """Herramienta para poblar y restablecer las tablas d autenticación y autorización."""

    @staticmethod
    def reset_and_seed():
        """
        Elimina todos los registros existentes de users y user_roles,
        luego inserta los datos de seed definidos en AUTH_SEED.

        Returns:
            dict con el resumen de registros insertados o un mensaje de error.
        """
        try:
            # Primero borramos usuarios por la FK
            User.query.delete()
            db.session.flush()

            users_insertados = 0

            for data in AUTH_SEED:
                user = User(
                    id = data.get("id"),    
                    username=data["email"].split("@")[0],
                    email=data["email"],
                    password_hash=generate_password_hash(data["password"]),
                    first_name=data.get("first_name"),
                    last_name=data.get("last_name"),
                    is_active = data.get("is_active", True),
                    is_verified = data.get("is_verified", True),
                    role=data.get("role", UserRole.TRAVELER)
                )
                db.session.add(user)
                users_insertados += 1

            db.session.commit()

            return {
                "ok": True,
                "users_insertados": users_insertados
            }

        except Exception as e:
            db.session.rollback()
            return {"ok": False, "error": str(e)}
