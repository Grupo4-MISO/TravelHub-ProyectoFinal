from app.db.models import Traveler, TravelerAddress, TravelerDocument, TravelerStatus, db
import uuid
import random

# ---------------------------------------------------------------------------
# Fallback: Usuarios TRAVELER locales 
# ---------------------------------------------------------------------------
TRAVELERS_FALLBACK = [
    {"id": uuid.UUID("ed4be7ea-b9f0-42b7-97fc-4808d359ba70"), "documentNumber": "100000001", "userId": uuid.UUID("ed4be7ea-b9f0-42b7-97fc-4808d359ba70"), "email": "ana.lopez@yopmail.com", "first_name": "Ana", "last_name": "Lopez", "phone": "3000000001", "travelerStatus": TravelerStatus.Active},
    {"id": uuid.UUID("f12f3c5d-da80-4a54-b9d8-f6b1a3cb272a"), "documentNumber": "100000002", "userId": uuid.UUID("f12f3c5d-da80-4a54-b9d8-f6b1a3cb272a"), "email": "luis.martinez@yopmail.com", "first_name": "Luis", "last_name": "Martinez", "phone": "3000000002", "travelerStatus": TravelerStatus.Active},
    {"id": uuid.UUID("a1aaf0dc-36b6-422d-87fe-3c04173c88ef"), "documentNumber": "100000003", "userId": uuid.UUID("a1aaf0dc-36b6-422d-87fe-3c04173c88ef"), "email": "sofia.ruiz@yopmail.com", "first_name": "Sofia", "last_name": "Ruiz", "phone": "3000000003", "travelerStatus": TravelerStatus.Active},
    {"id": uuid.UUID("8a6f2b3c-1d4e-4a8d-9c1f-4bb3f6d7a101"), "documentNumber": "100000004", "userId": uuid.UUID("8a6f2b3c-1d4e-4a8d-9c1f-4bb3f6d7a101"), "email": "camila.hernandez@yopmail.com", "first_name": "Camila", "last_name": "Hernandez", "phone": "3000000004", "travelerStatus": TravelerStatus.Active},
    {"id": uuid.UUID("c1e4d5f6-2a3b-4c4d-8e9f-5a6b7c8d9e10"), "documentNumber": "100000005", "userId": uuid.UUID("c1e4d5f6-2a3b-4c4d-8e9f-5a6b7c8d9e10"), "email": "juan.perez@yopmail.com", "first_name": "Juan", "last_name": "Perez", "phone": "3000000005", "travelerStatus": TravelerStatus.Active},
    {"id": uuid.UUID("d2f3a4b5-6c7d-4e8f-9a10-1b2c3d4e5f60"), "documentNumber": "100000006", "userId": uuid.UUID("d2f3a4b5-6c7d-4e8f-9a10-1b2c3d4e5f60"), "email": "valentina.mora@yopmail.com", "first_name": "Valentina", "last_name": "Mora", "phone": "3000000006", "travelerStatus": TravelerStatus.Active},
    {"id": uuid.UUID("e3a4b5c6-7d8e-4f90-9a11-2c3d4e5f6071"), "documentNumber": "100000007", "userId": uuid.UUID("e3a4b5c6-7d8e-4f90-9a11-2c3d4e5f6071"), "email": "santiago.lopez@yopmail.com", "first_name": "Santiago", "last_name": "Lopez", "phone": "3000000007", "travelerStatus": TravelerStatus.Active},
    {"id": uuid.UUID("f4b5c6d7-8e9f-4012-8a13-3d4e5f607182"), "documentNumber": "100000008", "userId": uuid.UUID("f4b5c6d7-8e9f-4012-8a13-3d4e5f607182"), "email": "daniela.garcia@yopmail.com", "first_name": "Daniela", "last_name": "Garcia", "phone": "3000000008", "travelerStatus": TravelerStatus.Active},
    {"id": uuid.UUID("a5c6d7e8-9f01-4123-8a14-4e5f60718293"), "documentNumber": "100000009", "userId": uuid.UUID("a5c6d7e8-9f01-4123-8a14-4e5f60718293"), "email": "mateo.suarez@yopmail.com", "first_name": "Mateo", "last_name": "Suarez", "phone": "3000000009", "travelerStatus": TravelerStatus.Active},
    {"id": uuid.UUID("b6d7e8f9-0a12-4234-8a15-5f60718293a4"), "documentNumber": "100000010", "userId": uuid.UUID("b6d7e8f9-0a12-4234-8a15-5f60718293a4"), "email": "laura.ramirez@yopmail.com", "first_name": "Laura", "last_name": "Ramirez", "phone": "3000000010", "travelerStatus": TravelerStatus.Active},
    {"id": uuid.UUID("c7e8f90a-1b23-4345-8a16-60718293a4b5"), "documentNumber": "100000011", "userId": uuid.UUID("c7e8f90a-1b23-4345-8a16-60718293a4b5"), "email": "andres.torres@yopmail.com", "first_name": "Andres", "last_name": "Torres", "phone": "3000000011", "travelerStatus": TravelerStatus.Active},
    {"id": uuid.UUID("d8f90a1b-2c34-4456-8a17-718293a4b5c6"), "documentNumber": "100000012", "userId": uuid.UUID("d8f90a1b-2c34-4456-8a17-718293a4b5c6"), "email": "paula.castro@yopmail.com", "first_name": "Paula", "last_name": "Castro", "phone": "3000000012", "travelerStatus": TravelerStatus.Active},
    {"id": uuid.UUID("e90a1b2c-3d45-4567-8a18-8293a4b5c6d7"), "documentNumber": "100000013", "userId": uuid.UUID("e90a1b2c-3d45-4567-8a18-8293a4b5c6d7"), "email": "sebastian.ortiz@yopmail.com", "first_name": "Sebastian", "last_name": "Ortiz", "phone": "3000000013", "travelerStatus": TravelerStatus.Active},
    {"id": uuid.UUID("0a1b2c3d-4e56-4678-8a19-93a4b5c6d7e8"), "documentNumber": "100000014", "userId": uuid.UUID("0a1b2c3d-4e56-4678-8a19-93a4b5c6d7e8"), "email": "juliana.vargas@yopmail.com", "first_name": "Juliana", "last_name": "Vargas", "phone": "3000000014", "travelerStatus": TravelerStatus.Active},
    {"id": uuid.UUID("1b2c3d4e-5f67-4789-8a1a-a4b5c6d7e8f9"), "documentNumber": "100000015", "userId": uuid.UUID("1b2c3d4e-5f67-4789-8a1a-a4b5c6d7e8f9"), "email": "diego.gomez@yopmail.com", "first_name": "Diego", "last_name": "Gomez", "phone": "3000000015", "travelerStatus": TravelerStatus.Active},
    {"id": uuid.UUID("2c3d4e5f-6071-4890-8a1b-b5c6d7e8f90a"), "documentNumber": "100000016", "userId": uuid.UUID("2c3d4e5f-6071-4890-8a1b-b5c6d7e8f90a"), "email": "natalia.reyes@yopmail.com", "first_name": "Natalia", "last_name": "Reyes", "phone": "3000000016", "travelerStatus": TravelerStatus.Active},
    {"id": uuid.UUID("3d4e5f60-7182-4901-8a1c-c6d7e8f90a1b"), "documentNumber": "100000017", "userId": uuid.UUID("3d4e5f60-7182-4901-8a1c-c6d7e8f90a1b"), "email": "felipe.marin@yopmail.com", "first_name": "Felipe", "last_name": "Marin", "phone": "3000000017", "travelerStatus": TravelerStatus.Active},
    {"id": uuid.UUID("4e5f6071-8293-4a12-8a1d-d7e8f90a1b2c"), "documentNumber": "100000018", "userId": uuid.UUID("4e5f6071-8293-4a12-8a1d-d7e8f90a1b2c"), "email": "maria.fernandez@yopmail.com", "first_name": "Maria", "last_name": "Fernandez", "phone": "3000000018", "travelerStatus": TravelerStatus.Active},
    {"id": uuid.UUID("5f607182-93a4-4b23-8a1e-e8f90a1b2c3d"), "documentNumber": "100000019", "userId": uuid.UUID("5f607182-93a4-4b23-8a1e-e8f90a1b2c3d"), "email": "camilo.rojas@yopmail.com", "first_name": "Camilo", "last_name": "Rojas", "phone": "3000000019", "travelerStatus": TravelerStatus.Active},
    {"id": uuid.UUID("60718293-a4b5-4c34-8a1f-f90a1b2c3d4e"), "documentNumber": "100000020", "userId": uuid.UUID("60718293-a4b5-4c34-8a1f-f90a1b2c3d4e"), "email": "isabella.cortes@yopmail.com", "first_name": "Isabella", "last_name": "Cortes", "phone": "3000000020", "travelerStatus": TravelerStatus.Active},
]

