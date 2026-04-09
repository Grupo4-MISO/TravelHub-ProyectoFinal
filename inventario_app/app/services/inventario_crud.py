from app.db.models import db, HospedajeORM, HabitacionORM
from app.errors.exceptions import DatababaseError

class InventarioCRUD:
    def __init__(self):
        self.db = db.session

    def listadoCiudades(self):
        try:
            #Query de consulta
            query = self.db.query(HospedajeORM.ciudad, HospedajeORM.pais).distinct().all()

            #Construimos respuesta
            ciudades = list()

            for ciudad, pais in query:
                ciudades.append({'ciudad': ciudad, 'pais': pais})
            
            return ciudades
            
        except Exception as e:
            self.db.rollback()
            raise DatababaseError(f"Error en la base de datos: {str(e)}")
        
    def habitacionesDisponibles(self, ciudad, capacidad):
        try:
            #Definimos la consulta para obtener habitaciones disponibles
            query = self.db.query(
                HabitacionORM.id.label('habitacion_id'),
                HabitacionORM.precio,
                HabitacionORM.capacidad,
                HabitacionORM.descripcion,
                HospedajeORM.id.label('hospedaje_id'),
                HospedajeORM.nombre,
                HospedajeORM.pais,
                HospedajeORM.ciudad,
                HospedajeORM.direccion,
                HospedajeORM.rating
            ).join(HospedajeORM, HabitacionORM.propiedad_id == HospedajeORM.id)

            #Aplicamos filtros de ciudad y capacidad
            if ciudad:
                query = query.filter(HospedajeORM.ciudad == ciudad)
            
            if capacidad:
                query = query.filter(HabitacionORM.capacidad >= capacidad)
            
            #Realizamos query
            resultados = query.all()

            #Construimos respuesta
            response = [
                {
                    'habitacion_id': str(campo.habitacion_id),
                    'hospedaje_id': str(campo.hospedaje_id),
                    'nombre': campo.nombre,
                    'pais': campo.pais,
                    'ciudad': campo.ciudad,
                    'direccion': campo.direccion,
                    'rating': campo.rating,
                    'capacidad': campo.capacidad,
                    'precio': campo.precio,
                    'descripcion': campo.descripcion
                }
                for campo in resultados
            ]

            return response
    
        except Exception as e:
            self.db.rollback()
            raise DatababaseError(f"Error en la base de datos: {str(e)}")


