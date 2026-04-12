from app.db.models import Review, db
from werkzeug.security import generate_password_hash
import uuid
import random

# ---------------------------------------------------------------------------
# Fallback: Usuarios TRAVELER locales 
# ---------------------------------------------------------------------------
TRAVELERS_FALLBACK = [
    {"id": uuid.UUID("ed4be7ea-b9f0-42b7-97fc-4808d359ba70"), "email": "ana.lopez@yopmail.com", "first_name": "Ana", "last_name": "Lopez"},
    {"id": uuid.UUID("f12f3c5d-da80-4a54-b9d8-f6b1a3cb272a"), "email": "luis.martinez@yopmail.com", "first_name": "Luis", "last_name": "Martinez"},
    {"id": uuid.UUID("a1aaf0dc-36b6-422d-87fe-3c04173c88ef"), "email": "sofia.ruiz@yopmail.com", "first_name": "Sofia", "last_name": "Ruiz"},
    {"id": uuid.UUID("8a6f2b3c-1d4e-4a8d-9c1f-4bb3f6d7a101"), "email": "camila.hernandez@yopmail.com", "first_name": "Camila", "last_name": "Hernandez"},
    {"id": uuid.UUID("c1e4d5f6-2a3b-4c4d-8e9f-5a6b7c8d9e10"), "email": "juan.perez@yopmail.com", "first_name": "Juan", "last_name": "Perez"},
    {"id": uuid.UUID("d2f3a4b5-6c7d-4e8f-9a10-1b2c3d4e5f60"), "email": "valentina.mora@yopmail.com", "first_name": "Valentina", "last_name": "Mora"},
    {"id": uuid.UUID("e3a4b5c6-7d8e-4f90-9a11-2c3d4e5f6071"), "email": "santiago.lopez@yopmail.com", "first_name": "Santiago", "last_name": "Lopez"},
    {"id": uuid.UUID("f4b5c6d7-8e9f-4012-8a13-3d4e5f607182"), "email": "daniela.garcia@yopmail.com", "first_name": "Daniela", "last_name": "Garcia"},
    {"id": uuid.UUID("a5c6d7e8-9f01-4123-8a14-4e5f60718293"), "email": "mateo.suarez@yopmail.com", "first_name": "Mateo", "last_name": "Suarez"},
    {"id": uuid.UUID("b6d7e8f9-0a12-4234-8a15-5f60718293a4"), "email": "laura.ramirez@yopmail.com", "first_name": "Laura", "last_name": "Ramirez"},
    {"id": uuid.UUID("c7e8f90a-1b23-4345-8a16-60718293a4b5"), "email": "andres.torres@yopmail.com", "first_name": "Andres", "last_name": "Torres"},
    {"id": uuid.UUID("d8f90a1b-2c34-4456-8a17-718293a4b5c6"), "email": "paula.castro@yopmail.com", "first_name": "Paula", "last_name": "Castro"},
    {"id": uuid.UUID("e90a1b2c-3d45-4567-8a18-8293a4b5c6d7"), "email": "sebastian.ortiz@yopmail.com", "first_name": "Sebastian", "last_name": "Ortiz"},
    {"id": uuid.UUID("0a1b2c3d-4e56-4678-8a19-93a4b5c6d7e8"), "email": "juliana.vargas@yopmail.com", "first_name": "Juliana", "last_name": "Vargas"},
    {"id": uuid.UUID("1b2c3d4e-5f67-4789-8a1a-a4b5c6d7e8f9"), "email": "diego.gomez@yopmail.com", "first_name": "Diego", "last_name": "Gomez"},
    {"id": uuid.UUID("2c3d4e5f-6071-4890-8a1b-b5c6d7e8f90a"), "email": "natalia.reyes@yopmail.com", "first_name": "Natalia", "last_name": "Reyes"},
    {"id": uuid.UUID("3d4e5f60-7182-4901-8a1c-c6d7e8f90a1b"), "email": "felipe.marin@yopmail.com", "first_name": "Felipe", "last_name": "Marin"},
    {"id": uuid.UUID("4e5f6071-8293-4a12-8a1d-d7e8f90a1b2c"), "email": "maria.fernandez@yopmail.com", "first_name": "Maria", "last_name": "Fernandez"},
    {"id": uuid.UUID("5f607182-93a4-4b23-8a1e-e8f90a1b2c3d"), "email": "camilo.rojas@yopmail.com", "first_name": "Camilo", "last_name": "Rojas"},
    {"id": uuid.UUID("60718293-a4b5-4c34-8a1f-f90a1b2c3d4e"), "email": "isabella.cortes@yopmail.com", "first_name": "Isabella", "last_name": "Cortes"},
]

