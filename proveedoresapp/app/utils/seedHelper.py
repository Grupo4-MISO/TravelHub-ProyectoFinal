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
                manager_id = uuid.UUID(manager["id"])

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
                    hospedajeId=hospedajes_seleccionados[0]["id"],
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
