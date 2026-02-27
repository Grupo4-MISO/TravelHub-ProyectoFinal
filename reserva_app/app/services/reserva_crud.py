from app.db.reserva import ReservaORM, db
from datetime import datetime

class ReservaCRUD:
    def __init__(self):
        self.db = db.session
    
    def crearReservaDB(self, reserva_data: dict):
        try:
            #Creamos nueva reserva en base de datos
            nueva_reserva = ReservaORM(**reserva_data)

            #Hacemos persistencia del nuevo hospedaje
            self.db.add(nueva_reserva)
            self.db.commit()

            return nueva_reserva
        
        except Exception as e:
            self.db.rollback()
            return str(e)
    
    def obtenerReservaDB(self, reserva_id: str):
        try:
            #Traemos la reserva de la base de datos
            reserva = self.db.query(ReservaORM).filter_by(id = reserva_id).first()

            #Si la reserva no existe, retornamos None
            if not reserva:
                return None
            
            return reserva
        
        except Exception as e:
            return str(e)
    
    def actualizarReservaDB(self, reserva_id: str, reserva_data: dict):
        try:
            #Traemos la reserva de la base de datos
            reserva = self.db.query(ReservaORM).filter_by(id = reserva_id).first()

            #Si la reserva no existe, retornamos None
            if not reserva:
                return None
            
            #Actualizamos los campos de la reserva
            for key, value in reserva_data.items():
                if hasattr(reserva, key):
                    setattr(reserva, key, value)
            
            #Hacemos persistencia de los cambios
            self.db.commit()

            return reserva
        
        except Exception as e:
            self.db.rollback()
            return str(e)
    
    def eliminarReservaDB(self, reserva_id: str):
        try:
            #Traemos la reserva de la base de datos
            reserva = self.db.query(ReservaORM).filter_by(id = reserva_id).first()

            #Si la reserva no existe, retornamos None
            if not reserva:
                return None
            
            #Eliminamos la reserva de la base de datos
            self.db.delete(reserva)
            self.db.commit()

            return reserva
        
        except Exception as e:
            self.db.rollback()
            return str(e)
    
    def habitacionesReservasDisponiblesDB(self, fecha_inicio: str, fecha_fin: str, habitaciones: list):
        try:
            #Pasamos las fechas a formato datetime
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')

            #Consulta para reservas que se cruzan con las fechas dadas
            reservas_cruzadas = self.db.query(ReservaORM).filter(
                ReservaORM.habitacion_id.in_(habitaciones),
                ReservaORM.estado == 'confirmada',
                ReservaORM.fecha_inicio >= fecha_inicio,
                ReservaORM.fecha_fin <= fecha_fin
            )

            #Extraemos las habitaciones ocupadas
            habitaciones_ocupadas = {reservas_cruzada.habitacion_id for reservas_cruzada in reservas_cruzadas}

            #Filtramos las habitaciones disponibles
            habitaciones_disponibles = [habitacion_id for habitacion_id in habitaciones if habitacion_id not in habitaciones_ocupadas]

            return habitaciones_disponibles
        
        except Exception as e:
            self.db.rollback()
            return str(e)
        