from app.db.models import db, HospedajeORM, HabitacionORM, CountryORM
from app.errors.exceptions import DatababaseError

class InventarioCRUD:
    def __init__(self):
        self.db = db.session

    def listadoPaises(self):
        try:
            #Query de consulta
            query = self.db.query(HospedajeORM.pais).distinct().all()

            return sorted([pais[0] for pais in query])
        
        except Exception as e:
            self.db.rollback()
            raise DatababaseError(f"Error en la base de datos: {str(e)}")

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
        
    def crear_hospedaje(self, data):
        try:
            hospedaje = HospedajeORM(
                nombre=data.get('nombre'),
                countryCode=data.get('countryCode'),
                pais=data.get('pais'),
                ciudad=data.get('ciudad'),
                direccion=data.get('direccion'),
                rating=float(data.get('rating')),
                reviews=int(data.get('reviews')),
            )

            self.db.add(hospedaje)
            self.db.commit()

            return {
                'id': str(hospedaje.id),
                'nombre': hospedaje.nombre,
                'countryCode': hospedaje.countryCode,
                'pais': hospedaje.pais,
                'ciudad': hospedaje.ciudad,
                'direccion': hospedaje.direccion,
                'rating': hospedaje.rating,
                'reviews': hospedaje.reviews,
                'created_at': hospedaje.created_at.isoformat() if hasattr(hospedaje.created_at, 'isoformat') else hospedaje.created_at,
                'updated_at': hospedaje.updated_at.isoformat() if hasattr(hospedaje.updated_at, 'isoformat') else hospedaje.updated_at,
            }

        except Exception as e:
            self.db.rollback()
            return DatababaseError(f"Error en la base de datos: {str(e)}")
    
    def habitacionesDisponibles(self, ciudad, capacidad):
        try:
            #Definimos la consulta para obtener habitaciones disponibles
            query = self.db.query(
                HabitacionORM.id.label('habitacion_id'),
                HabitacionORM.code,
                HabitacionORM.precio,
                HabitacionORM.capacidad,
                HabitacionORM.descripcion,
                HospedajeORM.id.label('hospedaje_id'),
                HospedajeORM.nombre,
                HospedajeORM.pais,
                HospedajeORM.ciudad,
                HospedajeORM.direccion,
                HospedajeORM.rating,
                HospedajeORM.reviews,
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
                    'code': campo.code,
                    'nombre': campo.nombre,
                    'pais': campo.pais,
                    'ciudad': campo.ciudad,
                    'direccion': campo.direccion,
                    'rating': campo.rating,
                    'reviews': campo.reviews,
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


class CountriesCRUD:
    def __init__(self):
        self.db = db.session

    def obtener_paises(self):
        try:
            countries = self.db.query(CountryORM).order_by(CountryORM.name.asc()).all()

            response = [
                {
                    'id': str(country.id),
                    'name': country.name,
                    'code': country.code,
                    'CurrencyCode': country.CurrencyCode,
                    'CurrencySymbol': country.CurrencySymbol,
                    'FlagEmoji': country.FlagEmoji,
                    'PhoneCode': country.PhoneCode,
                }
                for country in countries
            ]

            return response

        except Exception as e:
            self.db.rollback()
            return DatababaseError(f"Error en la base de datos: {str(e)}")


