class InventarioHelper:
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