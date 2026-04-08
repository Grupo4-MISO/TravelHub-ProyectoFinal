from app.errors.exceptions import BadRequestError

class InventarioHelper:
    @staticmethod
    def validacionCampoCiudad(ciudad):
        if not ciudad:
            raise BadRequestError('El campo ciudad no debe ser vacío')

        try:
            ciudad = int(ciudad)

            if isinstance(ciudad, int):
                raise BadRequestError('El campo ciudad debe ser un texto')
        
        except ValueError:
            return ciudad
    
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

        return capacidad

    @staticmethod
    def ordenarCiudades(ciudades):
        return sorted(ciudades)