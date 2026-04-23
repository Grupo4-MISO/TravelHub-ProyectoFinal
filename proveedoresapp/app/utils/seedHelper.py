from app.db.models import Manager, db
import uuid
import random

# ---------------------------------------------------------------------------
# Fallback: Usuarios MANAGER locales 
# ---------------------------------------------------------------------------
MANAGERS_FALLBACK = [
    {"id": uuid.UUID("9a4a97e8-7f0e-46fb-a451-d7de8ef19ba5"), "email": "carla.gomez@yopmail.com", "first_name": "Carla", "last_name": "Gomez"},
    {"id": uuid.UUID("7f93f279-130f-4231-9458-b976925d40eb"), "email": "diego.vargas@yopmail.com", "first_name": "Diego", "last_name": "Vargas"},
]

PROVIDERS_FALLBACK = [
    {"id": uuid.UUID("2cda6215-be04-4553-8cd9-cc0d67d7a64f"), "name": "Proveedor A", "DocumentNumber": "123456789", "status": "Active"},
    {"id": uuid.UUID("42ab5da0-b381-46b7-b209-db09052fcdd0"), "name": "Proveedor B", "DocumentNumber": "987654321", "status": "Pending"},
]


class SeedHelper:
    """Herramienta para poblar y restablecer las tablas de usuarios managers."""

    @staticmethod
    def reset_and_seed():
        """
        Elimina todos los registros existentes de managers,
        luego recorre cada manager, asignando 1 hospedaje.

        Returns:
            dict con el resumen de registros insertados o un mensaje de error.
        """
        try:
            # Limpiar tabla de managers existentes
            Manager.query.delete()
            db.session.flush()

            managers_procesados = 0

            # Recorrer cada manager
            for manager in MANAGERS_FALLBACK:
                raw_manager_id = manager.get("id")
                manager_id = raw_manager_id if isinstance(raw_manager_id, uuid.UUID) else uuid.UUID(str(raw_manager_id))

                # Seleccionar aleatoriamente 1 hospedaje para el manager
                num_hospedaje = random.randint(1, 1)
                hospedajes_seleccionados = random.sample(
                    HOSPEDAJES_FALLBACK, 
                    min(num_hospedaje, len(HOSPEDAJES_FALLBACK))
                )

                # Para cada manager, seleccionar un usuario aleatorio
                    
                # Construir el nombre del manager desde el email (antes del @)
                user_name = manager.get('email', "").split("@")[0]

                # Crear el Manager
                manager_obj = Manager(
                    id=uuid.uuid4(),
                    hospedajeId=uuid.UUID(str(hospedajes_seleccionados[0]["id"])),
                    userId=manager_id,
                    userName=user_name,
                    email = manager.get('email'),
                    first_name = manager.get('first_name'),
                    last_name = manager.get('last_name'),
                )
                
                db.session.add(manager_obj)
                managers_procesados += 1

            db.session.commit()

            return {
                "ok": True,
                "managers_procesados": managers_procesados,
                "usuarios_managers": len(MANAGERS_FALLBACK)
            }

        except Exception as e:
            db.session.rollback()
            return {"ok": False, "error": str(e)}
