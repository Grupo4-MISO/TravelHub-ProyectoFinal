from app.db.habitacion import HabitacionORM, db
from app.db.hospedaje import HospedajeORM, db

class InventarioCRUD:
    def __init__(self):
        self.db = db.session
    
    def crearHospedajeDB(self, hospedaje_data: dict):
        try:
            #Creamos nuevo hospedaje en base de datos
            nuevo_hospedaje = HospedajeORM(**hospedaje_data)

            #Hacemos persistencia del nuevo hospedaje
            self.db.add(nuevo_hospedaje)
            self.db.commit()

            return nuevo_hospedaje
        
        except Exception as e:
            self.db.rollback()
            return str(e)
    
    def obtenerHospedajeDB(self, hospedaje_id: str):
        try:
            #Traemos el hospedaje de la base de datos
            hospedaje = self.db.query(HospedajeORM).filter_by(id = hospedaje_id).first()

            #Si el hospedaje no existe, retornamos None
            if not hospedaje:
                return None
            
            return hospedaje
        
        except Exception as e:
            return str(e)
    
    def actualizarHospedajeDB(self, hospedaje_id: str, hospedaje_data: dict):
        try:
            #Traemos el hospedaje de la base de datos
            hospedaje = self.db.query(HospedajeORM).filter_by(id = hospedaje_id).first()

            #Si el hospedaje no existe, retornamos None
            if not hospedaje:
                return None
            
            #Actualizamos los campos del hospedaje
            for key, value in hospedaje_data.items():
                if hasattr(hospedaje, key):
                    setattr(hospedaje, key, value)
            
            #Hacemos persistencia de los cambios
            self.db.commit()

            return hospedaje
        
        except Exception as e:
            self.db.rollback()
            return str(e)
    
    def eliminarHospedajeDB(self, hospedaje_id: str):
        try:
            #Traemos el hospedaje de la base de datos
            hospedaje = self.db.query(HospedajeORM).filter_by(id = hospedaje_id).first()

            #Si el hospedaje no existe, retornamos None
            if not hospedaje:
                return None
            
            #Eliminamos el hospedaje de la base de datos
            self.db.delete(hospedaje)
            self.db.commit()

            return hospedaje
        
        except Exception as e:
            self.db.rollback()
            return str(e)
    
    def obtenerHabitacionesPorHospedajeDB(self, hospedaje_id: str):
        try:
            #Traemos las habitaciones del hospedaje de la base de datos
            habitaciones = self.db.query(HabitacionORM).filter_by(propiedad_id = hospedaje_id).all()

            return habitaciones
        
        except Exception as e:
            return str(e)
    
    def hospedajesCiudadCapacidadDB(self, filtros: dict):
        try:
            #Definimos query
            query = (
                self.db.query(HospedajeORM)
                .join(HabitacionORM, HabitacionORM.propiedad_id == HospedajeORM.id)
                .filter(HospedajeORM.ciudad == filtros.get('ciudad'))
                .filter(HabitacionORM.capacidad >= filtros.get('capacidad'))
                .distinct()
            )

            #Ejecutamos query y retornamos resultados
            hospedajes = query.all()

            return [hospedaje.habitacion_id for hospedaje in hospedajes]
        
        except Exception as e:
            self.db.rollback()
            return str(e)
        