# ---------------------------------------------------------------------------
# Fallback: Hospedajes locales 
# ---------------------------------------------------------------------------
HOSPEDAJES_FALLBACK = [
    {"id": "300d110a-e8a8-4fce-ba66-a4883b20e6b9"},
    {"id": "859f1435-879b-4590-b09c-33bb3ab9df0e"},
    {"id": "ce956720-a473-42c6-a0a5-eef6b0b8415a"},
    {"id": "11aa8a43-2216-4ae4-b121-d61cd73c1b0d"},
    {"id": "d5dbb696-6bd4-4265-9032-9101965b34db"},
    {"id": "66ef518d-0d97-4652-93aa-fcea4b917158"},
    {"id": "63534bd8-8476-4874-b4ad-c29fca185161"},
    {"id": "b99a11f9-ffdc-42d1-887e-4cc652471f0c"},
    {"id": "33774a58-5203-4910-8d18-c1a4d43a0add"},
    {"id": "79be1bfc-37b1-49b7-a92b-6922d39ca65a"},
    {"id": "c9d34eb9-8447-44ab-9002-0dd11c3cd215"},
    {"id": "fdbb20bf-9ce8-4476-a8a2-bfb5cb3bcb10"},
    {"id": "e7769aaf-603e-465f-840a-0f804373d985"},
    {"id": "cea4d236-be70-45bf-8a16-f83ef756312f"},
    {"id": "177baefd-8f4c-4333-92fe-b7947a4e5a06"},
    {"id": "2cbed5ca-76ea-4674-972d-609439da3be7"},
    {"id": "e6f10ee9-10b9-4cab-b812-b13a8af287a0"},
    {"id": "dc55b37d-8ded-49b6-a04b-9cece2734efb"},
    {"id": "dc5be755-1636-4599-9f43-9d97743b2786"},
    {"id": "9046b401-28e5-45d7-a05b-1e7c825c2fed"},
    {"id": "3faa135c-376f-4cad-9bf6-64bb98a93a85"},
    {"id": "996d574f-ca06-45aa-859a-51b16f171c13"},
    {"id": "721a9e18-93ea-472a-b266-8628b20c7aed"},
    {"id": "b60a1ad8-d32b-42ab-8696-fe8fd249df75"},
    {"id": "a7e4aad0-967b-464a-ab44-38417219de76"},
    {"id": "ac522e77-2cb2-4377-8016-902a56310169"},
    {"id": "a611593b-7aa5-41dc-9645-ee45a88519f1"},
    {"id": "6a57e50e-e7c7-4830-b422-87a7b7929671"},
    {"id": "a367622d-3d77-484a-8cd8-8bee9e9d1219"},
    {"id": "6e46139f-10c3-47ff-8e55-e3e7fed7ba6c"},
    {"id": "0a784cd5-4ae6-4408-8a7c-eb2267b994de"},
    {"id": "d3fb8472-4137-4a4a-931f-e203b8c798e5"},
    {"id": "262c174d-b9cc-4860-939c-00bb940a7f45"},
    {"id": "a4c036cb-a020-4f79-8ab2-855ecffdb1cd"},
    {"id": "c926533b-d033-4573-a0f3-8368378afcf5"},
    {"id": "b760a30f-4ef3-443b-b928-64c3fee45f02"},
    {"id": "8c2e8214-d38d-4364-b9f9-ab911ba95d8a"},
    {"id": "035c5388-66b6-4e30-baf2-8a20afff7f11"},
    {"id": "f839f286-3b95-48a9-aa4b-562c71d346b8"},
    {"id": "b97e420c-4649-4c66-9337-8bff924a34d1"},
    {"id": "05f12119-2fdb-4472-837b-4f44fbc7f422"},
    {"id": "09dfea9e-994b-46a2-85b3-03deb3dc16d6"},
    {"id": "f56de4e2-a3a5-4a88-8259-70c16c53d943"},
    {"id": "1c72f450-be39-4c76-9ac7-110634c63f5d"},
    {"id": "0fedea59-bcc4-4b90-b703-b8613d93c415"},
    {"id": "81057645-60de-468e-a6b2-6591575839b5"},
    {"id": "f71b03be-da4c-4fff-9204-574cded1b9a7"},
    {"id": "08cfcc5b-ede9-4e48-be6b-123631bc966e"},
    {"id": "dab02bbb-28de-4c1c-8ec5-2c518766b7e3"},
    {"id": "0533ce73-5cf4-4440-9d87-9cb4de0b0b3f"},
    {"id": "b6892dc3-2458-4c8d-9bd9-5b14c1a16e06"},
    {"id": "8f37dc55-8932-4f12-b840-5fd0c2d9f14a"},
    {"id": "e751bc79-4262-4750-af23-f8056d9fe116"},
    {"id": "6555b91c-f59d-46ae-9b25-6ecfc744c148"},
    {"id": "ea4a19ea-97ed-4b4e-9171-f428ff7e6a29"},
    {"id": "7a4aa60c-fab5-43c4-b234-e1c72f249b18"},
    {"id": "f46f0dbe-5f49-4073-9434-60a830777db4"},
    {"id": "7e568af0-e961-47ae-a8ca-c6e98b96bb57"},
    {"id": "b9491d5c-4df2-4521-acac-d6bd1a005b7f"},
    {"id": "5b2a8073-523c-4aba-94c0-c263e1b3575d"},
    {"id": "30dec8f0-6f56-4802-8198-3a0c4ed2d280"},
    {"id": "80a879cd-ca1e-481b-aeb7-2792144c95a8"},
    {"id": "42663bab-43bb-47f3-bd69-96af05b7c8f0"},
]


