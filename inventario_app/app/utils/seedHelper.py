import uuid
import random

from app.db.models import (
    db,
    AmenidadORM,
    HabitacionORM,
    HospedajeORM,
    Hospedaje_AmenidadORM,
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
        "currencySymbol" : "S/",
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


# ---------------------------------------------------------------------------
# Datos de hoteles representativos en Colombia — 7 hoteles por ciudad
# Ciudades: Bogota, Medellin, Cartagena, Cali, Santa Marta,
#           Barranquilla, San Andres, Manizales, Villa de Leyva
# ---------------------------------------------------------------------------
HOSPEDAJES_SEED = [

    # ════════════════════════════════════════════════════════════════════════
    # Bogota  (7 hoteles)
    # ════════════════════════════════════════════════════════════════════════
    {
        "id": "300d110a-e8a8-4fce-ba66-a4883b20e6b9",
        "nombre": "Hotel Casa Medina",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Bogota",
        "direccion": "Carrera 7 # 69A-22, Chapinero, Bogota",
        "rating": 4.8, 
        "reviews": 1200,
        "habitaciones": [
            {"id": "8ec6a00d-2616-46a5-8376-2c22de6760ac", "code" : "101" , "descripcion": "Habitación Estándar Doble", "capacidad": 2, "precio": 380000.0},
            {"id": "9bf5b0fc-421c-43cc-b50f-47d843ad9800", "code" : "102" , "descripcion": "Suite Junior",              "capacidad": 2, "precio": 620000.0},
            {"id": "cd37f922-30c3-4998-af19-c7b9333e912a", "code" : "103" , "descripcion": "Suite Presidencial",        "capacidad": 4, "precio": 1200000.0},
        ],
    },
    {
        "id": "859f1435-879b-4590-b09c-33bb3ab9df0e",
        "nombre": "Sofitel Bogota Victoria Regia",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Bogota",
        "direccion": "Calle 98 # 9A-03, Chicó, Bogota",
        "rating": 4.7,
        "reviews": 950, 
        "habitaciones": [
            {"id": "ce99f183-c48a-4b07-a9c6-cb7880e811cc", "code" : "101" , "descripcion": "Habitación Clásica",  "capacidad": 2, "precio": 450000.0},
            {"id": "bf6476d7-667e-4898-863b-ce5d1a92e8de", "code" : "102" , "descripcion": "Habitación Superior", "capacidad": 2, "precio": 550000.0},
            {"id": "41de0b34-7b9b-48c6-8999-83316fbc110b", "code" : "103" , "descripcion": "Suite Luxury",         "capacidad": 3, "precio": 980000.0},
        ],
    },
    {
        "id": "ce956720-a473-42c6-a0a5-eef6b0b8415a",
        "nombre": "Hotel Tequendama",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Bogota",
        "direccion": "Carrera 10 # 26-21, Centro, Bogota",
        "rating": 4.2,
        "reviews": 800,
        "habitaciones": [
            {"id": "130a049f-56d8-4e0f-a98d-95641fbd28ef", "code" : "101" , "descripcion": "Habitación Sencilla",        "capacidad": 1, "precio": 180000.0},
            {"id": "ca07235e-e648-45f5-990f-c99f33ff9787", "code" : "102" , "descripcion": "Habitación Doble Estándar",  "capacidad": 2, "precio": 260000.0},
            {"id": "81924b69-6ccc-497d-9bb8-ff569e9536d1", "code" : "103" , "descripcion": "Suite Ejecutiva",            "capacidad": 2, "precio": 520000.0},
        ],
    },
    {
        "id": "11aa8a43-2216-4ae4-b121-d61cd73c1b0d",
        "nombre": "Hotel B.O.G",
        "pais": "Argentina",
        "ciudad": "Buenos Aires",
        "direccion": "Calle 11 # 4-16, La Candelaria, Buenos Aires",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Bogota",
        "direccion": "Calle 11 # 4-16, La Candelaria, Bogota",
        "rating": 4.6,
        "reviews": 1100,
        "habitaciones": [
            {"id": "ed04a651-620c-4ce7-9155-d787e6ec660b", "code" : "101" , "descripcion": "Habitación Urban",      "capacidad": 2, "precio": 410000.0},
            {"id": "35738cd5-da75-4fd5-9b0c-915f68184496", "code" : "102" , "descripcion": "Habitación Deluxe",     "capacidad": 2, "precio": 530000.0},
            {"id": "ae49df2c-255d-4aae-bf81-ef6e86f47657", "code" : "103" , "descripcion": "Suite Rooftop",         "capacidad": 3, "precio": 950000.0},
        ],
    },
    {
        "id": "d5dbb696-6bd4-4265-9032-9101965b34db",
        "nombre": "W Bogota",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Bogota",
        "direccion": "Calle 100 # 8A-01, Chicó, Bogota",
        "rating": 4.7,
        "reviews": 1300,    
        "habitaciones": [
            {"id": "62275ad7-c51c-4111-8bc1-d7e77dcfdfc5", "code" : "101" , "descripcion": "Wonderful Room",         "capacidad": 2, "precio": 600000.0},
            {"id": "138bc5f0-a81a-4229-9323-203fdaf45ffd", "code" : "102" , "descripcion": "Spectacular Suite",      "capacidad": 2, "precio": 900000.0},
            {"id": "9aaaa907-f447-420c-8841-c2bd987c1bb8", "code" : "103" , "descripcion": "WOW Suite",              "capacidad": 4, "precio": 1800000.0},
        ],
    },
    {
        "id": "66ef518d-0d97-4652-93aa-fcea4b917158",
        "nombre": "Hyatt Regency Bogota",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Bogota",
        "direccion": "Calle 24 # 57A-60, Salitre, Bogota",
        "rating": 4.5,
        "reviews": 1000,
        "habitaciones": [
            {"id": "03c1e385-1fad-4ac0-9c9f-19f414093493", "code" : "101" , "descripcion": "Habitación King Estándar",  "capacidad": 2, "precio": 390000.0},
            {"id": "33c0a7b5-73ea-4164-af58-3c1f716614c9", "code" : "102" , "descripcion": "Habitación Club",           "capacidad": 2, "precio": 520000.0},
            {"id": "b9879942-a68e-4df1-8b18-1db1f6b1d3ff", "code" : "103" , "descripcion": "Suite Regency",             "capacidad": 3, "precio": 870000.0},
        ],
    },
    {
        "id": "63534bd8-8476-4874-b4ad-c29fca185161",
        "nombre": "Hotel Click Clack Bogota",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Bogota",
        "direccion": "Carrera 11 # 93-77, Chicó, Bogota",
        "rating": 4.4,
        "reviews": 900,
        "habitaciones": [
            {"id": "74349159-b1f4-4c6a-a4ce-afbd0c19eb86", "code" : "101" , "descripcion": "Habitación Pequeña",    "capacidad": 1, "precio": 220000.0},
            {"id": "a33d09c7-4c8f-4e5a-804a-0f6512fb0964", "code" : "102" , "descripcion": "Habitación Mediana",    "capacidad": 2, "precio": 310000.0},
            {"id": "c9faf6ff-d97c-4bba-af4a-44d4fe4ec3d2", "code" : "103" , "descripcion": "Habitación Grande",     "capacidad": 3, "precio": 460000.0},
        ],
    },

    # ════════════════════════════════════════════════════════════════════════
    # Medellin  (7 hoteles)
    # ════════════════════════════════════════════════════════════════════════
    {
        "id": "b99a11f9-ffdc-42d1-887e-4cc652471f0c",
        "nombre": "Hotel Dann Carlton Medellin",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Medellin",
        "direccion": "Calle 1A Sur # 43A-83, El Poblado, Medellin",
        "rating": 4.6,
        "reviews": 1100,
        "habitaciones": [
            {"id": "d8b11063-2edf-4c36-b724-b54b0db1fd20", "code" : "101" , "descripcion": "Habitación Estándar",  "capacidad": 2, "precio": 320000.0},
            {"id": "6a96e2f7-6768-4d11-838f-d1727070676d", "code" : "102" , "descripcion": "Habitación Deluxe",    "capacidad": 2, "precio": 430000.0},
            {"id": "155a99bc-af25-47f6-adb4-42d56c01eefb", "code" : "103" , "descripcion": "Suite Ejecutiva",      "capacidad": 3, "precio": 750000.0},
        ],
    },
    {
        "id": "33774a58-5203-4910-8d18-c1a4d43a0add",
        "nombre": "Intercontinental Medellin",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Medellin",
        "direccion": "Calle 16 # 28-51, Laureles, Medellin",
        "rating": 4.5,
        "reviews": 900,
        "habitaciones": [
            {"id": "597fa455-8d24-4e6d-9f07-ca438a04bd09", "code" : "101" , "descripcion": "Habitación Club",  "capacidad": 2, "precio": 490000.0},
            {"id": "4f74dab5-6365-476a-acb6-28890f2d1b6a", "code" : "102" , "descripcion": "Suite Junior",     "capacidad": 2, "precio": 680000.0},
            {"id": "952baeca-c873-4d2e-b333-6d65749bbb9a", "code" : "103" , "descripcion": "Penthouse",        "capacidad": 4, "precio": 1500000.0},
        ],
    },
    {
        "id": "79be1bfc-37b1-49b7-a92b-6922d39ca65a",
        "nombre": "Hotel Park 10 Medellin",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Medellin",
        "direccion": "Carrera 36D # 10A-22, El Poblado, Medellin",
        "rating": 4.4,
        "reviews": 800, 
        "habitaciones": [
            {"id": "8fd15930-ee0d-4c7f-a224-9bcbb2a3edf6", "code" : "101" , "descripcion": "Habitación Sencilla", "capacidad": 1, "precio": 200000.0},
            {"id": "d96550d2-2e9e-4dbf-81a6-7da30073953b", "code" : "102" , "descripcion": "Habitación Doble",    "capacidad": 2, "precio": 290000.0},
            {"id": "37379570-0a47-4e0f-b500-2ed821f4e95f", "code" : "103" , "descripcion": "Habitación Triple",   "capacidad": 3, "precio": 370000.0},
        ],
    },
    {
        "id": "c9d34eb9-8447-44ab-9002-0dd11c3cd215",
        "nombre": "The Charlee Hotel Medellin",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Medellin",
        "direccion": "Carrera 43B # 11-50, El Poblado, Medellin",
        "rating": 4.7,
        "reviews": 1200,
        "habitaciones": [
            {"id": "5b37c212-d0f8-4696-83ca-dcdf342ca5de", "code" : "101" , "descripcion": "Habitación Lifestyle",   "capacidad": 2, "precio": 480000.0},
            {"id": "ef7b9f21-b8f2-405b-8d9b-4f0eadc8fe21", "code" : "102" , "descripcion": "Suite Rooftop Pool",     "capacidad": 2, "precio": 780000.0},
            {"id": "2125c918-db8a-4637-8892-c371a2c2017f", "code" : "103" , "descripcion": "Suite Presidencial",     "capacidad": 4, "precio": 1600000.0},
        ],
    },
    {
        "id": "fdbb20bf-9ce8-4476-a8a2-bfb5cb3bcb10",
        "nombre": "Hotel Diez Categoría Colombia",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Medellin",
        "direccion": "Calle 11A # 32-65, El Poblado, Medellin",
        "rating": 4.5,
        "reviews": 1000,
        "habitaciones": [
            {"id": "ac0f4af8-e1af-411e-8971-afff3f94a7b7", "code" : "101" , "descripcion": "Habitación Estándar",  "capacidad": 2, "precio": 350000.0},
            {"id": "821ec00c-4c57-4f09-b0f5-40905f5b561f", "code" : "102" , "descripcion": "Habitación Superior",  "capacidad": 2, "precio": 460000.0},
            {"id": "026b5bbe-8114-46b9-9f55-52c36c7b9a5e", "code" : "103" , "descripcion": "Suite Diez",           "capacidad": 3, "precio": 820000.0},
        ],
    },
    {
        "id": "e7769aaf-603e-465f-840a-0f804373d985",
        "nombre": "Hotel Nutibara Medellin",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Medellin",
        "direccion": "Carrera 50 # 52A-28, Centro, Medellin",
        "rating": 4.1,
        "reviews": 700,
        "habitaciones": [
            {"id": "3908c099-f92d-4da2-9085-989c6aa55680", "code" : "101" , "descripcion": "Habitación Sencilla",     "capacidad": 1, "precio": 150000.0},
            {"id": "2b2087d8-c540-4261-980e-81348c995ba6", "code" : "102" , "descripcion": "Habitación Doble",        "capacidad": 2, "precio": 210000.0},
            {"id": "d7d5035b-7c12-4c66-a0c6-4a802fb956ca", "code" : "103" , "descripcion": "Habitación Ejecutiva",    "capacidad": 2, "precio": 320000.0},
        ],
    },
    {
        "id": "cea4d236-be70-45bf-8a16-f83ef756312f",
        "nombre": "Hotel Estelar Milla de Oro",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Medellin",
        "direccion": "Carrera 43A # 6 Sur-15, El Poblado, Medellin",
        "rating": 4.6,
        "reviews": 900,
        "habitaciones": [
            {"id": "3c74b35c-5d55-48e6-91d2-6692351ca2a8", "code" : "101" , "descripcion": "Habitación Confort",   "capacidad": 2, "precio": 370000.0},
            {"id": "471b0c29-e166-43c6-9e4f-10bfeb33e139", "code" : "102" , "descripcion": "Habitación Deluxe",    "capacidad": 2, "precio": 500000.0},
            {"id": "b86280ee-5140-494a-b57a-a8e436b30671", "code" : "103" , "descripcion": "Suite Estelar",        "capacidad": 4, "precio": 900000.0},
        ],
    },

    # ════════════════════════════════════════════════════════════════════════
    # CARTAGENA  (7 hoteles)
    # ════════════════════════════════════════════════════════════════════════
    {
        "id": "177baefd-8f4c-4333-92fe-b7947a4e5a06",
        "nombre": "Hotel Charleston Santa Teresa",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Cartagena",
        "direccion": "Plaza de Santa Teresa, Centro Histórico, Cartagena",
        "rating": 4.9,
        "reviews": 1400,
        "habitaciones": [
            {"id": "7f120834-469e-4264-9dda-c99dfe0205a5", "code" : "101" , "descripcion": "Habitación Colonial",      "capacidad": 2, "precio": 650000.0},
            {"id": "6f8bb4ad-87f8-4d36-b2bb-daf4faa82eec", "code" : "102" , "descripcion": "Suite Panorámica Mar",     "capacidad": 2, "precio": 1100000.0},
            {"id": "cdfdceea-3d63-44ce-8e6d-0521c7935921", "code" : "103" , "descripcion": "Suite Real",               "capacidad": 4, "precio": 2200000.0},
        ],
    },
    {
        "id": "2cbed5ca-76ea-4674-972d-609439da3be7",
        "nombre": "Sofitel Legend Santa Clara",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Cartagena",
        "direccion": "Calle del Torno # 39-29, Centro Histórico, Cartagena",
        "rating": 4.9,
        "reviews": 1300,
        "habitaciones": [
            {"id": "1a1aaab5-0632-43ae-8120-76d11bd1741a", "code" : "101" , "descripcion": "Habitación Clásica Patio",   "capacidad": 2, "precio": 720000.0},
            {"id": "09a4f26c-f77a-4823-83a1-1349f10de98a", "code" : "102" , "descripcion": "Habitación Deluxe Piscina",  "capacidad": 2, "precio": 950000.0},
            {"id": "786a8d1c-479d-4b6a-b8a4-5757a949c99b", "code" : "103" , "descripcion": "Suite Legend",               "capacidad": 3, "precio": 1800000.0},
        ],
    },
    {
        "id": "e6f10ee9-10b9-4cab-b812-b13a8af287a0",
        "nombre": "Hotel Movich Cartagena de Indias",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Cartagena",
        "direccion": "Bocagrande, Carrera 3 # 8-129, Cartagena",
        "rating": 4.3,
        "reviews": 800,
        "habitaciones": [
            {"id": "69ece869-4c9f-4990-a946-3d87ea12edf8", "code" : "101" , "descripcion": "Habitación Estándar",    "capacidad": 2, "precio": 310000.0},
            {"id": "905dda41-2619-447d-894f-5bb783ebd2c6", "code" : "102" , "descripcion": "Habitación Vista al Mar","capacidad": 2, "precio": 480000.0},
            {"id": "0c6af421-e829-455c-bdaf-4d402840f164", "code" : "103" , "descripcion": "Suite Familiar",         "capacidad": 5, "precio": 820000.0},
        ],
    },
    {
        "id": "dc55b37d-8ded-49b6-a04b-9cece2734efb",
        "nombre": "Bastión Luxury Hotel",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Cartagena",
        "direccion": "Calle del Guerrero # 29-10, Centro Histórico, Cartagena",
        "rating": 4.8,
        "reviews": 1200,
        "habitaciones": [
            {"id": "61f0dd47-c8d0-4982-859d-d4cd1984c4a1", "code" : "101" , "descripcion": "Habitación Deluxe Patio",  "capacidad": 2, "precio": 680000.0},
            {"id": "115fb419-8de0-4987-98f3-2e4d9ef09481", "code" : "102" , "descripcion": "Suite Bastión",            "capacidad": 2, "precio": 1050000.0},
            {"id": "83c0d74e-f18a-4ad6-9e78-a51ba41ed1db", "code" : "103" , "descripcion": "Suite Gran Bastión",       "capacidad": 4, "precio": 2000000.0},
        ],
    },
    {
        "id": "dc5be755-1636-4599-9f43-9d97743b2786",
        "nombre": "Hotel Caribe by Faranda",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Cartagena",
        "direccion": "Carrera 1 # 2-87, Bocagrande, Cartagena",
        "rating": 4.2,
        "reviews": 700,
        "habitaciones": [
            {"id": "bfb89d53-6e1c-4058-b9c3-d77a974b94e9", "code" : "101" , "descripcion": "Habitación Estándar Jardín", "capacidad": 2, "precio": 270000.0},
            {"id": "534a63f3-1651-4261-8c03-b87e7fc5d430", "code" : "102" , "descripcion": "Habitación Vista al Mar",    "capacidad": 2, "precio": 380000.0},
            {"id": "72f984f6-b79d-4ddc-853f-018357e4d82e", "code" : "103" , "descripcion": "Suite Caribe",               "capacidad": 4, "precio": 750000.0},
        ],
    },
    {
        "id": "9046b401-28e5-45d7-a05b-1e7c825c2fed",
        "nombre": "Almirante Cartagena Hotel",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Cartagena",
        "direccion": "Av. San Martín # 4-33, Bocagrande, Cartagena",
        "rating": 4.1,
        "reviews": 600,
        "habitaciones": [
            {"id": "1d14b0ad-7ea0-4bb9-ac1b-bd5cf2d27983", "code" : "101" , "descripcion": "Habitación Sencilla",   "capacidad": 1, "precio": 210000.0},
            {"id": "4dd30c99-da2b-4dc5-af32-c9fd476c3a31", "code" : "102" , "descripcion": "Habitación Doble",      "capacidad": 2, "precio": 300000.0},
            {"id": "bc8287dc-fe69-471a-a701-63908d96fbc5", "code" : "103" , "descripcion": "Suite Superior",        "capacidad": 3, "precio": 580000.0},
        ],
    },
    {
        "id": "3faa135c-376f-4cad-9bf6-64bb98a93a85",
        "nombre": "El Marqués Hotel Boutique",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Cartagena",
        "direccion": "Calle 33 # 3-67, Getsemaní, Cartagena",
        "rating": 4.5,
        "reviews": 850,
        "habitaciones": [
            {"id": "ba7187cf-e7ca-4cda-a9d4-6f0ab9bcfe18", "code" : "101" , "descripcion": "Habitación Getsemaní",  "capacidad": 2, "precio": 340000.0},
            {"id": "1f773935-fefd-4880-aa2c-97b9ee36f5f9", "code" : "102" , "descripcion": "Suite Marqués",         "capacidad": 2, "precio": 560000.0},
            {"id": "acb9af38-ef22-4fc6-9733-12607ea8a630", "code" : "103" , "descripcion": "Suite Familiar",        "capacidad": 4, "precio": 920000.0},
        ],
    },

    # ════════════════════════════════════════════════════════════════════════
    # CALI  (7 hoteles)
    # ════════════════════════════════════════════════════════════════════════
    {
        "id": "996d574f-ca06-45aa-859a-51b16f171c13",
        "nombre": "Hotel Dann Carlton Cali",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Cali",
        "direccion": "Avenida Colombia # 2-72, Cali",
        "rating": 4.4,
        "reviews": 1000,
        "habitaciones": [
            {"id": "47207429-dbf3-4877-ab05-29153b9bf216", "code" : "101" , "descripcion": "Habitación Estándar Sencilla", "capacidad": 1, "precio": 190000.0},
            {"id": "8ba38a48-af85-4dd8-9a05-acc61abcb7a1", "code" : "102" , "descripcion": "Habitación Estándar Doble",    "capacidad": 2, "precio": 280000.0},
            {"id": "e8f8b0d5-5750-4382-8650-71dc2c73926c", "code" : "103" , "descripcion": "Suite Ejecutiva",              "capacidad": 2, "precio": 560000.0},
        ],
    },
    {
        "id": "721a9e18-93ea-472a-b266-8628b20c7aed",
        "nombre": "GHL Hotel Collection Palma Real",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Cali",
        "direccion": "Calle 19A Norte # 8N-40, Cali",
        "rating": 4.3,
        "reviews": 1100,
        "habitaciones": [
            {"id": "fef4b4f9-d9e6-4a63-943e-369aa248d151", "code" : "101" , "descripcion": "Habitación Business",  "capacidad": 2, "precio": 240000.0},
            {"id": "d96726f4-a122-4c8b-a1ce-f6049873b61d", "code" : "102" , "descripcion": "Habitación Deluxe",    "capacidad": 2, "precio": 360000.0},
            {"id": "9a177549-d051-4c35-b79a-39c937564fb3", "code" : "103" , "descripcion": "Suite Junior",         "capacidad": 3, "precio": 620000.0},
        ],
    },
    {
        "id": "b60a1ad8-d32b-42ab-8696-fe8fd249df75",
        "nombre": "Hotel Spiwak Chipichape",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Cali",
        "direccion": "Carrera 1B # 66-200, Chipichape, Cali",
        "rating": 4.5,
        "reviews": 900,
        "habitaciones": [
            {"id": "7b315c7a-ba78-4b92-878a-1f2c917d9c8e", "code" : "101" , "descripcion": "Habitación Superior",  "capacidad": 2, "precio": 310000.0},
            {"id": "f06f6b3a-9de0-4846-bd1b-503f9281656d", "code" : "102" , "descripcion": "Habitación Deluxe",    "capacidad": 2, "precio": 420000.0},
            {"id": "d000ccea-815c-465c-8996-2985635ed6b9", "code" : "103" , "descripcion": "Suite Spiwak",         "capacidad": 4, "precio": 780000.0},
        ],
    },
    {
        "id": "a7e4aad0-967b-464a-ab44-38417219de76",
        "nombre": "Estelar Belmonte Cali",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Cali",
        "direccion": "Calle 16A Norte # 4N-62, Normandía, Cali",
        "rating": 4.4,
        "reviews": 850,
        "habitaciones": [
            {"id": "5416323c-ecb8-4e2d-a806-40e93b23d5e1", "code" : "101" , "descripcion": "Habitación Confort",   "capacidad": 2, "precio": 270000.0},
            {"id": "8bac6ac0-ac4b-4441-971a-3cf63169ce0d", "code" : "102" , "descripcion": "Habitación Superior",  "capacidad": 2, "precio": 370000.0},
            {"id": "addc0757-88f8-487f-961d-68ff45dc780c", "code" : "103" , "descripcion": "Suite Estelar",        "capacidad": 3, "precio": 650000.0},
        ],
    },
    {
        "id": "ac522e77-2cb2-4377-8016-902a56310169",
        "nombre": "Hotel Camino Real Cali",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Cali",
        "direccion": "Av. Colombia # 7-38, Granada, Cali",
        "rating": 4.0,
        "reviews": 1200,
        "habitaciones": [
            {"id": "c8bffeb3-943f-4331-a8cc-1702a333d1d4", "code" : "101" , "descripcion": "Habitación Sencilla",       "capacidad": 1, "precio": 160000.0},
            {"id": "3b9fa9ac-6420-4163-aeb0-9bbc72d3e413", "code" : "102" , "descripcion": "Habitación Doble Estándar", "capacidad": 2, "precio": 230000.0},
            {"id": "fe8ac986-791a-4f54-8065-f024bc54b896", "code" : "103" , "descripcion": "Habitación Familiar",       "capacidad": 4, "precio": 390000.0},
        ],
    },
    {
        "id": "a611593b-7aa5-41dc-9645-ee45a88519f1",
        "nombre": "Hotel Boutique Bello Horizonte Cali",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Cali",
        "direccion": "Calle 5B # 36A-27, San Fernando, Cali",
        "rating": 4.6,
        "reviews": 1000,
        "habitaciones": [
            {"id": "2d33c1d1-86ae-423e-a391-b1c9106e5ecc", "code" : "101" , "descripcion": "Habitación Jardín",     "capacidad": 2, "precio": 290000.0},
            {"id": "fc385e1a-3078-4301-8ef2-fca014d12716", "code" : "102" , "descripcion": "Habitación Piscina",    "capacidad": 2, "precio": 380000.0},
            {"id": "577b6c25-e06c-4373-a916-a874fedc0c13", "code" : "103" , "descripcion": "Suite Bello Horizonte", "capacidad": 3, "precio": 680000.0},
        ],
    },
    {
        "id": "6a57e50e-e7c7-4830-b422-87a7b7929671",
        "nombre": "Hotel Casa Republicana Cali",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Cali",
        "direccion": "Carrera 6 # 8-13, Centro Histórico, Cali",
        "rating": 4.2,
        "reviews": 800,
        "habitaciones": [
            {"id": "64ea074a-db46-430d-a188-2cb22cc786ec", "code" : "101" , "descripcion": "Habitación Colonial",   "capacidad": 2, "precio": 220000.0},
            {"id": "6b8abc79-c8be-438f-bf33-f8e2a3c8cbe9", "code" : "102" , "descripcion": "Suite Colonial",        "capacidad": 3, "precio": 420000.0},
            {"id": "c626a2b0-6ab5-4d5a-897b-0139ad61816e", "code" : "103" , "descripcion": "Suite Presidencial",    "capacidad": 4, "precio": 750000.0},
        ],
    },

    # ════════════════════════════════════════════════════════════════════════
    # SANTA MARTA  (7 hoteles)
    # ════════════════════════════════════════════════════════════════════════
    {
        "id": "a367622d-3d77-484a-8cd8-8bee9e9d1219",
        "nombre": "Hotel Zuana Beach Resort",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Santa Marta",
        "direccion": "Carrera 2 # 6-10, El Rodadero, Santa Marta",
        "rating": 4.5,
        "reviews": 1200,
        "habitaciones": [
            {"id": "1e0467d2-1e0f-4676-8f97-89860ad73537", "code" : "101" , "descripcion": "Habitación Estándar",    "capacidad": 2, "precio": 350000.0},
            {"id": "89d483e8-77a4-47fe-b956-13cb31bac204", "code" : "102" , "descripcion": "Suite Frente al Mar",    "capacidad": 2, "precio": 600000.0},
            {"id": "0e2b930a-0ed7-4be9-bebd-23401db26aa1", "code" : "103" , "descripcion": "Suite Familiar",         "capacidad": 5, "precio": 900000.0},
        ],
    },
    {
        "id": "6e46139f-10c3-47ff-8e55-e3e7fed7ba6c",
        "nombre": "Casa Loma Hotel Boutique",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Santa Marta",
        "direccion": "Carrera 20 # 3-69, Centro Histórico, Santa Marta",
        "rating": 4.6,
        "reviews": 900,
        "habitaciones": [
            {"id": "d7c7cc82-a746-49ce-b907-e41c4b95e2e9", "code" : "101" , "descripcion": "Habitación Jardín",      "capacidad": 2, "precio": 280000.0},
            {"id": "5e3e0141-6e54-4cf8-bb55-c4cb61845a85", "code" : "102" , "descripcion": "Habitación Vista Ciudad","capacidad": 2, "precio": 340000.0},
            {"id": "9dafaab1-88e1-401c-8fcc-2730cb07beef", "code" : "103" , "descripcion": "Suite Penthouse",        "capacidad": 3, "precio": 780000.0},
        ],
    },
    {
        "id": "0a784cd5-4ae6-4408-8a7c-eb2267b994de",
        "nombre": "Irotama Resort Santa Marta",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Santa Marta",
        "direccion": "Km 14 vía Santa Marta-Barranquilla, Santa Marta",
        "rating": 4.4,
        "reviews": 1100,
        "habitaciones": [
            {"id": "f42fda46-dd7d-4976-98c4-18ca94a30302", "code" : "101" , "descripcion": "Cabaña Estándar",        "capacidad": 2, "precio": 400000.0},
            {"id": "b0acf5b0-54fd-4bfd-89d3-6479c587f8aa", "code" : "102" , "descripcion": "Cabaña Frente al Mar",   "capacidad": 4, "precio": 680000.0},
            {"id": "9c810f03-1e5f-4017-acda-8733dd79e09a", "code" : "103" , "descripcion": "Suite VIP Playa",        "capacidad": 4, "precio": 1100000.0},
        ],
    },
    {
        "id": "d3fb8472-4137-4a4a-931f-e203b8c798e5",
        "nombre": "La Sierra Hotel El Rodadero",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Santa Marta",
        "direccion": "Carrera 1A # 9-47, El Rodadero, Santa Marta",
        "rating": 4.3,
        "reviews": 800,
        "habitaciones": [
            {"id": "bdc18575-08ce-4d98-a8f0-1811a33affa1", "code" : "101" , "descripcion": "Habitación Sencilla",     "capacidad": 1, "precio": 190000.0},
            {"id": "df2d3992-4952-475a-8ee6-586f1c82cd13", "code" : "102" , "descripcion": "Habitación Vista Mar",    "capacidad": 2, "precio": 320000.0},
            {"id": "5847273e-074b-4d5f-8ea6-1730ec75468c", "code" : "103" , "descripcion": "Suite Familiar",          "capacidad": 5, "precio": 620000.0},
        ],
    },
    {
        "id": "262c174d-b9cc-4860-939c-00bb940a7f45",
        "nombre": "Tamacá Beach Resort Hotel",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Santa Marta",
        "direccion": "Carrera 2 # 11A-98, El Rodadero, Santa Marta",
        "rating": 4.2,
        "reviews": 700,
        "habitaciones": [
            {"id": "0f016d72-fdbb-4f8e-a935-8cb64669552b", "code" : "101" , "descripcion": "Habitación Playa",        "capacidad": 2, "precio": 310000.0},
            {"id": "33b7f219-8745-4f2b-aa73-82462f04559d", "code" : "102" , "descripcion": "Suite Coral",             "capacidad": 3, "precio": 520000.0},
            {"id": "f2bbaa8b-c3fa-40ab-a456-98f982b4a70c", "code" : "103" , "descripcion": "Suite Presidencial Mar",  "capacidad": 4, "precio": 850000.0},
        ],
    },
    {
        "id": "a4c036cb-a020-4f79-8ab2-855ecffdb1cd",
        "nombre": "Hotel Bello Horizonte Santa Marta",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Santa Marta",
        "direccion": "Carrera 2 # 11-24, El Rodadero, Santa Marta",
        "rating": 4.1,
        "reviews": 600, 
        "habitaciones": [
            {"id": "d946346c-8fdf-40b5-b8f0-a56a162ab193", "code" : "101" , "descripcion": "Habitación Económica",   "capacidad": 2, "precio": 180000.0},
            {"id": "110d5364-5186-4d1a-8bd0-836dc9321cf3", "code" : "102" , "descripcion": "Habitación Doble",       "capacidad": 2, "precio": 260000.0},
            {"id": "8018d84b-0a37-4e4a-b4f1-fee676c5fbe4", "code" : "103" , "descripcion": "Habitación Triple",      "capacidad": 3, "precio": 350000.0},
        ],
    },
    {
        "id": "c926533b-d033-4573-a0f3-8368378afcf5",
        "nombre": "Hotel Boutique La Tortuga",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Santa Marta",
        "direccion": "Calle 18 # 3-26, Centro Histórico, Santa Marta",
        "rating": 4.7,
        "reviews": 850,
        "habitaciones": [
            {"id": "9a2c8080-360e-4552-8387-20e9c30d14fe", "code" : "101" , "descripcion": "Habitación Deluxe",      "capacidad": 2, "precio": 360000.0},
            {"id": "c4db2560-03d0-4b02-acb9-1c248c8e5100", "code" : "102" , "descripcion": "Suite Caribe",           "capacidad": 2, "precio": 580000.0},
            {"id": "5f9421ce-3385-4585-8af2-bb36237a7171", "code" : "103" , "descripcion": "Suite La Tortuga",       "capacidad": 4, "precio": 960000.0},
        ],
    },

    # ════════════════════════════════════════════════════════════════════════
    # BARRANQUILLA  (7 hoteles)
    # ════════════════════════════════════════════════════════════════════════
    {
        "id": "b760a30f-4ef3-443b-b928-64c3fee45f02",
        "nombre": "Hotel El Prado",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Barranquilla",
        "direccion": "Carrera 54 # 70-10, El Prado, Barranquilla",
        "rating": 4.4,
        "reviews": 1000,
        "habitaciones": [
            {"id": "9eac4560-9394-4450-a111-51b6b21fb8f4", "code" : "101" , "descripcion": "Habitación Clásica",    "capacidad": 2, "precio": 220000.0},
            {"id": "d67c812f-2700-4c78-b8ed-42a569732cd2", "code" : "102" , "descripcion": "Habitación Superior",   "capacidad": 2, "precio": 320000.0},
            {"id": "3c2c7a8d-73a8-4d45-a3a1-93d35e30bc7a", "code" : "103" , "descripcion": "Suite Gran Prado",      "capacidad": 4, "precio": 700000.0},
        ],
    },
    {
        "id": "8c2e8214-d38d-4364-b9f9-ab911ba95d8a",
        "nombre": "GHL Hotel Barranquilla",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Barranquilla",
        "direccion": "Carrera 52 # 75-30, Barranquilla",
        "rating": 4.2,
        "reviews": 900,
        "habitaciones": [
            {"id": "8a341169-db44-4a9c-b4c6-2252df9ed2cf", "code" : "101" , "descripcion": "Habitación Estándar",   "capacidad": 2, "precio": 200000.0},
            {"id": "258337aa-5624-445e-9649-19f0b9496ead", "code" : "102" , "descripcion": "Habitación Ejecutiva",  "capacidad": 2, "precio": 300000.0},
            {"id": "dfa62105-1e2a-4904-aaac-4708e72cd991", "code" : "103" , "descripcion": "Suite Ejecutiva",       "capacidad": 3, "precio": 550000.0},
        ],
    },
    {
        "id": "035c5388-66b6-4e30-baf2-8a20afff7f11",
        "nombre": "Hotel Dann Carlton Barranquilla",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Barranquilla",
        "direccion": "Carrera 50 # 80-41, El Nogal, Barranquilla",
        "rating": 4.5,
        "reviews": 1100,
        "habitaciones": [
            {"id": "9eb29a79-f063-4d37-8fbb-e4d57a00f184", "code" : "101" , "descripcion": "Habitación Confort",    "capacidad": 2, "precio": 260000.0},
            {"id": "bc848086-c9e1-440c-bbd7-d49ca51dcf45", "code" : "102" , "descripcion": "Habitación Deluxe",     "capacidad": 2, "precio": 370000.0},
            {"id": "ca21c88a-cdc9-4fa2-8b81-e3c043cb2a15", "code" : "103" , "descripcion": "Suite Carlton",         "capacidad": 3, "precio": 720000.0},
        ],
    },
    {
        "id": "f839f286-3b95-48a9-aa4b-562c71d346b8",
        "nombre": "Sonesta Hotel Barranquilla",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Barranquilla",
        "direccion": "Calle 106 # 50-48, Barranquilla",
        "rating": 4.3,
        "reviews": 950,
        "habitaciones": [
            {"id": "8e5f6dda-0115-46a7-bf76-48ee9c55eef5", "code" : "101" , "descripcion": "Habitación Estándar",   "capacidad": 2, "precio": 240000.0},
            {"id": "d4d1b118-5bb9-4667-b4cc-706bfda38f18", "code" : "102" , "descripcion": "Habitación Superior",   "capacidad": 2, "precio": 340000.0},
            {"id": "1148f047-5a29-4147-950b-67a7ebb8eb6a", "code" : "103" , "descripcion": "Suite Sonesta",         "capacidad": 4, "precio": 680000.0},
        ],
    },
    {
        "id": "b97e420c-4649-4c66-9337-8bff924a34d1",
        "nombre": "Holiday Inn Barranquilla",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Barranquilla",
        "direccion": "Carrera 54 # 59-45, Barranquilla",
        "rating": 4.1,
        "reviews": 850,
        "habitaciones": [
            {"id": "127b4cef-d783-4263-a9b0-d8a19bad4d01", "code" : "101" , "descripcion": "Habitación Estándar",      "capacidad": 2, "precio": 210000.0},
            {"id": "dc6290d0-c3bd-4764-8adf-9c4ff53590c5", "code" : "102" , "descripcion": "Habitación Ejecutiva",     "capacidad": 2, "precio": 290000.0},
            {"id": "4eaeb8d0-789d-49da-a77d-c2d9448a27bc", "code" : "103" , "descripcion": "Suite Familiar",           "capacidad": 4, "precio": 500000.0},
        ],
    },
    {
        "id": "05f12119-2fdb-4472-837b-4f44fbc7f422",
        "nombre": "Estelar Barranquilla Hotel",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Barranquilla",
        "direccion": "Carrera 53 # 98-228, Barranquilla",
        "rating": 4.4,
        "reviews": 900,
        "habitaciones": [
            {"id": "4faa9113-9600-4f1d-b127-80c5a9cdb632", "code" : "101" , "descripcion": "Habitación Confort",    "capacidad": 2, "precio": 250000.0},
            {"id": "0b1dbc89-447a-48b0-b4d9-0bff96be45d7", "code" : "102" , "descripcion": "Habitación Deluxe",     "capacidad": 2, "precio": 360000.0},
            {"id": "55243358-6df1-445e-9371-fe2f9ae929be", "code" : "103" , "descripcion": "Suite Estelar",         "capacidad": 3, "precio": 640000.0},
        ],
    },
    {
        "id": "09dfea9e-994b-46a2-85b3-03deb3dc16d6",
        "nombre": "Hotel Movich Buró 26 Barranquilla",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Barranquilla",
        "direccion": "Carrera 53B # 26-21, Barranquilla",
        "rating": 4.3,
        "reviews": 850,
        "habitaciones": [
            {"id": "f491a6a5-958d-4afe-b14f-fe67d810a339", "code" : "101" , "descripcion": "Habitación Smart",      "capacidad": 1, "precio": 180000.0},
            {"id": "789f0a8a-f75e-4de5-8a38-01147fa7322a", "code" : "102" , "descripcion": "Habitación Business",   "capacidad": 2, "precio": 280000.0},
            {"id": "19846e70-9e26-42b1-8d7d-5b6aaf9bf197", "code" : "103" , "descripcion": "Suite Movich",          "capacidad": 3, "precio": 530000.0},
        ],
    },

    # ════════════════════════════════════════════════════════════════════════
    # San Andres  (7 hoteles)
    # ════════════════════════════════════════════════════════════════════════
    {
        "id": "f56de4e2-a3a5-4a88-8259-70c16c53d943",
        "nombre": "Hotel Decameron San Luis",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "San Andres",
        "direccion": "Km 13 vía San Luis, San Andres Isla",
        "rating": 4.5,
        "reviews": 1200,
        "habitaciones": [
            {"id": "f265d5c9-c41d-4897-b2bf-44d4bf2776ad", "code" : "101" , "descripcion": "Habitación Estándar Todo Incluido",  "capacidad": 2, "precio": 580000.0},
            {"id": "71970215-fc0c-4048-b8ae-15920564867f", "code" : "102" , "descripcion": "Habitación Superior Vista al Mar",   "capacidad": 2, "precio": 780000.0},
            {"id": "116af757-b05e-4ec1-bfbd-1cccba768704", "code" : "103" , "descripcion": "Suite Caribe",                       "capacidad": 4, "precio": 1400000.0},
        ],
    },
    {
        "id": "1c72f450-be39-4c76-9ac7-110634c63f5d",
        "nombre": "Casa Harb Hotel Boutique",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "San Andres",
        "direccion": "Av. Colombia # 3-59, San Andres Isla",
        "rating": 4.6,
        "reviews": 900,
        "habitaciones": [
            {"id": "f654e7b8-3169-42dd-81cf-58b4a64b470e", "code" : "101" , "descripcion": "Habitación Coral",               "capacidad": 2, "precio": 420000.0},
            {"id": "723c2944-2d49-4d55-b70b-b5f98603f4a4", "code" : "102" , "descripcion": "Habitación Mar de Siete Colores","capacidad": 2, "precio": 600000.0},
            {"id": "397e5188-2ad7-47fe-9314-aa43a9fc1051", "code" : "103" , "descripcion": "Suite Isla",                     "capacidad": 3, "precio": 950000.0},
        ],
    },
    {
        "id": "0fedea59-bcc4-4b90-b703-b8613d93c415",
        "nombre": "Hotel Sunrise Beach San Andres",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "San Andres",
        "direccion": "Av. Colombia # 1A-104, San Andres Isla",
        "rating": 4.3,
        "reviews": 850,
        "habitaciones": [
            {"id": "a8b7436f-2329-480b-8826-857296842dc6", "code" : "101" , "descripcion": "Habitación Playa",         "capacidad": 2, "precio": 360000.0},
            {"id": "c12d9860-6980-4305-bd0f-6bc023e484c8", "code" : "102" , "descripcion": "Suite Amanecer Mar",       "capacidad": 2, "precio": 560000.0},
            {"id": "168fdd6d-ceea-4f03-a029-f65dc61c148b", "code" : "103" , "descripcion": "Suite Familiar Sunrise",   "capacidad": 5, "precio": 920000.0},
        ],
    },
    {
        "id": "81057645-60de-468e-a6b2-6591575839b5",
        "nombre": "Hotel Lord Pierre San Andres",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "San Andres",
        "direccion": "Av. 20 de Julio # 3-88, San Andres Isla",
        "rating": 4.0,
        "reviews": 800,
        "habitaciones": [
            {"id": "0f01beec-bd22-4905-86af-723945cba9e1", "code" : "101" , "descripcion": "Habitación Estándar",       "capacidad": 2, "precio": 290000.0},
            {"id": "c8161ef5-ced1-44c2-9651-f787779fb2e8", "code" : "102" , "descripcion": "Habitación Vista al Mar",   "capacidad": 2, "precio": 400000.0},
            {"id": "5bf32407-7e9b-46cf-b1a1-8abf9842f44c", "code" : "103" , "descripcion": "Suite Lord Pierre",         "capacidad": 3, "precio": 680000.0},
        ],
    },
    {
        "id": "f71b03be-da4c-4fff-9204-574cded1b9a7",
        "nombre": "Portobelo Hotel San Andres",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "San Andres",
        "direccion": "Carretera Circunvalar Km 2, San Andres Isla",
        "rating": 4.2,
        "reviews": 750,
        "habitaciones": [
            {"id": "3720ed32-e4c7-4828-8898-3588302fbc0d", "code" : "101" , "descripcion": "Habitación Jardín Tropical","capacidad": 2, "precio": 310000.0},
            {"id": "ce2462a5-3590-46c4-883b-8c918d497640", "code" : "102" , "descripcion": "Habitación Piscina",        "capacidad": 2, "precio": 440000.0},
            {"id": "b2bb5e76-ae2c-48c7-b775-6472d3a27908", "code" : "103" , "descripcion": "Suite Portobelo",           "capacidad": 4, "precio": 780000.0},
        ],
    },
    {
        "id": "08cfcc5b-ede9-4e48-be6b-123631bc966e",
        "nombre": "Cocoplum Beach Hotel",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "San Andres",
        "direccion": "North End, San Andres Isla",
        "rating": 4.4,
        "reviews": 800,
        "habitaciones": [
            {"id": "b1a13ca0-5d6f-4d84-a44a-bb630ce15436", "code" : "101" , "descripcion": "Habitación Coconut",       "capacidad": 2, "precio": 380000.0},
            {"id": "5b2586c7-e869-4c82-bbb3-9b0a9357945e", "code" : "102" , "descripcion": "Suite Ocean View",         "capacidad": 2, "precio": 620000.0},
            {"id": "19bdbde4-f7f5-4cd2-a8e5-00dbfac9ad15", "code" : "103" , "descripcion": "Villa Playa",              "capacidad": 6, "precio": 1300000.0},
        ],
    },
    {
        "id": "dab02bbb-28de-4c1c-8ec5-2c518766b7e3",
        "nombre": "Hotel Decameron Isleño",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "San Andres",
        "direccion": "Km 3 vía Sound Bay, San Andres Isla",
        "rating": 4.3,
        "reviews": 850,
        "habitaciones": [
            {"id": "59f34749-0429-4cc5-8bcf-d377c76c6d06", "code" : "101" , "descripcion": "Habitación Todo Incluido",     "capacidad": 2, "precio": 530000.0},
            {"id": "3f41e99f-b245-4102-a0d2-449461db450c", "code" : "102" , "descripcion": "Habitación Deluxe T.I.",       "capacidad": 2, "precio": 700000.0},
            {"id": "be9a6d5b-42f5-459c-9f8c-cd243a002c52", "code" : "103" , "descripcion": "Suite Isleño",                 "capacidad": 4, "precio": 1200000.0},
        ],
    },

    # ════════════════════════════════════════════════════════════════════════
    # MANIZALES  (7 hoteles)
    # ════════════════════════════════════════════════════════════════════════
    {
        "id": "0533ce73-5cf4-4440-9d87-9cb4de0b0b3f",
        "nombre": "Hotel Recinto del Pensamiento",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Manizales",
        "direccion": "Km 11 vía al Magdalena, Manizales",
        "rating": 4.3,
        "reviews": 800,
        "habitaciones": [
            {"id": "a61aae58-86c4-4938-8712-b267946689c8", "code" : "101" , "descripcion": "Cabaña Sencilla",   "capacidad": 2, "precio": 250000.0},
            {"id": "84d96cb7-029e-4cb8-80c5-f65fdc48a642", "code" : "102" , "descripcion": "Cabaña Doble",      "capacidad": 4, "precio": 400000.0},
            {"id": "816b9f19-fbe5-4a6f-b38f-2c133fc28b32", "code" : "103" , "descripcion": "Suite Cafetal",     "capacidad": 4, "precio": 650000.0},
        ],
    },
    {
        "id": "b6892dc3-2458-4c8d-9bd9-5b14c1a16e06",
        "nombre": "Hotel Varuna Manizales",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Manizales",
        "direccion": "Carrera 23 # 66-87, Manizales",
        "rating": 4.4,
        "reviews": 850,
        "habitaciones": [
            {"id": "2b92eef5-0344-4daf-a2ec-ea3815ff3aad", "code" : "101" , "descripcion": "Habitación Estándar",   "capacidad": 2, "precio": 220000.0},
            {"id": "e3602d61-357c-4aac-a471-ed8aa0a978c2", "code" : "102" , "descripcion": "Habitación Superior",   "capacidad": 2, "precio": 310000.0},
            {"id": "5210bbfb-1d4c-41e4-a6c4-4bbd188156fd", "code" : "103" , "descripcion": "Suite Varuna",          "capacidad": 3, "precio": 560000.0},
        ],
    },
    {
        "id": "8f37dc55-8932-4f12-b840-5fd0c2d9f14a",
        "nombre": "Hotel Carretero Manizales",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Manizales",
        "direccion": "Av. Santander # 11-51, Manizales",
        "rating": 4.0,
        "reviews": 750,
        "habitaciones": [
            {"id": "228bd36c-7f82-468b-b9e5-8d6b9ce1d92a", "code" : "101" , "descripcion": "Habitación Sencilla",        "capacidad": 1, "precio": 140000.0},
            {"id": "567021b2-1c31-4654-9fcb-da3d01badc56", "code" : "102" , "descripcion": "Habitación Doble",           "capacidad": 2, "precio": 200000.0},
            {"id": "371eaa64-7415-43c8-a789-b042ae05788f", "code" : "103" , "descripcion": "Habitación Ejecutiva",       "capacidad": 2, "precio": 310000.0},
        ],
    },
    {
        "id": "e751bc79-4262-4750-af23-f8056d9fe116",
        "nombre": "Hotel Estelar El Cable Manizales",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Manizales",
        "direccion": "Carrera 23 # 66-23, El Cable, Manizales",
        "rating": 4.5,
        "reviews": 900,
        "habitaciones": [
            {"id": "25c8c1dc-0816-4f83-b8a8-b67ade0ffa0f", "code" : "101" , "descripcion": "Habitación Confort",    "capacidad": 2, "precio": 280000.0},
            {"id": "e32c7ad0-ce58-4de9-a030-cf893cbb14f3", "code" : "102" , "descripcion": "Habitación Deluxe",     "capacidad": 2, "precio": 380000.0},
            {"id": "7e44ef3b-b267-4dd2-8cdf-c42c954a94cf", "code" : "103" , "descripcion": "Suite Estelar",         "capacidad": 4, "precio": 690000.0},
        ],
    },
    {
        "id": "6555b91c-f59d-46ae-9b25-6ecfc744c148",
        "nombre": "Hotel Termales del Ruiz",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Manizales",
        "direccion": "Carretera al Nevado del Ruiz Km 22, Manizales",
        "rating": 4.6,
        "reviews": 850,
        "habitaciones": [
            {"id": "df0617dd-340c-4b28-b904-c4e159d9ad6e", "code" : "101" , "descripcion": "Cabaña Termal Sencilla",  "capacidad": 2, "precio": 320000.0},
            {"id": "8d429456-a56e-4418-917a-de3f5615df4d", "code" : "102" , "descripcion": "Cabaña Termal Doble",     "capacidad": 4, "precio": 500000.0},
            {"id": "7186cfb3-6fd8-4916-b7b6-7436678b2fce", "code" : "103" , "descripcion": "Suite Volcán",            "capacidad": 4, "precio": 850000.0},
        ],
    },
    {
        "id": "ea4a19ea-97ed-4b4e-9171-f428ff7e6a29",
        "nombre": "GHL Hotel Manizales",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Manizales",
        "direccion": "Carrera 22 # 20-20, Manizales",
        "rating": 4.2,
        "reviews": 800,
        "habitaciones": [
            {"id": "a54acc56-bd81-4ebe-bb3e-ffb653aa053c", "code" : "101" , "descripcion": "Habitación Business",   "capacidad": 2, "precio": 230000.0},
            {"id": "cf7c51ee-0a16-4608-b47f-4a70bdde61ba", "code" : "102" , "descripcion": "Habitación Deluxe",     "capacidad": 2, "precio": 340000.0},
            {"id": "26d61b21-d1d4-46e0-901b-72872ea22b5d", "code" : "103" , "descripcion": "Suite GHL",             "capacidad": 3, "precio": 600000.0},
        ],
    },
    {
        "id": "7a4aa60c-fab5-43c4-b234-e1c72f249b18",
        "nombre": "Hotel Las Colinas Manizales",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Manizales",
        "direccion": "Calle 22 # 20-20, Centro, Manizales",
        "rating": 4.1,
        "reviews": 750,
        "habitaciones": [
            {"id": "46f50af3-f0c8-401a-93b1-2f1c17ad36e8", "code" : "101" , "descripcion": "Habitación Sencilla",    "capacidad": 1, "precio": 150000.0},
            {"id": "6c0b7f21-e00e-4801-bd3e-edb755489be2", "code" : "102" , "descripcion": "Habitación Doble",       "capacidad": 2, "precio": 230000.0},
            {"id": "58f2f88e-43ab-48c9-981e-9345d4f0d7e4", "code" : "103" , "descripcion": "Habitación Familiar",    "capacidad": 4, "precio": 380000.0},
        ],
    },

    # ════════════════════════════════════════════════════════════════════════
    # VILLA DE LEYVA  (7 hoteles)
    # ════════════════════════════════════════════════════════════════════════
    {
        "id": "f46f0dbe-5f49-4073-9434-60a830777db4",
        "nombre": "Hotel Mesón de los Virreyes",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Villa de Leyva",
        "direccion": "Carrera 9 # 9-35, Plaza Mayor, Villa de Leyva",
        "rating": 4.7,
        "reviews": 950,
        "habitaciones": [
            {"id": "81ca4fe3-50b8-4bb0-9cf1-28da9b699c57", "code" : "101" , "descripcion": "Habitación Colonial Sencilla", "capacidad": 1, "precio": 180000.0},
            {"id": "159be8df-361e-40ff-b14a-af736649986d", "code" : "102" , "descripcion": "Habitación Colonial Doble",    "capacidad": 2, "precio": 290000.0},
            {"id": "fdc9531e-2c44-4eb9-8b3a-48e8f94086bb", "code" : "103" , "descripcion": "Suite Colonial",              "capacidad": 3, "precio": 520000.0},
        ],
    },
    {
        "id": "7e568af0-e961-47ae-a8ca-c6e98b96bb57",
        "nombre": "Posada de San Antonio Villa de Leyva",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Villa de Leyva",
        "direccion": "Calle 13 # 8-53, Villa de Leyva",
        "rating": 4.5,
        "reviews": 900,
        "habitaciones": [
            {"id": "f78733a7-fd0e-4faa-bdea-e6f1a876fd00", "code" : "101" , "descripcion": "Habitación Patio",       "capacidad": 2, "precio": 220000.0},
            {"id": "50d1938f-b1e0-4020-bf82-6e763f47aba8", "code" : "102" , "descripcion": "Habitación Jardín",      "capacidad": 2, "precio": 300000.0},
            {"id": "9edd7d2a-b0c3-4d8f-93b1-8ff79eec220d", "code" : "103" ,  "descripcion": "Suite San Antonio",      "capacidad": 3, "precio": 500000.0},
        ],
    },
    {
        "id": "b9491d5c-4df2-4521-acac-d6bd1a005b7f",
        "nombre": "La Posada de San Jorge",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Villa de Leyva",
        "direccion": "Carrera 9 # 11-34, Villa de Leyva",
        "rating": 4.6,
        "reviews": 850,
        "habitaciones": [
            {"id": "333eee04-67f5-4ff2-bae0-4809d0db4a20", "code" : "101" , "descripcion": "Habitación Colonial",    "capacidad": 2, "precio": 240000.0},
            {"id": "52230ad1-3d75-4c5d-a2ee-147e1c6f35de", "code" : "102" , "descripcion": "Suite Hacienda",         "capacidad": 3, "precio": 420000.0},
            {"id": "3194c709-b376-4694-b2f7-a655e5a0cdbb", "code" : "103" , "descripcion": "Suite Presidencial",     "capacidad": 4, "precio": 750000.0},
        ],
    },
    {
        "id": "5b2a8073-523c-4aba-94c0-c263e1b3575d",
        "nombre": "Hospedería Renacer",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Villa de Leyva",
        "direccion": "Calle 12 # 9-21, Villa de Leyva",
        "rating": 4.3,
        "reviews": 800,
        "habitaciones": [
            {"id": "c80bbf13-cad0-4d71-b3ed-9d3dc44e48ff", "code" : "101" , "descripcion": "Habitación Renacer",     "capacidad": 2, "precio": 200000.0},
            {"id": "ad28cafe-6133-41ca-afdd-7d4b4e5d2562", "code" : "102" , "descripcion": "Habitación Superior",    "capacidad": 2, "precio": 280000.0},
            {"id": "4479c80b-459b-4f26-ae91-103aedba014e", "code" : "103" , "descripcion": "Suite Renacer",          "capacidad": 4, "precio": 480000.0},
        ],
    },
    {
        "id": "30dec8f0-6f56-4802-8198-3a0c4ed2d280",
        "nombre": "Hotel Boutique Plaza Mayor Villa de Leyva",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Villa de Leyva",
        "direccion": "Calle 13 # 7-58, Plaza Mayor, Villa de Leyva",
        "rating": 4.8,
        "reviews": 950,
        "habitaciones": [
            {"id": "5b6aa1c7-f533-49da-b0ed-a606bfa26f73", "code" : "101" , "descripcion": "Habitación Plaza",           "capacidad": 2, "precio": 310000.0},
            {"id": "ebacdcfe-7865-4f12-8473-da86ba1d0687", "code" : "102" , "descripcion": "Suite Vista a la Plaza",     "capacidad": 2, "precio": 520000.0},
            {"id": "99fe1504-3eda-4704-a755-493dde16ab22", "code" : "103" , "descripcion": "Suite Presidencial Plaza",   "capacidad": 4, "precio": 900000.0},
        ],
    },
    {
        "id": "80a879cd-ca1e-481b-aeb7-2792144c95a8",
        "nombre": "Posada Campanario Villa de Leyva",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Villa de Leyva",
        "direccion": "Vereda Sachica Km 2, Villa de Leyva",
        "rating": 4.4,
        "reviews": 800,
        "habitaciones": [
            {"id": "0bda2ecd-6583-41f7-b05d-3ab77f125489", "code" : "101" , "descripcion": "Cabaña Campo Sencilla",  "capacidad": 2, "precio": 190000.0},
            {"id": "8052d126-6836-42c7-9949-877b7e3dd4e6", "code" : "102" , "descripcion": "Cabaña Campo Doble",     "capacidad": 4, "precio": 330000.0},
            {"id": "5a8fcf14-ba1f-49e0-a6d8-295d213c6703", "code" : "103" , "descripcion": "Suite Campanario",       "capacidad": 4, "precio": 580000.0},
        ],
    },
    {
        "id": "42663bab-43bb-47f3-bd69-96af05b7c8f0",
        "nombre": "Hotel Casa de los Pájaros",
        "pais": "Colombia", "countryCode" : "CO",
        "ciudad": "Villa de Leyva",
        "direccion": "Carrera 10 # 13-20, Villa de Leyva",
        "rating": 4.5,
        "reviews": 850,
        "habitaciones": [
            {"id": "8e1f3317-6b65-4598-80fb-7454b8fb505b", "code" : "101" , "descripcion": "Habitación Nido",         "capacidad": 2, "precio": 250000.0},
            {"id": "c39f51df-faaf-4871-a237-a685fce141c9", "code" : "102" , "descripcion": "Habitación Jardín",       "capacidad": 2, "precio": 340000.0},
            {"id": "c12b526c-9b12-452d-a9fd-416bdb1a5233", "code" : "103" , "descripcion": "Suite Pájaros",           "capacidad": 3, "precio": 560000.0},
        ],
    },
]


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
            CountryORM.__table__.create(bind=db.engine, checkfirst=True)

            # Primero borramos habitaciones por la FK
            HabitacionORM.query.delete()
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
                hospedaje = HospedajeORM(
                    nombre=data["nombre"],
                    countryCode = data["countryCode"],
                    pais=data["pais"],
                    ciudad=data["ciudad"],
                    direccion=data["direccion"],
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
                        propiedad_id=hospedaje.id,
                        code=hab["code"],
                        descripcion=hab["descripcion"],
                        capacidad=hab["capacidad"],
                        precio=hab["precio"],
                    )
                    db.session.add(habitacion)
                    habitaciones_insertadas += 1

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
