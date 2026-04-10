import uuid
from app.utils.helper import InventarioHelper
from app.db.models import db, HospedajeORM, HabitacionORM, CountryORM, Hospedaje_ImagenORM
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
        
    def obtener_hospedajes(self, country_code=None, ciudad=None):
        try:
            query = self.db.query(HospedajeORM)

            if country_code:
                query = query.filter(HospedajeORM.countryCode == country_code)

            if ciudad:
                query = query.filter(HospedajeORM.ciudad == ciudad)

            hospedajes = query.order_by(HospedajeORM.nombre.asc()).all()

            return [
                {
                    'id': str(hospedaje.id),
                    'nombre': hospedaje.nombre,
                    'descripcion': hospedaje.descripcion,
                    'countryCode': hospedaje.countryCode,
                    'pais': hospedaje.pais,
                    'ciudad': hospedaje.ciudad,
                    'direccion': hospedaje.direccion,
                    'latitude': hospedaje.latitude,
                    'longitude': hospedaje.longitude,
                    'rating': hospedaje.rating,
                    'reviews': hospedaje.reviews,
                    'created_at': hospedaje.created_at.isoformat() if hasattr(hospedaje.created_at, 'isoformat') else hospedaje.created_at,
                    'updated_at': hospedaje.updated_at.isoformat() if hasattr(hospedaje.updated_at, 'isoformat') else hospedaje.updated_at,
                }
                for hospedaje in hospedajes
            ]

        except Exception as e:
            self.db.rollback()
            return DatababaseError(f"Error en la base de datos: {str(e)}")

    def crear_hospedaje(self, data):
        try:
            hospedaje = HospedajeORM(
                nombre=data.get('nombre'),
                descripcion=data.get('descripcion') or f"Hospedaje en {data.get('ciudad', 'destino turístico')}",
                countryCode=data.get('countryCode'),
                pais=data.get('pais'),
                ciudad=data.get('ciudad'),
                direccion=data.get('direccion'),
                latitude=float(data.get('latitude', 0.0)),
                longitude=float(data.get('longitude', 0.0)),
                rating=float(data.get('rating')),
                reviews=int(data.get('reviews')),
            )

            self.db.add(hospedaje)
            self.db.commit()

            return {
                'id': str(hospedaje.id),
                'nombre': hospedaje.nombre,
                'descripcion': hospedaje.descripcion,
                'countryCode': hospedaje.countryCode,
                'pais': hospedaje.pais,
                'ciudad': hospedaje.ciudad,
                'direccion': hospedaje.direccion,
                'latitude': hospedaje.latitude,
                'longitude': hospedaje.longitude,
                'rating': hospedaje.rating,
                'reviews': hospedaje.reviews,
                'created_at': hospedaje.created_at.isoformat() if hasattr(hospedaje.created_at, 'isoformat') else hospedaje.created_at,
                'updated_at': hospedaje.updated_at.isoformat() if hasattr(hospedaje.updated_at, 'isoformat') else hospedaje.updated_at,
            }

        except Exception as e:
            self.db.rollback()
            return DatababaseError(f"Error en la base de datos: {str(e)}")

    def obtener_hospedaje_por_id(self, hospedaje_id):
        try:
            hospedaje_uuid = uuid.UUID(str(hospedaje_id))
            hospedaje = self.db.query(HospedajeORM).filter(HospedajeORM.id == hospedaje_uuid).first()

            if not hospedaje:
                return None

            return {
                'id': str(hospedaje.id),
                'nombre': hospedaje.nombre,
                'descripcion': hospedaje.descripcion,
                'countryCode': hospedaje.countryCode,
                'pais': hospedaje.pais,
                'ciudad': hospedaje.ciudad,
                'direccion': hospedaje.direccion,
                'latitude': hospedaje.latitude,
                'longitude': hospedaje.longitude,
                'rating': hospedaje.rating,
                'reviews': hospedaje.reviews,
                'habitaciones': [
                    {
                        'id': str(h.id),
                        'code': h.code,
                        'descripcion': h.descripcion,
                        'capacidad': h.capacidad,
                        'precio': h.precio,
                        'imageUrl': h.imageUrl,
                    }
                    for h in hospedaje.habitaciones
                ],
                'imagenes': [
                    {
                        'id': str(img.id),
                        'url': img.url,
                    }
                    for img in hospedaje.imagenes
                ],
                'created_at': hospedaje.created_at.isoformat() if hasattr(hospedaje.created_at, 'isoformat') else hospedaje.created_at,
                'updated_at': hospedaje.updated_at.isoformat() if hasattr(hospedaje.updated_at, 'isoformat') else hospedaje.updated_at,
            }

        except ValueError:
            return DatababaseError("El id del hospedaje no tiene un formato UUID válido")
        except Exception as e:
            self.db.rollback()
            return DatababaseError(f"Error en la base de datos: {str(e)}")
    
    def habitacionesDisponibles(self, ciudad, capacidad, currency_code_destino):
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
                CountryORM.CurrencyCode.label('currency_code'),
                Hospedaje_ImagenORM.url.label('image_url')
            ).join(HospedajeORM, HabitacionORM.propiedad_id == HospedajeORM.id)\
            .join(CountryORM, HospedajeORM.countryCode == CountryORM.code)\
            .join(Hospedaje_ImagenORM, HospedajeORM.id == Hospedaje_ImagenORM.hospedaje_id)

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
                    'descripcion': campo.descripcion,
                    'currency_code': campo.currency_code,
                    'image_url': campo.image_url,
                }
                for campo in resultados
            ]
            
            #Construimos respuesta con precios convertidos
            response_convertida = InventarioHelper.convertirPrecios(response, currency_code_destino)

            return response_convertida
        
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

    def obtener_ciudades_por_codigo(self, country_code):
        try:
            code = (country_code or '').upper().strip()
            if not code:
                return []

            ciudades = (
                self.db.query(HospedajeORM.ciudad)
                .filter(HospedajeORM.countryCode == code)
                .group_by(HospedajeORM.countryCode, HospedajeORM.pais, HospedajeORM.ciudad)
                .order_by(HospedajeORM.ciudad.asc())
                .all()
            )

            return [row.ciudad for row in ciudades]

        except Exception as e:
            self.db.rollback()
            return DatababaseError(f"Error en la base de datos: {str(e)}")