class SeedHelper:
    """Herramienta para poblar y restablecer las tablas de travelers."""

    @staticmethod
    def reset_and_seed():
        """
        Elimina todos los registros existentes de travelers, y luego inserta los datos de ejemplo definidos en TRAVELERS_FALLBACK.

        Returns:
            dict con el resumen de registros insertados o un mensaje de error.
        """
        try:
            # Limpiar tabla de travelers existentes
            TravelerAddress.query.delete()
            TravelerDocument.query.delete()
            Traveler.query.delete()
            
            db.session.flush()

            travelers_procesados = 0

            # Insertar travelers de ejemplo
            for traveler in TRAVELERS_FALLBACK:
                traveler_obj = Traveler(
                    id=traveler.get("id"),
                    documentNumber=traveler.get("documentNumber"),
                    userId=traveler.get("userId"),
                    first_name=traveler.get("first_name"),
                    last_name=traveler.get("last_name"),
                    phone=traveler.get("phone"),
                    email=traveler.get("email"),
                    travelerStatus=traveler.get("travelerStatus")
                )
                db.session.add(traveler_obj)
                travelers_procesados += 1

            db.session.commit()    

            return {
                "ok": True,
                "travelers_procesados": travelers_procesados,
                "usuarios_travelers": len(TRAVELERS_FALLBACK)
            }

        except Exception as e:
            db.session.rollback()
            return {"ok": False, "error": str(e)}
