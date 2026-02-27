from app.db.reserva import ReservaORM, db

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
        