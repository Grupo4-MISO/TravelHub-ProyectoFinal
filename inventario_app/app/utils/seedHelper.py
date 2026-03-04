from app.db.models import db, HospedajeORM, HabitacionORM

# ---------------------------------------------------------------------------
# Datos de hoteles representativos en Colombia — 7 hoteles por ciudad
# Ciudades: Bogotá, Medellín, Cartagena, Cali, Santa Marta,
#           Barranquilla, San Andrés, Manizales, Villa de Leyva
# ---------------------------------------------------------------------------
HOSPEDAJES_SEED = [

    # ════════════════════════════════════════════════════════════════════════
    # BOGOTÁ  (7 hoteles)
    # ════════════════════════════════════════════════════════════════════════
    {
        "nombre": "Hotel Casa Medina",
        "pais": "Colombia",
        "ciudad": "Bogotá",
        "direccion": "Carrera 7 # 69A-22, Chapinero, Bogotá",
        "rating": 4.8,
        "habitaciones": [
            {"descripcion": "Habitación Estándar Doble", "capacidad": 2, "precio": 380000.0},
            {"descripcion": "Suite Junior",              "capacidad": 2, "precio": 620000.0},
            {"descripcion": "Suite Presidencial",        "capacidad": 4, "precio": 1200000.0},
        ],
    },
    {
        "nombre": "Sofitel Bogotá Victoria Regia",
        "pais": "Colombia",
        "ciudad": "Bogotá",
        "direccion": "Calle 98 # 9A-03, Chicó, Bogotá",
        "rating": 4.7,
        "habitaciones": [
            {"descripcion": "Habitación Clásica",  "capacidad": 2, "precio": 450000.0},
            {"descripcion": "Habitación Superior", "capacidad": 2, "precio": 550000.0},
            {"descripcion": "Suite Luxury",         "capacidad": 3, "precio": 980000.0},
        ],
    },
    {
        "nombre": "Hotel Tequendama",
        "pais": "Colombia",
        "ciudad": "Bogotá",
        "direccion": "Carrera 10 # 26-21, Centro, Bogotá",
        "rating": 4.2,
        "habitaciones": [
            {"descripcion": "Habitación Sencilla",        "capacidad": 1, "precio": 180000.0},
            {"descripcion": "Habitación Doble Estándar",  "capacidad": 2, "precio": 260000.0},
            {"descripcion": "Suite Ejecutiva",            "capacidad": 2, "precio": 520000.0},
        ],
    },
    {
        "nombre": "Hotel B.O.G",
        "pais": "Colombia",
        "ciudad": "Bogotá",
        "direccion": "Calle 11 # 4-16, La Candelaria, Bogotá",
        "rating": 4.6,
        "habitaciones": [
            {"descripcion": "Habitación Urban",      "capacidad": 2, "precio": 410000.0},
            {"descripcion": "Habitación Deluxe",     "capacidad": 2, "precio": 530000.0},
            {"descripcion": "Suite Rooftop",         "capacidad": 3, "precio": 950000.0},
        ],
    },
    {
        "nombre": "W Bogotá",
        "pais": "Colombia",
        "ciudad": "Bogotá",
        "direccion": "Calle 100 # 8A-01, Chicó, Bogotá",
        "rating": 4.7,
        "habitaciones": [
            {"descripcion": "Wonderful Room",         "capacidad": 2, "precio": 600000.0},
            {"descripcion": "Spectacular Suite",      "capacidad": 2, "precio": 900000.0},
            {"descripcion": "WOW Suite",              "capacidad": 4, "precio": 1800000.0},
        ],
    },
    {
        "nombre": "Hyatt Regency Bogotá",
        "pais": "Colombia",
        "ciudad": "Bogotá",
        "direccion": "Calle 24 # 57A-60, Salitre, Bogotá",
        "rating": 4.5,
        "habitaciones": [
            {"descripcion": "Habitación King Estándar",  "capacidad": 2, "precio": 390000.0},
            {"descripcion": "Habitación Club",           "capacidad": 2, "precio": 520000.0},
            {"descripcion": "Suite Regency",             "capacidad": 3, "precio": 870000.0},
        ],
    },
    {
        "nombre": "Hotel Click Clack Bogotá",
        "pais": "Colombia",
        "ciudad": "Bogotá",
        "direccion": "Carrera 11 # 93-77, Chicó, Bogotá",
        "rating": 4.4,
        "habitaciones": [
            {"descripcion": "Habitación Pequeña",    "capacidad": 1, "precio": 220000.0},
            {"descripcion": "Habitación Mediana",    "capacidad": 2, "precio": 310000.0},
            {"descripcion": "Habitación Grande",     "capacidad": 3, "precio": 460000.0},
        ],
    },

    # ════════════════════════════════════════════════════════════════════════
    # MEDELLÍN  (7 hoteles)
    # ════════════════════════════════════════════════════════════════════════
    {
        "nombre": "Hotel Dann Carlton Medellín",
        "pais": "Colombia",
        "ciudad": "Medellín",
        "direccion": "Calle 1A Sur # 43A-83, El Poblado, Medellín",
        "rating": 4.6,
        "habitaciones": [
            {"descripcion": "Habitación Estándar",  "capacidad": 2, "precio": 320000.0},
            {"descripcion": "Habitación Deluxe",    "capacidad": 2, "precio": 430000.0},
            {"descripcion": "Suite Ejecutiva",      "capacidad": 3, "precio": 750000.0},
        ],
    },
    {
        "nombre": "Intercontinental Medellín",
        "pais": "Colombia",
        "ciudad": "Medellín",
        "direccion": "Calle 16 # 28-51, Laureles, Medellín",
        "rating": 4.5,
        "habitaciones": [
            {"descripcion": "Habitación Club",  "capacidad": 2, "precio": 490000.0},
            {"descripcion": "Suite Junior",     "capacidad": 2, "precio": 680000.0},
            {"descripcion": "Penthouse",        "capacidad": 4, "precio": 1500000.0},
        ],
    },
    {
        "nombre": "Hotel Park 10 Medellín",
        "pais": "Colombia",
        "ciudad": "Medellín",
        "direccion": "Carrera 36D # 10A-22, El Poblado, Medellín",
        "rating": 4.4,
        "habitaciones": [
            {"descripcion": "Habitación Sencilla", "capacidad": 1, "precio": 200000.0},
            {"descripcion": "Habitación Doble",    "capacidad": 2, "precio": 290000.0},
            {"descripcion": "Habitación Triple",   "capacidad": 3, "precio": 370000.0},
        ],
    },
    {
        "nombre": "The Charlee Hotel Medellín",
        "pais": "Colombia",
        "ciudad": "Medellín",
        "direccion": "Carrera 43B # 11-50, El Poblado, Medellín",
        "rating": 4.7,
        "habitaciones": [
            {"descripcion": "Habitación Lifestyle",   "capacidad": 2, "precio": 480000.0},
            {"descripcion": "Suite Rooftop Pool",     "capacidad": 2, "precio": 780000.0},
            {"descripcion": "Suite Presidencial",     "capacidad": 4, "precio": 1600000.0},
        ],
    },
    {
        "nombre": "Hotel Diez Categoría Colombia",
        "pais": "Colombia",
        "ciudad": "Medellín",
        "direccion": "Calle 11A # 32-65, El Poblado, Medellín",
        "rating": 4.5,
        "habitaciones": [
            {"descripcion": "Habitación Estándar",  "capacidad": 2, "precio": 350000.0},
            {"descripcion": "Habitación Superior",  "capacidad": 2, "precio": 460000.0},
            {"descripcion": "Suite Diez",           "capacidad": 3, "precio": 820000.0},
        ],
    },
    {
        "nombre": "Hotel Nutibara Medellín",
        "pais": "Colombia",
        "ciudad": "Medellín",
        "direccion": "Carrera 50 # 52A-28, Centro, Medellín",
        "rating": 4.1,
        "habitaciones": [
            {"descripcion": "Habitación Sencilla",     "capacidad": 1, "precio": 150000.0},
            {"descripcion": "Habitación Doble",        "capacidad": 2, "precio": 210000.0},
            {"descripcion": "Habitación Ejecutiva",    "capacidad": 2, "precio": 320000.0},
        ],
    },
    {
        "nombre": "Hotel Estelar Milla de Oro",
        "pais": "Colombia",
        "ciudad": "Medellín",
        "direccion": "Carrera 43A # 6 Sur-15, El Poblado, Medellín",
        "rating": 4.6,
        "habitaciones": [
            {"descripcion": "Habitación Confort",   "capacidad": 2, "precio": 370000.0},
            {"descripcion": "Habitación Deluxe",    "capacidad": 2, "precio": 500000.0},
            {"descripcion": "Suite Estelar",        "capacidad": 4, "precio": 900000.0},
        ],
    },

    # ════════════════════════════════════════════════════════════════════════
    # CARTAGENA  (7 hoteles)
    # ════════════════════════════════════════════════════════════════════════
    {
        "nombre": "Hotel Charleston Santa Teresa",
        "pais": "Colombia",
        "ciudad": "Cartagena",
        "direccion": "Plaza de Santa Teresa, Centro Histórico, Cartagena",
        "rating": 4.9,
        "habitaciones": [
            {"descripcion": "Habitación Colonial",      "capacidad": 2, "precio": 650000.0},
            {"descripcion": "Suite Panorámica Mar",     "capacidad": 2, "precio": 1100000.0},
            {"descripcion": "Suite Real",               "capacidad": 4, "precio": 2200000.0},
        ],
    },
    {
        "nombre": "Sofitel Legend Santa Clara",
        "pais": "Colombia",
        "ciudad": "Cartagena",
        "direccion": "Calle del Torno # 39-29, Centro Histórico, Cartagena",
        "rating": 4.9,
        "habitaciones": [
            {"descripcion": "Habitación Clásica Patio",   "capacidad": 2, "precio": 720000.0},
            {"descripcion": "Habitación Deluxe Piscina",  "capacidad": 2, "precio": 950000.0},
            {"descripcion": "Suite Legend",               "capacidad": 3, "precio": 1800000.0},
        ],
    },
    {
        "nombre": "Hotel Movich Cartagena de Indias",
        "pais": "Colombia",
        "ciudad": "Cartagena",
        "direccion": "Bocagrande, Carrera 3 # 8-129, Cartagena",
        "rating": 4.3,
        "habitaciones": [
            {"descripcion": "Habitación Estándar",    "capacidad": 2, "precio": 310000.0},
            {"descripcion": "Habitación Vista al Mar","capacidad": 2, "precio": 480000.0},
            {"descripcion": "Suite Familiar",         "capacidad": 5, "precio": 820000.0},
        ],
    },
    {
        "nombre": "Bastión Luxury Hotel",
        "pais": "Colombia",
        "ciudad": "Cartagena",
        "direccion": "Calle del Guerrero # 29-10, Centro Histórico, Cartagena",
        "rating": 4.8,
        "habitaciones": [
            {"descripcion": "Habitación Deluxe Patio",  "capacidad": 2, "precio": 680000.0},
            {"descripcion": "Suite Bastión",            "capacidad": 2, "precio": 1050000.0},
            {"descripcion": "Suite Gran Bastión",       "capacidad": 4, "precio": 2000000.0},
        ],
    },
    {
        "nombre": "Hotel Caribe by Faranda",
        "pais": "Colombia",
        "ciudad": "Cartagena",
        "direccion": "Carrera 1 # 2-87, Bocagrande, Cartagena",
        "rating": 4.2,
        "habitaciones": [
            {"descripcion": "Habitación Estándar Jardín", "capacidad": 2, "precio": 270000.0},
            {"descripcion": "Habitación Vista al Mar",    "capacidad": 2, "precio": 380000.0},
            {"descripcion": "Suite Caribe",               "capacidad": 4, "precio": 750000.0},
        ],
    },
    {
        "nombre": "Almirante Cartagena Hotel",
        "pais": "Colombia",
        "ciudad": "Cartagena",
        "direccion": "Av. San Martín # 4-33, Bocagrande, Cartagena",
        "rating": 4.1,
        "habitaciones": [
            {"descripcion": "Habitación Sencilla",   "capacidad": 1, "precio": 210000.0},
            {"descripcion": "Habitación Doble",      "capacidad": 2, "precio": 300000.0},
            {"descripcion": "Suite Superior",        "capacidad": 3, "precio": 580000.0},
        ],
    },
    {
        "nombre": "El Marqués Hotel Boutique",
        "pais": "Colombia",
        "ciudad": "Cartagena",
        "direccion": "Calle 33 # 3-67, Getsemaní, Cartagena",
        "rating": 4.5,
        "habitaciones": [
            {"descripcion": "Habitación Getsemaní",  "capacidad": 2, "precio": 340000.0},
            {"descripcion": "Suite Marqués",         "capacidad": 2, "precio": 560000.0},
            {"descripcion": "Suite Familiar",        "capacidad": 4, "precio": 920000.0},
        ],
    },

    # ════════════════════════════════════════════════════════════════════════
    # CALI  (7 hoteles)
    # ════════════════════════════════════════════════════════════════════════
    {
        "nombre": "Hotel Dann Carlton Cali",
        "pais": "Colombia",
        "ciudad": "Cali",
        "direccion": "Avenida Colombia # 2-72, Cali",
        "rating": 4.4,
        "habitaciones": [
            {"descripcion": "Habitación Estándar Sencilla", "capacidad": 1, "precio": 190000.0},
            {"descripcion": "Habitación Estándar Doble",    "capacidad": 2, "precio": 280000.0},
            {"descripcion": "Suite Ejecutiva",              "capacidad": 2, "precio": 560000.0},
        ],
    },
    {
        "nombre": "GHL Hotel Collection Palma Real",
        "pais": "Colombia",
        "ciudad": "Cali",
        "direccion": "Calle 19A Norte # 8N-40, Cali",
        "rating": 4.3,
        "habitaciones": [
            {"descripcion": "Habitación Business",  "capacidad": 2, "precio": 240000.0},
            {"descripcion": "Habitación Deluxe",    "capacidad": 2, "precio": 360000.0},
            {"descripcion": "Suite Junior",         "capacidad": 3, "precio": 620000.0},
        ],
    },
    {
        "nombre": "Hotel Spiwak Chipichape",
        "pais": "Colombia",
        "ciudad": "Cali",
        "direccion": "Carrera 1B # 66-200, Chipichape, Cali",
        "rating": 4.5,
        "habitaciones": [
            {"descripcion": "Habitación Superior",  "capacidad": 2, "precio": 310000.0},
            {"descripcion": "Habitación Deluxe",    "capacidad": 2, "precio": 420000.0},
            {"descripcion": "Suite Spiwak",         "capacidad": 4, "precio": 780000.0},
        ],
    },
    {
        "nombre": "Estelar Belmonte Cali",
        "pais": "Colombia",
        "ciudad": "Cali",
        "direccion": "Calle 16A Norte # 4N-62, Normandía, Cali",
        "rating": 4.4,
        "habitaciones": [
            {"descripcion": "Habitación Confort",   "capacidad": 2, "precio": 270000.0},
            {"descripcion": "Habitación Superior",  "capacidad": 2, "precio": 370000.0},
            {"descripcion": "Suite Estelar",        "capacidad": 3, "precio": 650000.0},
        ],
    },
    {
        "nombre": "Hotel Camino Real Cali",
        "pais": "Colombia",
        "ciudad": "Cali",
        "direccion": "Av. Colombia # 7-38, Granada, Cali",
        "rating": 4.0,
        "habitaciones": [
            {"descripcion": "Habitación Sencilla",       "capacidad": 1, "precio": 160000.0},
            {"descripcion": "Habitación Doble Estándar", "capacidad": 2, "precio": 230000.0},
            {"descripcion": "Habitación Familiar",       "capacidad": 4, "precio": 390000.0},
        ],
    },
    {
        "nombre": "Hotel Boutique Bello Horizonte Cali",
        "pais": "Colombia",
        "ciudad": "Cali",
        "direccion": "Calle 5B # 36A-27, San Fernando, Cali",
        "rating": 4.6,
        "habitaciones": [
            {"descripcion": "Habitación Jardín",     "capacidad": 2, "precio": 290000.0},
            {"descripcion": "Habitación Piscina",    "capacidad": 2, "precio": 380000.0},
            {"descripcion": "Suite Bello Horizonte", "capacidad": 3, "precio": 680000.0},
        ],
    },
    {
        "nombre": "Hotel Casa Republicana Cali",
        "pais": "Colombia",
        "ciudad": "Cali",
        "direccion": "Carrera 6 # 8-13, Centro Histórico, Cali",
        "rating": 4.2,
        "habitaciones": [
            {"descripcion": "Habitación Colonial",   "capacidad": 2, "precio": 220000.0},
            {"descripcion": "Suite Colonial",        "capacidad": 3, "precio": 420000.0},
            {"descripcion": "Suite Presidencial",    "capacidad": 4, "precio": 750000.0},
        ],
    },

    # ════════════════════════════════════════════════════════════════════════
    # SANTA MARTA  (7 hoteles)
    # ════════════════════════════════════════════════════════════════════════
    {
        "nombre": "Hotel Zuana Beach Resort",
        "pais": "Colombia",
        "ciudad": "Santa Marta",
        "direccion": "Carrera 2 # 6-10, El Rodadero, Santa Marta",
        "rating": 4.5,
        "habitaciones": [
            {"descripcion": "Habitación Estándar",    "capacidad": 2, "precio": 350000.0},
            {"descripcion": "Suite Frente al Mar",    "capacidad": 2, "precio": 600000.0},
            {"descripcion": "Suite Familiar",         "capacidad": 5, "precio": 900000.0},
        ],
    },
    {
        "nombre": "Casa Loma Hotel Boutique",
        "pais": "Colombia",
        "ciudad": "Santa Marta",
        "direccion": "Carrera 20 # 3-69, Centro Histórico, Santa Marta",
        "rating": 4.6,
        "habitaciones": [
            {"descripcion": "Habitación Jardín",      "capacidad": 2, "precio": 280000.0},
            {"descripcion": "Habitación Vista Ciudad","capacidad": 2, "precio": 340000.0},
            {"descripcion": "Suite Penthouse",        "capacidad": 3, "precio": 780000.0},
        ],
    },
    {
        "nombre": "Irotama Resort Santa Marta",
        "pais": "Colombia",
        "ciudad": "Santa Marta",
        "direccion": "Km 14 vía Santa Marta-Barranquilla, Santa Marta",
        "rating": 4.4,
        "habitaciones": [
            {"descripcion": "Cabaña Estándar",        "capacidad": 2, "precio": 400000.0},
            {"descripcion": "Cabaña Frente al Mar",   "capacidad": 4, "precio": 680000.0},
            {"descripcion": "Suite VIP Playa",        "capacidad": 4, "precio": 1100000.0},
        ],
    },
    {
        "nombre": "La Sierra Hotel El Rodadero",
        "pais": "Colombia",
        "ciudad": "Santa Marta",
        "direccion": "Carrera 1A # 9-47, El Rodadero, Santa Marta",
        "rating": 4.3,
        "habitaciones": [
            {"descripcion": "Habitación Sencilla",     "capacidad": 1, "precio": 190000.0},
            {"descripcion": "Habitación Vista Mar",    "capacidad": 2, "precio": 320000.0},
            {"descripcion": "Suite Familiar",          "capacidad": 5, "precio": 620000.0},
        ],
    },
    {
        "nombre": "Tamacá Beach Resort Hotel",
        "pais": "Colombia",
        "ciudad": "Santa Marta",
        "direccion": "Carrera 2 # 11A-98, El Rodadero, Santa Marta",
        "rating": 4.2,
        "habitaciones": [
            {"descripcion": "Habitación Playa",        "capacidad": 2, "precio": 310000.0},
            {"descripcion": "Suite Coral",             "capacidad": 3, "precio": 520000.0},
            {"descripcion": "Suite Presidencial Mar",  "capacidad": 4, "precio": 850000.0},
        ],
    },
    {
        "nombre": "Hotel Bello Horizonte Santa Marta",
        "pais": "Colombia",
        "ciudad": "Santa Marta",
        "direccion": "Carrera 2 # 11-24, El Rodadero, Santa Marta",
        "rating": 4.1,
        "habitaciones": [
            {"descripcion": "Habitación Económica",   "capacidad": 2, "precio": 180000.0},
            {"descripcion": "Habitación Doble",       "capacidad": 2, "precio": 260000.0},
            {"descripcion": "Habitación Triple",      "capacidad": 3, "precio": 350000.0},
        ],
    },
    {
        "nombre": "Hotel Boutique La Tortuga",
        "pais": "Colombia",
        "ciudad": "Santa Marta",
        "direccion": "Calle 18 # 3-26, Centro Histórico, Santa Marta",
        "rating": 4.7,
        "habitaciones": [
            {"descripcion": "Habitación Deluxe",      "capacidad": 2, "precio": 360000.0},
            {"descripcion": "Suite Caribe",           "capacidad": 2, "precio": 580000.0},
            {"descripcion": "Suite La Tortuga",       "capacidad": 4, "precio": 960000.0},
        ],
    },

    # ════════════════════════════════════════════════════════════════════════
    # BARRANQUILLA  (7 hoteles)
    # ════════════════════════════════════════════════════════════════════════
    {
        "nombre": "Hotel El Prado",
        "pais": "Colombia",
        "ciudad": "Barranquilla",
        "direccion": "Carrera 54 # 70-10, El Prado, Barranquilla",
        "rating": 4.4,
        "habitaciones": [
            {"descripcion": "Habitación Clásica",    "capacidad": 2, "precio": 220000.0},
            {"descripcion": "Habitación Superior",   "capacidad": 2, "precio": 320000.0},
            {"descripcion": "Suite Gran Prado",      "capacidad": 4, "precio": 700000.0},
        ],
    },
    {
        "nombre": "GHL Hotel Barranquilla",
        "pais": "Colombia",
        "ciudad": "Barranquilla",
        "direccion": "Carrera 52 # 75-30, Barranquilla",
        "rating": 4.2,
        "habitaciones": [
            {"descripcion": "Habitación Estándar",   "capacidad": 2, "precio": 200000.0},
            {"descripcion": "Habitación Ejecutiva",  "capacidad": 2, "precio": 300000.0},
            {"descripcion": "Suite Ejecutiva",       "capacidad": 3, "precio": 550000.0},
        ],
    },
    {
        "nombre": "Hotel Dann Carlton Barranquilla",
        "pais": "Colombia",
        "ciudad": "Barranquilla",
        "direccion": "Carrera 50 # 80-41, El Nogal, Barranquilla",
        "rating": 4.5,
        "habitaciones": [
            {"descripcion": "Habitación Confort",    "capacidad": 2, "precio": 260000.0},
            {"descripcion": "Habitación Deluxe",     "capacidad": 2, "precio": 370000.0},
            {"descripcion": "Suite Carlton",         "capacidad": 3, "precio": 720000.0},
        ],
    },
    {
        "nombre": "Sonesta Hotel Barranquilla",
        "pais": "Colombia",
        "ciudad": "Barranquilla",
        "direccion": "Calle 106 # 50-48, Barranquilla",
        "rating": 4.3,
        "habitaciones": [
            {"descripcion": "Habitación Estándar",   "capacidad": 2, "precio": 240000.0},
            {"descripcion": "Habitación Superior",   "capacidad": 2, "precio": 340000.0},
            {"descripcion": "Suite Sonesta",         "capacidad": 4, "precio": 680000.0},
        ],
    },
    {
        "nombre": "Holiday Inn Barranquilla",
        "pais": "Colombia",
        "ciudad": "Barranquilla",
        "direccion": "Carrera 54 # 59-45, Barranquilla",
        "rating": 4.1,
        "habitaciones": [
            {"descripcion": "Habitación Estándar",      "capacidad": 2, "precio": 210000.0},
            {"descripcion": "Habitación Ejecutiva",     "capacidad": 2, "precio": 290000.0},
            {"descripcion": "Suite Familiar",           "capacidad": 4, "precio": 500000.0},
        ],
    },
    {
        "nombre": "Estelar Barranquilla Hotel",
        "pais": "Colombia",
        "ciudad": "Barranquilla",
        "direccion": "Carrera 53 # 98-228, Barranquilla",
        "rating": 4.4,
        "habitaciones": [
            {"descripcion": "Habitación Confort",    "capacidad": 2, "precio": 250000.0},
            {"descripcion": "Habitación Deluxe",     "capacidad": 2, "precio": 360000.0},
            {"descripcion": "Suite Estelar",         "capacidad": 3, "precio": 640000.0},
        ],
    },
    {
        "nombre": "Hotel Movich Buró 26 Barranquilla",
        "pais": "Colombia",
        "ciudad": "Barranquilla",
        "direccion": "Carrera 53B # 26-21, Barranquilla",
        "rating": 4.3,
        "habitaciones": [
            {"descripcion": "Habitación Smart",      "capacidad": 1, "precio": 180000.0},
            {"descripcion": "Habitación Business",   "capacidad": 2, "precio": 280000.0},
            {"descripcion": "Suite Movich",          "capacidad": 3, "precio": 530000.0},
        ],
    },

    # ════════════════════════════════════════════════════════════════════════
    # SAN ANDRÉS  (7 hoteles)
    # ════════════════════════════════════════════════════════════════════════
    {
        "nombre": "Hotel Decameron San Luis",
        "pais": "Colombia",
        "ciudad": "San Andrés",
        "direccion": "Km 13 vía San Luis, San Andrés Isla",
        "rating": 4.5,
        "habitaciones": [
            {"descripcion": "Habitación Estándar Todo Incluido",  "capacidad": 2, "precio": 580000.0},
            {"descripcion": "Habitación Superior Vista al Mar",   "capacidad": 2, "precio": 780000.0},
            {"descripcion": "Suite Caribe",                       "capacidad": 4, "precio": 1400000.0},
        ],
    },
    {
        "nombre": "Casa Harb Hotel Boutique",
        "pais": "Colombia",
        "ciudad": "San Andrés",
        "direccion": "Av. Colombia # 3-59, San Andrés Isla",
        "rating": 4.6,
        "habitaciones": [
            {"descripcion": "Habitación Coral",               "capacidad": 2, "precio": 420000.0},
            {"descripcion": "Habitación Mar de Siete Colores","capacidad": 2, "precio": 600000.0},
            {"descripcion": "Suite Isla",                     "capacidad": 3, "precio": 950000.0},
        ],
    },
    {
        "nombre": "Hotel Sunrise Beach San Andrés",
        "pais": "Colombia",
        "ciudad": "San Andrés",
        "direccion": "Av. Colombia # 1A-104, San Andrés Isla",
        "rating": 4.3,
        "habitaciones": [
            {"descripcion": "Habitación Playa",         "capacidad": 2, "precio": 360000.0},
            {"descripcion": "Suite Amanecer Mar",       "capacidad": 2, "precio": 560000.0},
            {"descripcion": "Suite Familiar Sunrise",   "capacidad": 5, "precio": 920000.0},
        ],
    },
    {
        "nombre": "Hotel Lord Pierre San Andrés",
        "pais": "Colombia",
        "ciudad": "San Andrés",
        "direccion": "Av. 20 de Julio # 3-88, San Andrés Isla",
        "rating": 4.0,
        "habitaciones": [
            {"descripcion": "Habitación Estándar",       "capacidad": 2, "precio": 290000.0},
            {"descripcion": "Habitación Vista al Mar",   "capacidad": 2, "precio": 400000.0},
            {"descripcion": "Suite Lord Pierre",         "capacidad": 3, "precio": 680000.0},
        ],
    },
    {
        "nombre": "Portobelo Hotel San Andrés",
        "pais": "Colombia",
        "ciudad": "San Andrés",
        "direccion": "Carretera Circunvalar Km 2, San Andrés Isla",
        "rating": 4.2,
        "habitaciones": [
            {"descripcion": "Habitación Jardín Tropical","capacidad": 2, "precio": 310000.0},
            {"descripcion": "Habitación Piscina",        "capacidad": 2, "precio": 440000.0},
            {"descripcion": "Suite Portobelo",           "capacidad": 4, "precio": 780000.0},
        ],
    },
    {
        "nombre": "Cocoplum Beach Hotel",
        "pais": "Colombia",
        "ciudad": "San Andrés",
        "direccion": "North End, San Andrés Isla",
        "rating": 4.4,
        "habitaciones": [
            {"descripcion": "Habitación Coconut",       "capacidad": 2, "precio": 380000.0},
            {"descripcion": "Suite Ocean View",         "capacidad": 2, "precio": 620000.0},
            {"descripcion": "Villa Playa",              "capacidad": 6, "precio": 1300000.0},
        ],
    },
    {
        "nombre": "Hotel Decameron Isleño",
        "pais": "Colombia",
        "ciudad": "San Andrés",
        "direccion": "Km 3 vía Sound Bay, San Andrés Isla",
        "rating": 4.3,
        "habitaciones": [
            {"descripcion": "Habitación Todo Incluido",     "capacidad": 2, "precio": 530000.0},
            {"descripcion": "Habitación Deluxe T.I.",       "capacidad": 2, "precio": 700000.0},
            {"descripcion": "Suite Isleño",                 "capacidad": 4, "precio": 1200000.0},
        ],
    },

    # ════════════════════════════════════════════════════════════════════════
    # MANIZALES  (7 hoteles)
    # ════════════════════════════════════════════════════════════════════════
    {
        "nombre": "Hotel Recinto del Pensamiento",
        "pais": "Colombia",
        "ciudad": "Manizales",
        "direccion": "Km 11 vía al Magdalena, Manizales",
        "rating": 4.3,
        "habitaciones": [
            {"descripcion": "Cabaña Sencilla",   "capacidad": 2, "precio": 250000.0},
            {"descripcion": "Cabaña Doble",      "capacidad": 4, "precio": 400000.0},
            {"descripcion": "Suite Cafetal",     "capacidad": 4, "precio": 650000.0},
        ],
    },
    {
        "nombre": "Hotel Varuna Manizales",
        "pais": "Colombia",
        "ciudad": "Manizales",
        "direccion": "Carrera 23 # 66-87, Manizales",
        "rating": 4.4,
        "habitaciones": [
            {"descripcion": "Habitación Estándar",   "capacidad": 2, "precio": 220000.0},
            {"descripcion": "Habitación Superior",   "capacidad": 2, "precio": 310000.0},
            {"descripcion": "Suite Varuna",          "capacidad": 3, "precio": 560000.0},
        ],
    },
    {
        "nombre": "Hotel Carretero Manizales",
        "pais": "Colombia",
        "ciudad": "Manizales",
        "direccion": "Av. Santander # 11-51, Manizales",
        "rating": 4.0,
        "habitaciones": [
            {"descripcion": "Habitación Sencilla",        "capacidad": 1, "precio": 140000.0},
            {"descripcion": "Habitación Doble",           "capacidad": 2, "precio": 200000.0},
            {"descripcion": "Habitación Ejecutiva",       "capacidad": 2, "precio": 310000.0},
        ],
    },
    {
        "nombre": "Hotel Estelar El Cable Manizales",
        "pais": "Colombia",
        "ciudad": "Manizales",
        "direccion": "Carrera 23 # 66-23, El Cable, Manizales",
        "rating": 4.5,
        "habitaciones": [
            {"descripcion": "Habitación Confort",    "capacidad": 2, "precio": 280000.0},
            {"descripcion": "Habitación Deluxe",     "capacidad": 2, "precio": 380000.0},
            {"descripcion": "Suite Estelar",         "capacidad": 4, "precio": 690000.0},
        ],
    },
    {
        "nombre": "Hotel Termales del Ruiz",
        "pais": "Colombia",
        "ciudad": "Manizales",
        "direccion": "Carretera al Nevado del Ruiz Km 22, Manizales",
        "rating": 4.6,
        "habitaciones": [
            {"descripcion": "Cabaña Termal Sencilla",  "capacidad": 2, "precio": 320000.0},
            {"descripcion": "Cabaña Termal Doble",     "capacidad": 4, "precio": 500000.0},
            {"descripcion": "Suite Volcán",            "capacidad": 4, "precio": 850000.0},
        ],
    },
    {
        "nombre": "GHL Hotel Manizales",
        "pais": "Colombia",
        "ciudad": "Manizales",
        "direccion": "Carrera 22 # 20-20, Manizales",
        "rating": 4.2,
        "habitaciones": [
            {"descripcion": "Habitación Business",   "capacidad": 2, "precio": 230000.0},
            {"descripcion": "Habitación Deluxe",     "capacidad": 2, "precio": 340000.0},
            {"descripcion": "Suite GHL",             "capacidad": 3, "precio": 600000.0},
        ],
    },
    {
        "nombre": "Hotel Las Colinas Manizales",
        "pais": "Colombia",
        "ciudad": "Manizales",
        "direccion": "Calle 22 # 20-20, Centro, Manizales",
        "rating": 4.1,
        "habitaciones": [
            {"descripcion": "Habitación Sencilla",    "capacidad": 1, "precio": 150000.0},
            {"descripcion": "Habitación Doble",       "capacidad": 2, "precio": 230000.0},
            {"descripcion": "Habitación Familiar",    "capacidad": 4, "precio": 380000.0},
        ],
    },

    # ════════════════════════════════════════════════════════════════════════
    # VILLA DE LEYVA  (7 hoteles)
    # ════════════════════════════════════════════════════════════════════════
    {
        "nombre": "Hotel Mesón de los Virreyes",
        "pais": "Colombia",
        "ciudad": "Villa de Leyva",
        "direccion": "Carrera 9 # 9-35, Plaza Mayor, Villa de Leyva",
        "rating": 4.7,
        "habitaciones": [
            {"descripcion": "Habitación Colonial Sencilla", "capacidad": 1, "precio": 180000.0},
            {"descripcion": "Habitación Colonial Doble",    "capacidad": 2, "precio": 290000.0},
            {"descripcion": "Suite Colonial",              "capacidad": 3, "precio": 520000.0},
        ],
    },
    {
        "nombre": "Posada de San Antonio Villa de Leyva",
        "pais": "Colombia",
        "ciudad": "Villa de Leyva",
        "direccion": "Calle 13 # 8-53, Villa de Leyva",
        "rating": 4.5,
        "habitaciones": [
            {"descripcion": "Habitación Patio",       "capacidad": 2, "precio": 220000.0},
            {"descripcion": "Habitación Jardín",      "capacidad": 2, "precio": 300000.0},
            {"descripcion": "Suite San Antonio",      "capacidad": 3, "precio": 500000.0},
        ],
    },
    {
        "nombre": "La Posada de San Jorge",
        "pais": "Colombia",
        "ciudad": "Villa de Leyva",
        "direccion": "Carrera 9 # 11-34, Villa de Leyva",
        "rating": 4.6,
        "habitaciones": [
            {"descripcion": "Habitación Colonial",    "capacidad": 2, "precio": 240000.0},
            {"descripcion": "Suite Hacienda",         "capacidad": 3, "precio": 420000.0},
            {"descripcion": "Suite Presidencial",     "capacidad": 4, "precio": 750000.0},
        ],
    },
    {
        "nombre": "Hospedería Renacer",
        "pais": "Colombia",
        "ciudad": "Villa de Leyva",
        "direccion": "Calle 12 # 9-21, Villa de Leyva",
        "rating": 4.3,
        "habitaciones": [
            {"descripcion": "Habitación Renacer",     "capacidad": 2, "precio": 200000.0},
            {"descripcion": "Habitación Superior",    "capacidad": 2, "precio": 280000.0},
            {"descripcion": "Suite Renacer",          "capacidad": 4, "precio": 480000.0},
        ],
    },
    {
        "nombre": "Hotel Boutique Plaza Mayor Villa de Leyva",
        "pais": "Colombia",
        "ciudad": "Villa de Leyva",
        "direccion": "Calle 13 # 7-58, Plaza Mayor, Villa de Leyva",
        "rating": 4.8,
        "habitaciones": [
            {"descripcion": "Habitación Plaza",           "capacidad": 2, "precio": 310000.0},
            {"descripcion": "Suite Vista a la Plaza",     "capacidad": 2, "precio": 520000.0},
            {"descripcion": "Suite Presidencial Plaza",   "capacidad": 4, "precio": 900000.0},
        ],
    },
    {
        "nombre": "Posada Campanario Villa de Leyva",
        "pais": "Colombia",
        "ciudad": "Villa de Leyva",
        "direccion": "Vereda Sachica Km 2, Villa de Leyva",
        "rating": 4.4,
        "habitaciones": [
            {"descripcion": "Cabaña Campo Sencilla",  "capacidad": 2, "precio": 190000.0},
            {"descripcion": "Cabaña Campo Doble",     "capacidad": 4, "precio": 330000.0},
            {"descripcion": "Suite Campanario",       "capacidad": 4, "precio": 580000.0},
        ],
    },
    {
        "nombre": "Hotel Casa de los Pájaros",
        "pais": "Colombia",
        "ciudad": "Villa de Leyva",
        "direccion": "Carrera 10 # 13-20, Villa de Leyva",
        "rating": 4.5,
        "habitaciones": [
            {"descripcion": "Habitación Nido",         "capacidad": 2, "precio": 250000.0},
            {"descripcion": "Habitación Jardín",       "capacidad": 2, "precio": 340000.0},
            {"descripcion": "Suite Pájaros",           "capacidad": 3, "precio": 560000.0},
        ],
    },
]


