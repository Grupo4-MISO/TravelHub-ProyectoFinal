from app.db.models import UserRole, db, User
from werkzeug.security import generate_password_hash
import uuid

# ---------------------------------------------------------------------------
# Datos de cuentas para autenticación base
# ---------------------------------------------------------------------------
AUTH_SEED = [
    {
        "id": uuid.UUID("f3647319-0202-4b9c-93fb-307c2bb54fd2"),
        "email": "d.andrades@uniandes.edu.co",
        "password": "12345",
        "first_name": "Daniel",
        "last_name": "Andrade",
        "is_active": True,
        "is_verified": True,
        "role": UserRole.ADMIN,
    },
    {
        "id": uuid.UUID("b17d0e07-03b9-41b5-a834-ad32e19501bd"),
        "email": "n.fajardo@uniandes.edu.co",
        "password": "12345",
        "first_name": "Neider",
        "last_name": "Fajardo",
        "is_active": True,
        "is_verified": True,
        "role": UserRole.ADMIN,
    },
    {
        "id": uuid.UUID("92665e0f-d1b8-4d95-b539-31e1f7988685"),
        "email": "jc.morag12@uniandes.edu.co",
        "password": "12345",
        "first_name": "Juan Camilo",
        "last_name": "Mora",
        "is_active": True,
        "is_verified": True,
        "role": UserRole.ADMIN,
    },
    {
        "id": uuid.UUID("16c34994-d6ad-44c0-9f09-ccbbdf60194d"),
        "email": "d.oicata@uniandes.edu.co",
        "password": "12345",
        "first_name": "Daniel",
        "last_name": "Oicata",
        "is_active": True,
        "is_verified": True,
        "role": UserRole.ADMIN,
    },
        {
        "id": uuid.UUID("9a4a97e8-7f0e-46fb-a451-d7de8ef19ba5"),
        "email": "carla.gomez@yopmail.com",
        "password": "12345",
        "first_name": "Carla",
        "last_name": "Gomez",
        "is_active": True,
        "is_verified": True,
        "role": UserRole.MANAGER,
    },
    {
        "id": uuid.UUID("7f93f279-130f-4231-9458-b976925d40eb"),
        "email": "diego.vargas@yopmail.com",
        "password": "12345",
        "first_name": "Diego",
        "last_name": "Vargas",
        "is_active": True,
        "is_verified": True,
        "role": UserRole.MANAGER,
    },
    {
        "id": uuid.UUID("ed4be7ea-b9f0-42b7-97fc-4808d359ba70"),
        "email": "ana.lopez@yopmail.com",
        "password": "12345",
        "first_name": "Ana",
        "last_name": "Lopez",
        "is_active": True,
        "is_verified": True,
        "role": UserRole.TRAVELER,
    },
    {
        "id": uuid.UUID("f12f3c5d-da80-4a54-b9d8-f6b1a3cb272a"),
        "email": "luis.martinez@yopmail.com",
        "password": "12345",
        "first_name": "Luis",
        "last_name": "Martinez",
        "is_active": True,
        "is_verified": True,
        "role": UserRole.TRAVELER,
    },
    {
        "id": uuid.UUID("a1aaf0dc-36b6-422d-87fe-3c04173c88ef"),
        "email": "sofia.ruiz@yopmail.com",
        "password": "12345",
        "first_name": "Sofia",
        "last_name": "Ruiz",
        "is_active": True,
        "is_verified": True,
        "role": UserRole.TRAVELER,
    },
    {
        "id": uuid.UUID("8a6f2b3c-1d4e-4a8d-9c1f-4bb3f6d7a101"),
        "email": "camila.hernandez@yopmail.com",
        "password": "12345",
        "first_name": "Camila",
        "last_name": "Hernandez",
        "is_active": True,
        "is_verified": True,
        "role": UserRole.TRAVELER,
    },
    {
        "id": uuid.UUID("c1e4d5f6-2a3b-4c4d-8e9f-5a6b7c8d9e10"),
        "email": "juan.perez@yopmail.com",
        "password": "12345",
        "first_name": "Juan",
        "last_name": "Perez",
        "is_active": True,
        "is_verified": True,
        "role": UserRole.TRAVELER,
    },
    {
        "id": uuid.UUID("d2f3a4b5-6c7d-4e8f-9a10-1b2c3d4e5f60"),
        "email": "valentina.mora@yopmail.com",
        "password": "12345",
        "first_name": "Valentina",
        "last_name": "Mora",
        "is_active": True,
        "is_verified": True,
        "role": UserRole.TRAVELER,
    },
    {
        "id": uuid.UUID("e3a4b5c6-7d8e-4f90-9a11-2c3d4e5f6071"),
        "email": "santiago.lopez@yopmail.com",
        "password": "12345",
        "first_name": "Santiago",
        "last_name": "Lopez",
        "is_active": True,
        "is_verified": True,
        "role": UserRole.TRAVELER,
    },
    {
        "id": uuid.UUID("f4b5c6d7-8e9f-4012-8a13-3d4e5f607182"),
        "email": "daniela.garcia@yopmail.com",
        "password": "12345",
        "first_name": "Daniela",
        "last_name": "Garcia",
        "is_active": True,
        "is_verified": True,
        "role": UserRole.TRAVELER,
    },
    {
        "id": uuid.UUID("a5c6d7e8-9f01-4123-8a14-4e5f60718293"),
        "email": "mateo.suarez@yopmail.com",
        "password": "12345",
        "first_name": "Mateo",
        "last_name": "Suarez",
        "is_active": True,
        "is_verified": True,
        "role": UserRole.TRAVELER,
    },
    {
        "id": uuid.UUID("b6d7e8f9-0a12-4234-8a15-5f60718293a4"),
        "email": "laura.ramirez@yopmail.com",
        "password": "12345",
        "first_name": "Laura",
        "last_name": "Ramirez",
        "is_active": True,
        "is_verified": True,
        "role": UserRole.TRAVELER,
    },
    {
        "id": uuid.UUID("c7e8f90a-1b23-4345-8a16-60718293a4b5"),
        "email": "andres.torres@yopmail.com",
        "password": "12345",
        "first_name": "Andres",
        "last_name": "Torres",
        "is_active": True,
        "is_verified": True,
        "role": UserRole.TRAVELER,
    },
    {
        "id": uuid.UUID("d8f90a1b-2c34-4456-8a17-718293a4b5c6"),
        "email": "paula.castro@yopmail.com",
        "password": "12345",
        "first_name": "Paula",
        "last_name": "Castro",
        "is_active": True,
        "is_verified": True,
        "role": UserRole.TRAVELER,
    },
    {
        "id": uuid.UUID("e90a1b2c-3d45-4567-8a18-8293a4b5c6d7"),
        "email": "sebastian.ortiz@yopmail.com",
        "password": "12345",
        "first_name": "Sebastian",
        "last_name": "Ortiz",
        "is_active": True,
        "is_verified": True,
        "role": UserRole.TRAVELER,
    },
    {
        "id": uuid.UUID("0a1b2c3d-4e56-4678-8a19-93a4b5c6d7e8"),
        "email": "juliana.vargas@yopmail.com",
        "password": "12345",
        "first_name": "Juliana",
        "last_name": "Vargas",
        "is_active": True,
        "is_verified": True,
        "role": UserRole.TRAVELER,
    },
    {
        "id": uuid.UUID("1b2c3d4e-5f67-4789-8a1a-a4b5c6d7e8f9"),
        "email": "diego.gomez@yopmail.com",
        "password": "12345",
        "first_name": "Diego",
        "last_name": "Gomez",
        "is_active": True,
        "is_verified": True,
        "role": UserRole.TRAVELER,
    },
    {
        "id": uuid.UUID("2c3d4e5f-6071-4890-8a1b-b5c6d7e8f90a"),
        "email": "natalia.reyes@yopmail.com",
        "password": "12345",
        "first_name": "Natalia",
        "last_name": "Reyes",
        "is_active": True,
        "is_verified": True,
        "role": UserRole.TRAVELER,
    },
    {
        "id": uuid.UUID("3d4e5f60-7182-4901-8a1c-c6d7e8f90a1b"),
        "email": "felipe.marin@yopmail.com",
        "password": "12345",
        "first_name": "Felipe",
        "last_name": "Marin",
        "is_active": True,
        "is_verified": True,
        "role": UserRole.TRAVELER,
    },
    {
        "id": uuid.UUID("4e5f6071-8293-4a12-8a1d-d7e8f90a1b2c"),
        "email": "maria.fernandez@yopmail.com",
        "password": "12345",
        "first_name": "Maria",
        "last_name": "Fernandez",
        "is_active": True,
        "is_verified": True,
        "role": UserRole.TRAVELER,
    },
    {
        "id": uuid.UUID("5f607182-93a4-4b23-8a1e-e8f90a1b2c3d"),
        "email": "camilo.rojas@yopmail.com",
        "password": "12345",
        "first_name": "Camilo",
        "last_name": "Rojas",
        "is_active": True,
        "is_verified": True,
        "role": UserRole.TRAVELER,
    },
    {
        "id": uuid.UUID("60718293-a4b5-4c34-8a1f-f90a1b2c3d4e"),
        "email": "isabella.cortes@yopmail.com",
        "password": "12345",
        "first_name": "Isabella",
        "last_name": "Cortes",
        "is_active": True,
        "is_verified": True,
        "role": UserRole.TRAVELER,
    }
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
                    role=data.get("role")
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
