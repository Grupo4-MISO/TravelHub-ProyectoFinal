from app.db.models import ReservaORM, db
from sqlalchemy import not_

class ReservaCRUD:
    def __init__(self):
        self.db = db.session
    
    def verificarDisponibilidad(self, habitacion_ids, check_in, check_out):
        try:
            #Definimos consulta para verificar disponibilidad
            query = self.db.query(ReservaORM).filter(
                ReservaORM.habitacion_id.in_(habitacion_ids),
                ReservaORM.estado == 'confirmada',
                not_(
                    (ReservaORM.check_out <= check_in) |
                    (ReservaORM.check_in >= check_out)
                )
            )

            #Resultados de las reservas ocupadas
            reservas_ocupadas = query.all()

            #Ids de habitaciones ocupadas
            habitaciones_ids_ocupadas = {str(reserva_ocupada.habitacion_id) for reserva_ocupada in reservas_ocupadas}

            #Habitaciones disponibles
            disponibilidad = dict()

            for habitacion_id in habitacion_ids:
                #Convertimos a string para comparar con los ids ocupados
                habitacion_id = str(habitacion_id)

                #Llenamos el diccionario de disponibilidad
                disponibilidad[habitacion_id] = habitacion_id not in habitaciones_ids_ocupadas
            
            return disponibilidad

        except Exception as e:
            self.db.rollback()
            return str(e)
        