# ---------------------------------------------------------------------------
# 30 Comentarios variados para hospedajes
# ---------------------------------------------------------------------------
COMMENTS_SEED = [
    {
        "rating": 5,
        "comment": "Experiencia excepcional. El personal fue atento, las instalaciones impecables y la ubicación perfecta. Volveré sin dudarlo.",
    },
    {
        "rating": 5,
        "comment": "Simplemente perfecto. Lujo, comodidad y servicio de clase mundial. Una noche memorable.",
    },
    {
        "rating": 4,
        "comment": "Muy buena estancia. Las habitaciones son cómodas, el desayuno delicioso y la ubicación excelente.",
    },
    {
        "rating": 4,
        "comment": "Recomendable para viajeros exigentes. Buen valor por dinero y servicio profesional.",
    },
    {
        "rating": 5,
        "comment": "Increíble. El personal nos sorprendió con detalles especiales. Las vistas desde la habitación son espectaculares.",
    },
    {
        "rating": 3,
        "comment": "Adecuado si buscas un hospedaje básico. Las instalaciones funcionan bien, aunque podría mejorar la limpieza.",
    },
    {
        "rating": 4,
        "comment": "Muy satisfecho con la estancia. La piscina es magnífica y el restaurante ofrece buena gastronomía.",
    },
    {
        "rating": 5,
        "comment": "Hotel de categoría. Habitaciones espaciosas, baños modernos y un servicio impecable en todos los detalles.",
    },
    {
        "rating": 3,
        "comment": "Aceptable por el precio. El wifi podría ser más rápido, pero la ubicación compensa.",
    },
    {
        "rating": 4,
        "comment": "Buena experiencia. La piscina es genial, aunque el desayuno podría tener más variedad.",
    },
    {
        "rating": 5,
        "comment": "Excelente relación calidad-precio. Las amenidades superaron mis expectativas y el staff muy amable.",
    },
    {
        "rating": 2,
        "comment": "Decepcionante. Las fotos del sitio web no corresponden con la realidad. Necesita mantenimiento.",
    },
    {
        "rating": 4,
        "comment": "Perfecto para descansar. Tranquilo, limpio y con servicios completos. Lo volvería a elegir.",
    },
    {
        "rating": 5,
        "comment": "Magnífico. El gym está bien equipado, la comida del restaurante es deliciosa, y la vista nocturna hermosa.",
    },
    {
        "rating": 3,
        "comment": "Regular. Buena ubicación pero el ruido de la calle es notable. Habitaciones pequeñas.",
    },
    {
        "rating": 4,
        "comment": "Estancia agradable. Personal atento, instalaciones limpias y cómodas. Notó buen mantenimiento.",
    },
    {
        "rating": 5,
        "comment": "Sensacional. El spa fue un lujo increíble. No pude pedir nada mejor para mi viaje de negocios.",
    },
    {
        "rating": 3,
        "comment": "Cumple lo básico. Habitación limpia pero sin amenidades extraordinarias. Precio justo.",
    },
    {
        "rating": 4,
        "comment": "Muy bonito. Decoración moderna, habitaciones amplias y un sistema de aire acondicionado silencioso.",
    },
    {
        "rating": 5,
        "comment": "Insuperable. Cada detalle está cuidado. El personal recordó mi nombre y mis preferencias.",
    },
    {
        "rating": 2,
        "comment": "Problemático. Problemas con la plomería y el servicio al cliente fue poco receptivo.",
    },
    {
        "rating": 4,
        "comment": "Buena opción familiar. Areas comunes bonitas, habitaciones espaciosas, kids club variado.",
    },
    {
        "rating": 5,
        "comment": "Obra maestra hotelera. Arquitectura impresionante, servicios premium, ubicación estratégica.",
    },
    {
        "rating": 3,
        "comment": "Conforme pero sin sorpresas. Correcto para una noche, aunque nada destacable.",
    },
    {
        "rating": 4,
        "comment": "Estancia cómoda. La piscina está bien mantenida, el personal muy profesional y sonriente.",
    },
    {
        "rating": 5,
        "comment": "Extraordinario nivel de lujo. Cena a la luz de velas, habitación en suite, servicio impecable.",
    },
    {
        "rating": 2,
        "comment": "Necesita mejoras. El wifi no funciona bien y las instalaciones se ven envejecidas.",
    },
    {
        "rating": 4,
        "comment": "Muy acertado. Ubicación estratégica en el corazón de la ciudad, habitaciones cómodas y limpias.",
    },
    {
        "rating": 5,
        "comment": "Hotel boutique de ensueño. Atención personalizada, diseño único en cada habitación, staff excepcional.",
    },
    {
        "rating": 3,
        "comment": "Intermedio. Tiene sus puntos fuertes en ubicación, pero pierde en modernidad de las instalaciones.",
    },
]