class SeedHelper:
    """Herramienta para poblar y restablecer las tablas de hospedajes y habitaciones."""

    @staticmethod
    def reset_and_seed():
        """
        Elimina todos los registros existentes de habitaciones y hospedajes,
        luego inserta los datos de seed definidos en HOSPEDAJES_SEED.

        Returns:
            dict con el resumen de registros insertados o un mensaje de error.
        """
        try:
            # Primero borramos habitaciones por la FK
            HabitacionORM.query.delete()
            HospedajeORM.query.delete()
            db.session.flush()

            hospedajes_insertados = 0
            habitaciones_insertadas = 0

            for data in HOSPEDAJES_SEED:
                hospedaje = HospedajeORM(
                    nombre=data["nombre"],
                    pais=data["pais"],
                    ciudad=data["ciudad"],
                    direccion=data["direccion"],
                    rating=data["rating"],
                )
                db.session.add(hospedaje)
                db.session.flush()  # Obtenemos el id antes del commit

                for hab in data["habitaciones"]:
                    habitacion = HabitacionORM(
                        propiedad_id=hospedaje.id,
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
                "hospedajes_insertados": hospedajes_insertados,
                "habitaciones_insertadas": habitaciones_insertadas,
            }

        except Exception as e:
            db.session.rollback()
            return {"ok": False, "error": str(e)}
