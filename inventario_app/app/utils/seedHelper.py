import uuid
import random
import json
import os

from app.db.models import (
    db,
    AmenidadORM,
    HabitacionORM,
    HospedajeORM,
    Hospedaje_AmenidadORM,
    Hospedaje_ImagenORM,
    CountryORM,
)
from sqlalchemy import text

COUNTRIES_SEED = [
    { 
        "id" : "a3d59338-df76-4b27-92b9-d8d188a1a34a", 
        "name" : "Colombia", 
        "code" : "CO", 
        "currencyCode" : "COP", 
        "currencySymbol" : "$",
        "flagEmoji" : "🇨🇴",
        "phoneCode" : "+57"
    },
    { 
        "id" : "83cfaba7-7c63-4943-a984-34e2613f5300", 
        "name" : "Perú", 
        "code" : "PE", 
        "currencyCode" : "PEN", 
        "currencySymbol" : "$",
        "flagEmoji" : "🇵🇪",
        "phoneCode" : "+51"
    },
    { 
        "id" : "82ee7241-0e45-4e74-ab37-d590e3e3ba96", 
        "name" : "Ecuador", 
        "code" : "EC", 
        "currencyCode" : "USD", 
        "currencySymbol" : "$",
        "flagEmoji" : "🇪🇨",
        "phoneCode" : "+593"
    },
    { 
        "id" : "cecf374a-c329-4bca-b113-2fa2ad0ccf53", 
        "name" : "México", 
        "code" : "MX", 
        "currencyCode" : "MXN", 
        "currencySymbol" : "$",
        "flagEmoji" : "🇲🇽",
        "phoneCode" : "+52"
    },
    { 
        "id" : "79bde85e-343c-4d8f-8688-9518fcb15504", 
        "name" : "Chile", 
        "code" : "CL", 
        "currencyCode" : "CLP", 
        "currencySymbol" : "$",
        "flagEmoji" : "🇨🇱",
        "phoneCode" : "+56"
    },
    { 
        "id" : "2a1572bf-1ad7-4bf0-b8ae-000c067cbd45", 
        "name" : "Argentina", 
        "code" : "AR", 
        "currencyCode" : "ARS", 
        "currencySymbol" : "$",
        "flagEmoji" : "🇦🇷",
        "phoneCode" : "+54"
    }
]


AMENIDADES_SEED = [
    { "id" : "d329c0e8-42e6-40c8-8cf7-4e4e309f537c", "name" : "WiFi", "icon" : "IconWiFi" },
    { "id" : "e430d1f9-53f7-41d9-9d98-5f5f41a0648d", "name" : "Desayuno", "icon" : "IconDesayuno" },
    { "id" : "f541e2a0-64b8-42e0-aa20-6c6c52b1759e", "name" : "Estacionamiento", "icon" : "IconEstacionamiento" },
    { "id" : "a652f3b1-75c9-43f1-ba31-7d7d63c286af", "name" : "Piscina", "icon" : "IconPiscina" },
    { "id" : "b763a4c2-86d0-44a2-ca42-8e8e74d397ba", "name" : "Gimnasio", "icon" : "IconGimnasio" },
    { "id" : "c874b5d3-97e1-45b3-da53-9f9f85e408cb", "name" : "Room Service", "icon" : "IconRoomService" },
    { "id" : "d985c6e4-08f2-46c4-ea64-0a0a96f519dc", "name" : "Spa", "icon" : "IconSpa" },
    { "id" : "e096d7f5-19a3-47d5-fa75-1b1b07a620ed", "name" : "Restaurante", "icon" : "IconRestaurante" },
    { "id" : "f107e8a6-20b4-48e6-ab86-2c2c18b731fe", "name" : "Playa Privada", "icon" : "IconPlayaPrivada" },
    { "id" : "a218f9b7-31c5-49f7-bc97-3d3d29c842af", "name" : "Bar", "icon" : "IconBar" },
    { "id" : "b329a0c8-42d6-40a8-cd08-4e4e30d953ba", "name" : "Terraza", "icon" : "IconTerraza" },
    { "id" : "c430b1d9-53e7-41b9-de19-5f5f41e064cb", "name" : "Todo Incluido", "icon" : "IconTodoIncluido" },
    { "id" : "d541c2e0-64f8-42c0-ef20-6a6a52f175dc", "name" : "Kids Club", "icon" :"IconKidsClub" },
    { "id" : "e652d3f1-75a9-43d1-fa31-7b7b63a286ed", "name" : "Playa", "icon" : "IconPlaya" },
    { "id" : "f763e4a2-86b0-44e2-ab42-8c8c74b397fe", "name" : "Snorkel", "icon" : "IconSnorkel" },
    { "id" : "a874f5b3-97c1-45f3-bc53-9d9d85c408af", "name" : "Business Center", "icon" : "IconBusinessCenter" },
    { "id" : "b985a6c4-08d2-46a4-cd64-0e0e96d519ba", "name" : "Chimenea", "icon" : "IconChimenea" },
    { "id" : "c096b7d5-19e3-47b5-de75-1f1f07e620cb", "name" : "Jardín", "icon" : "IconJardin" },
    { "id" : "d107c8e6-20f4-48c6-ef86-2a2a18f731dc", "name" : "Tour Cafetero", "icon" : "IconTourCafetero" },
    { "id" : "e118d9f7-31a5-49d7-fa97-3b3b29a842ed", "name" : "Senderismo", "icon" : "IconSenderismo" }
]

