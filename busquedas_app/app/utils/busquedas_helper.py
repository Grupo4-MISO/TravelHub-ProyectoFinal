from datetime import datetime

class BusquedasHelper:
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
            return 'El campo ciudad es requerido'
        
        if not isinstance(ciudad, str):
            return 'El campo ciudad debe ser una cadena de texto'
        
        return True
    
    @staticmethod
    def validacionCampoCapacidad(capacidad):
        if not capacidad:
            return 'El campo capacidad es requerido'
        
        if not isinstance(capacidad, int):
            return 'El campo capacidad debe ser un número entero'
        
        if capacidad <= 0:
            return 'El campo capacidad debe ser un número entero positivo'
        
        return True
    
    @staticmethod
    def validacionCampoFechas(check_in, check_out):
        if not check_in or not check_out:
            return 'Los campos check_in y check_out son requeridos'
        
        if check_in >= check_out:
            return 'La fecha de check-out debe ser posterior a la fecha de check-in'
        
        if check_out <= check_in:
            return 'La fecha de check-in debe ser anterior a la fecha de check-out'
        
        if check_out < datetime.now().date():
            return {'msg': 'La fecha de check-out debe ser una fecha futura'}, 400

        try:
            datetime.strptime(check_in, '%Y-%m-%d')
        except ValueError:
            return 'La fecha de check-in debe estar en formato YYYY-MM-DD'
        
        try:
            datetime.strptime(check_out, '%Y-%m-%d')
        except ValueError:
            return 'La fecha de check-out debe estar en formato YYYY-MM-DD'

        return True
