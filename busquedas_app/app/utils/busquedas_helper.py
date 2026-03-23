from app.errors.exceptions import BadRequestError
from datetime import datetime

class BusquedasHelper:
    @staticmethod
    def convertirFechasDate(fecha):
        return datetime.strptime(fecha, '%Y-%m-%d').date()
    
    @staticmethod
    def filtrarHabitacionesDisponibles(hospedajes_habitaciones, disponibles):
        #Diccionario de habitaciones disponibles
        hospedajes_habitaciones_disponibles = list()

        #Pasamos disponibles a set
        disponibles = set(disponibles)

        for hospedaje_habitacion in hospedajes_habitaciones:
            if hospedaje_habitacion.get('habitacion_id') in disponibles:
                hospedajes_habitaciones_disponibles.append(hospedaje_habitacion)
        
        return hospedajes_habitaciones_disponibles

    @staticmethod
    def validacionCampoCiudad(ciudad):
        if not ciudad:
            raise BadRequestError('El campo ciudad no debe ser vacío')

        try:
            ciudad = int(ciudad)

            if isinstance(ciudad, int):
                raise BadRequestError('El campo ciudad debe ser un texto')
        
        except ValueError:
            return None
    
    @staticmethod
    def validacionCampoCapacidad(capacidad):
        try:
            capacidad = int(capacidad)

        except ValueError:
            raise BadRequestError('El campo capacidad debe ser un número entero')
        
        except TypeError:
            raise BadRequestError('El campo capacidad no debe ser vacío')
        
        if capacidad <= 0:
            raise BadRequestError('El campo capacidad debe ser un número entero positivo')
    
    @staticmethod
    def validacionCampoFechas(check_in, check_out):
        try:
            check_in = BusquedasHelper.convertirFechasDate(check_in)

        except ValueError:
            raise BadRequestError('La fecha de check-in debe estar en formato YYYY-MM-DD')
        
        except TypeError:
            raise BadRequestError('La fecha de check-in no debe ser vacía')
        
        try:
            check_out = BusquedasHelper.convertirFechasDate(check_out)

        except ValueError:
            raise BadRequestError('La fecha de check-out debe estar en formato YYYY-MM-DD')
    
        except TypeError:
            raise BadRequestError('La fecha de check-out no debe ser vacía')
    
        if check_in >= check_out:
            raise BadRequestError('La fecha de check-out debe ser posterior a la fecha de check-in')
        
        if check_in < datetime.now().date():
            raise BadRequestError('La fecha de check-in debe ser una fecha futura')
        
        if check_out < datetime.now().date():
            raise BadRequestError('La fecha de check-out debe ser una fecha futura')