IMG_HABITACIONES_SEED = [
    { "code" : "101", "url": "https://images.unsplash.com/photo-1611892440504-42a792e24d32?w=600"},
    { "code" : "102", "url": "https://images.unsplash.com/photo-1590490360182-c33d57733427?w=600"},
    { "code" : "103", "url": "https://images.unsplash.com/photo-1618773928121-c32242e63f39?w=600"}
]

CITY_COORDINATES = {
    "bogota": (4.7110, -74.0721),
    "medellin": (6.2442, -75.5812),
    "cartagena": (10.3910, -75.4794),
    "cali": (3.4516, -76.5320),
    "santa marta": (11.2408, -74.1990),
    "san andres": (12.5847, -81.7006),
    "manizales": (5.0703, -75.5138),
    "villa de leyva": (5.6349, -73.5248),
    "barranquilla": (10.9685, -74.7813),
    "lima": (-12.0464, -77.0428),
    "cusco": (-13.5319, -71.9675),
    "arequipa": (-16.4090, -71.5375),
    "puno": (-15.8402, -70.0219),
    "trujillo": (-8.1118, -79.0288),
    "mancora": (-4.1050, -81.0470),
    "paracas": (-13.8333, -76.2500),
    "iquitos": (-3.7437, -73.2516),
    "quito": (-0.1807, -78.4678),
    "guayaquil": (-2.1709, -79.9224),
    "cuenca": (-2.9001, -79.0059),
    "galapagos": (-0.9538, -90.9656),
    "montanita": (-1.8262, -80.7528),
    "banos": (-1.3967, -78.4229),
    "manta": (-0.9677, -80.7089),
    "otavalo": (0.2346, -78.2620),
    "ciudad de mexico": (19.4326, -99.1332),
    "cancun": (21.1619, -86.8515),
    "playa del carmen": (20.6296, -87.0739),
    "guadalajara": (20.6597, -103.3496),
    "puerto vallarta": (20.6534, -105.2253),
    "oaxaca": (17.0732, -96.7266),
    "tulum": (20.2114, -87.4654),
    "los cabos": (22.8905, -109.9167),
    "santiago": (-33.4489, -70.6693),
    "valparaiso": (-33.0472, -71.6127),
    "vina del mar": (-33.0245, -71.5518),
    "puerto varas": (-41.3175, -72.9850),
    "san pedro de atacama": (-22.9087, -68.1997),
    "punta arenas": (-53.1638, -70.9171),
    "la serena": (-29.9045, -71.2489),
    "concepcion": (-36.8201, -73.0444),
    "buenos aires": (-34.6037, -58.3816),
    "mendoza": (-32.8908, -68.8272),
    "bariloche": (-41.1335, -71.3103),
    "cordoba": (-31.4201, -64.1888),
    "salta": (-24.7821, -65.4232),
    "puerto madryn": (-42.7692, -65.0385),
    "ushuaia": (-54.8019, -68.3030),
    "mar del plata": (-38.0055, -57.5426),
}


def _normalize_city(city):
    if not city:
        return ""

    replacements = {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "Á": "a",
        "É": "e",
        "Í": "i",
        "Ó": "o",
        "Ú": "u",
        "ñ": "n",
        "Ñ": "n",
    }
    normalized = str(city)
    for source, target in replacements.items():
        normalized = normalized.replace(source, target)

    return normalized.lower().strip()