class SeedHelper:
    """Herramienta para poblar y restablecer las tablas de comentarios de usuarios"""

    @staticmethod
    def reset_and_seed():
        """
        Elimina todos los registros existentes de comentarios,
        luego recorre cada hospedaje, asignando 3-10 comentarios
        aleatorios con usuarios TRAVELER aleatorios.

        Returns:
            dict con el resumen de registros insertados o un mensaje de error.
        """
        try:
            # Limpiar tabla de reviews existentes
            Review.query.delete()
            db.session.flush()

            reviews_insertados = 0
            hospedajes_procesados = 0

            # Recorrer cada hospedaje
            for hospedaje in HOSPEDAJES_FALLBACK:
                hospedaje_id = uuid.UUID(hospedaje["id"])
                
                # Seleccionar aleatoriamente entre 3 y 10 comentarios para este hospedaje
                num_comentarios = random.randint(3, 10)
                comentarios_seleccionados = random.sample(
                    COMMENTS_SEED, 
                    min(num_comentarios, len(COMMENTS_SEED))
                )

                # Para cada comentario, seleccionar un usuario aleatorio
                for comentario_data in comentarios_seleccionados:
                    usuario = random.choice(TRAVELERS_FALLBACK)
                    
                    # Construir el nombre del usuario desde el email (antes del @)
                    user_name = usuario.get('email', "").split("@")[0]
                    
                    # Crear el Review
                    review = Review(
                        id=uuid.uuid4(),
                        hospedajeId=hospedaje_id,
                        userId=usuario["id"],
                        userName=user_name,
                        rating=comentario_data["rating"],
                        comment=comentario_data["comment"]
                    )
                    
                    db.session.add(review)
                    reviews_insertados += 1

                hospedajes_procesados += 1

            db.session.commit()

            return {
                "ok": True,
                "reviews_insertados": reviews_insertados,
                "hospedajes_procesados": hospedajes_procesados,
                "comentarios_base": len(COMMENTS_SEED),
                "usuarios_travelers": len(TRAVELERS_FALLBACK)
            }

        except Exception as e:
            db.session.rollback()
            return {"ok": False, "error": str(e)}
