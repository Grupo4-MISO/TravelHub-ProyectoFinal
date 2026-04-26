import json
import os

from app.db.models import Manager, Provider, ProviderAddress, ProviderDocument, ProviderStatus, db
import uuid
import random

# ---------------------------------------------------------------------------
# Fallback: Usuarios MANAGER locales 
# ---------------------------------------------------------------------------
MANAGERS_FALLBACK = [
    { "id": uuid.UUID("9a4a97e8-7f0e-46fb-a451-d7de8ef19ba5"), 
     "provider_id": uuid.UUID("300d110a-e8a8-4fce-ba66-a4883b20e6b9"), 
     "userId": uuid.UUID("9a4a97e8-7f0e-46fb-a451-d7de8ef19ba5"), "email": "carla.gomez@yopmail.com", "first_name": "Carla", "last_name": "Gomez", "phone": "555-1234"},
    { "id": uuid.UUID("7f93f279-130f-4231-9458-b976925d40eb"), 
     "provider_id": uuid.UUID("859f1435-879b-4590-b09c-33bb3ab9df0e"),
     "userId": uuid.UUID("7f93f279-130f-4231-9458-b976925d40eb"), "email": "diego.vargas@yopmail.com", "first_name": "Diego", "last_name": "Vargas", "phone": "555-5678"},
]

# Funciones para cargar HOSPEDAJES_SEED desde archivos JSON por país/ciudad
def _data_file_path(file_name):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, '..', 'data', file_name)


def _load_json_file(file_name):
    json_path = _data_file_path(file_name)
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"No se encontró el archivo {file_name} en {json_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Error al parsear el archivo {file_name}: {str(e)}")

def _load_providers_seed():
    """Carga y anexa los proveedores desde todas las fuentes definidas en el catálogo."""
    catalog = _load_json_file('providers_por_pais.json')
    providers = []

    for country in catalog.get('countries', []):
        for source in country.get('sources', []):
            file_name = source.get('file')
            if not file_name:
                continue

            source_data = _load_json_file(file_name)
            if not isinstance(source_data, list):
                raise ValueError(f"El archivo {file_name} debe contener una lista de proveedores.")

            providers.extend(source_data)

    return providers


def _to_uuid(value):
    if isinstance(value, uuid.UUID):
        return value
    return uuid.UUID(str(value))

PROVIDERS_FALLBACK = _load_providers_seed()

class SeedHelper:
    """Herramienta para poblar y restablecer las tablas de proveedores y managers."""

    @staticmethod
    def reset_and_seed():
        """
        Elimina todos los registros existentes de managers y proveedores, y luego inserta los datos de ejemplo definidos en MANAGERS_FALLBACK y PROVIDERS_FALLBACK.

        Returns:
            dict con el resumen de registros insertados o un mensaje de error.
        """
        try:
            # Limpiar tabla de managers existentes
            Manager.query.delete()

            # Limpiar tabla de proveedores existentes
            ProviderAddress.query.delete()
            ProviderDocument.query.delete()
            Provider.query.delete()

            db.session.flush()

            providers_procesados = 0
            # Insertar proveedores de ejemplo
            for provider in PROVIDERS_FALLBACK:
                provider_obj = Provider(
                    id=_to_uuid(provider.get("id")),
                    name=provider.get("Name", provider.get("name")),
                    documentNumber=provider.get("documentNumber"),
                    providerStatus= ProviderStatus.Active 
                )
                db.session.add(provider_obj)

                address_object = ProviderAddress(
                    id = uuid.uuid4(),
                    provider_id =_to_uuid(provider.get("id")),
                    line1 = provider.get("line1"),
                    line2 = None,
                    city = provider.get("city"),
                    state=provider.get("state"),
                    country=provider.get("country"),
                    countryCode = provider.get("countryCode"),      
                    postal_code = provider.get("postal_code") or provider.get("postalCode") or "00000",
                )
                db.session.add(address_object)

                providers_procesados += 1

            db.session.commit()    
            
            managers_procesados = 0
            # Recorrer cada manager
            for manager in MANAGERS_FALLBACK:
                provider_id = _to_uuid(manager.get("provider_id"))
                manager_id = _to_uuid(manager.get("id"))
                user_id = _to_uuid(manager.get("userId"))

                # Crear el Manager
                manager_obj = Manager(
                    id=manager_id,
                    provider_id=provider_id,
                    userId=user_id,
                    first_name = manager.get('first_name'),
                    last_name = manager.get('last_name'),
                    phone = manager.get('phone'),
                    email = manager.get('email'),
                )
                
                db.session.add(manager_obj)
                managers_procesados += 1

            
            db.session.commit()

            return {
                "ok": True,
                "managers_procesados": managers_procesados,
                "usuarios_managers": len(MANAGERS_FALLBACK),
                "providers_procesados": providers_procesados,
                "proveedores_seed": len(PROVIDERS_FALLBACK)
            }

        except Exception as e:
            db.session.rollback()
            return {"ok": False, "error": str(e)}