def _resolve_coordinates(data):
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if latitude is not None and longitude is not None:
        return float(latitude), float(longitude)

    city_key = _normalize_city(data.get("ciudad"))
    return CITY_COORDINATES.get(city_key, (0.0, 0.0))


def _resolve_description(data):
    description = data.get("description") or data.get("Description") or data.get("descripcion")
    if description:
        return str(description)
    return f"Hospedaje en {data.get('ciudad', 'destino turístico')}"

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


def _load_hospedajes_catalog():
    """Carga el catálogo de seeds por país y ciudad."""
    catalog = _load_json_file('hospedajes_por_pais_ciudad.json')
    if not isinstance(catalog, dict) or 'countries' not in catalog:
        raise ValueError("El archivo hospedajes_por_pais_ciudad.json debe contener la clave 'countries'.")

    seed_country_codes = {country['code'] for country in COUNTRIES_SEED}
    catalog_country_codes = {
        country.get('countryCode') for country in catalog.get('countries', [])
    }
    missing_country_codes = seed_country_codes - catalog_country_codes

    if missing_country_codes:
        missing = ", ".join(sorted(missing_country_codes))
        raise ValueError(
            f"Faltan países en el catálogo de hospedajes_por_pais_ciudad.json: {missing}"
        )

    return catalog


def _load_hospedajes_seed():
    """Carga y anexa los hospedajes desde todas las fuentes definidas en el catálogo."""
    catalog = _load_hospedajes_catalog()
    hospedajes = []

    for country in catalog.get('countries', []):
        for source in country.get('sources', []):
            file_name = source.get('file')
            if not file_name:
                continue

            source_data = _load_json_file(file_name)
            if not isinstance(source_data, list):
                raise ValueError(f"El archivo {file_name} debe contener una lista de hospedajes.")

            hospedajes.extend(source_data)

    return hospedajes


# #sym:HOSPEDAJES_SEED - Cargado desde catálogo JSON por país/ciudad
HOSPEDAJES_SEED = _load_hospedajes_seed()


class SeedHelper:
    """Herramienta para poblar y restablecer las tablas de hospedajes, habitaciones y amenidades."""

    @staticmethod
    def _ensure_habitaciones_code_column():
        """
        Asegura que la columna code exista en SQLite antes del seed.
        Esto corrige bases locales creadas con un esquema anterior.
        """
        uri = str(db.engine.url)

        if not uri.startswith("sqlite"):
            return

        columns = db.session.execute(text("PRAGMA table_info(habitaciones)"))
        column_names = {row[1] for row in columns}

        if "code" not in column_names:
            db.session.execute(
                text("ALTER TABLE habitaciones ADD COLUMN code VARCHAR(50) NOT NULL DEFAULT ''")
            )
            db.session.commit()

    @staticmethod
    def _ensure_hospedajes_country_code_column():
        """
        Asegura que la columna countryCode exista en SQLite antes del seed.
        Esto corrige bases locales creadas con un esquema anterior.
        """
        uri = str(db.engine.url)

        if not uri.startswith("sqlite"):
            return

        columns = db.session.execute(text("PRAGMA table_info(hospedajes)"))
        column_names = {row[1] for row in columns}

        if "countryCode" not in column_names:
            db.session.execute(
                text("ALTER TABLE hospedajes ADD COLUMN \"countryCode\" VARCHAR(10) NOT NULL DEFAULT ''")
            )
            db.session.commit()

    @staticmethod
    def _ensure_hospedajes_extended_columns():
        """
        Asegura columnas adicionales de hospedajes en SQLite (descripcion, latitude, longitude).
        Esto corrige bases locales creadas con un esquema anterior.
        """
        uri = str(db.engine.url)

        if not uri.startswith("sqlite"):
            return

        columns = db.session.execute(text("PRAGMA table_info(hospedajes)"))
        column_names = {row[1] for row in columns}

        if "descripcion" not in column_names:
            db.session.execute(
                text("ALTER TABLE hospedajes ADD COLUMN descripcion VARCHAR(255) NOT NULL DEFAULT ''")
            )

        if "latitude" not in column_names:
            db.session.execute(
                text("ALTER TABLE hospedajes ADD COLUMN latitude FLOAT NOT NULL DEFAULT 0")
            )

        if "longitude" not in column_names:
            db.session.execute(
                text("ALTER TABLE hospedajes ADD COLUMN longitude FLOAT NOT NULL DEFAULT 0")
            )

        db.session.commit()

    @staticmethod
    def reset_and_seed():   
        """
        Elimina todos los registros existentes de habitaciones, hospedajes,
        amenidades y tabla pivote, luego inserta los datos de seed definidos.

        Returns:
            dict con el resumen de registros insertados o un mensaje de error.
        """
        try:
            SeedHelper._ensure_habitaciones_code_column()
            SeedHelper._ensure_hospedajes_country_code_column()
            SeedHelper._ensure_hospedajes_extended_columns()
            CountryORM.__table__.create(bind=db.engine, checkfirst=True)

            # Primero borramos habitaciones por la FK
            HabitacionORM.query.delete()
            Hospedaje_ImagenORM.query.delete()
            Hospedaje_AmenidadORM.query.delete()
            HospedajeORM.query.delete()
            AmenidadORM.query.delete()
            CountryORM.query.delete()
            db.session.flush()

            hospedajes_insertados = 0
            habitaciones_insertadas = 0
            amenidades_insertadas = 0
            amenidades_asignadas = 0
            countries_insertados = 0
            amenidades_creadas = []

            for country_data in COUNTRIES_SEED:
                country = CountryORM(
                    id=uuid.UUID(country_data["id"]),
                    name=country_data["name"],
                    code=country_data["code"],
                    CurrencyCode=country_data["currencyCode"],
                    CurrencySymbol=country_data["currencySymbol"],
                    FlagEmoji=country_data["flagEmoji"],
                    PhoneCode=country_data["phoneCode"],
                )
                db.session.add(country)
                countries_insertados += 1

            for amenidad_data in AMENIDADES_SEED:
                amenidad = AmenidadORM(
                    id=uuid.UUID(amenidad_data["id"]),
                    name=amenidad_data["name"],
                    icon=amenidad_data["icon"],
                )
                db.session.add(amenidad)
                amenidades_creadas.append(amenidad)
                amenidades_insertadas += 1

            db.session.flush()

            for data in HOSPEDAJES_SEED:
                latitude, longitude = _resolve_coordinates(data)
                hospedaje = HospedajeORM(
                    id=uuid.UUID(data["id"]),
                    nombre=data["nombre"],
                    descripcion=_resolve_description(data),
                    countryCode = data["countryCode"],
                    pais=data["pais"],
                    ciudad=data["ciudad"],
                    direccion=data["direccion"],
                    latitude=latitude,
                    longitude=longitude,
                    rating=data["rating"],
                    reviews=data["reviews"],
                )
                db.session.add(hospedaje)
                db.session.flush()  # Obtenemos el id antes del commit

                # Asignamos entre 3 y 7 amenidades aleatorias por hospedaje.
                cantidad = random.randint(3, min(7, len(amenidades_creadas)))
                hospedaje.amenidades = random.sample(amenidades_creadas, k=cantidad)
                amenidades_asignadas += cantidad

                for hab in data["habitaciones"]:
                    habitacion = HabitacionORM(
                        id =uuid.UUID(hab["id"]),
                        propiedad_id=hospedaje.id,
                        code=hab["code"],
                        descripcion=hab["descripcion"],
                        capacidad=hab["capacidad"],
                        precio=hab["precio"],
                        imageUrl=next((img["url"] for img in IMG_HABITACIONES_SEED if img["code"] == hab["code"]), None)
                    )
                    db.session.add(habitacion)
                    habitaciones_insertadas += 1

                for img in data["imagenes"]:
                    imagen = Hospedaje_ImagenORM(
                        id=uuid.UUID(img["id"]),
                        hospedaje_id=hospedaje.id,
                        url=img["url"]
                    )
                    db.session.add(imagen)    

                hospedajes_insertados += 1

            db.session.commit()

            return {
                "ok": True,
                "countries_insertados": countries_insertados,
                "amenidades_insertadas": amenidades_insertadas,
                "amenidades_asignadas": amenidades_asignadas,
                "hospedajes_insertados": hospedajes_insertados,
                "habitaciones_insertadas": habitaciones_insertadas,
            }

        except Exception as e:
            db.session.rollback()
            return {"ok": False, "error": str(e)}
    
    @staticmethod
    def seed_reservations():
       habitaciones = HabitacionORM.query.all()
       restuldado = [str(habitacion.id) for habitacion in habitaciones]
       return {"habitacion_ids": restuldado}
