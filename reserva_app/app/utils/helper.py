from app.errors.exceptions import BadRequestError, InternalServerError
from datetime import datetime
import json

IMPUESTOS = {
    'AR': 0.21,
    'CL': 0.19,
    'CO': 0.19,
    'EC': 0.15,
    'MX': 0.16,
    'PE': 0.18
}

class ReservaHelper:
    @staticmethod
    def convertirFechasDate(fecha):
        return datetime.strptime(fecha, '%Y-%m-%d').date()
    
    @staticmethod
    def loadJSON(message):
        try:
            return json.loads(message['Body'])
        
        except Exception as e:
            raise InternalServerError(f'Error loading JSON from message: {str(e)}')
    
    @staticmethod
    def validacionCampoFechas(check_in, check_out):
        try:
            check_in = ReservaHelper.convertirFechasDate(check_in)

        except ValueError:
            raise BadRequestError('La fecha de check-in debe estar en formato YYYY-MM-DD')
        
        except TypeError:
            raise BadRequestError('La fecha de check-in no debe ser vacía')
        
        try:
            check_out = ReservaHelper.convertirFechasDate(check_out)

        except ValueError:
            raise BadRequestError('La fecha de check-out debe estar en formato YYYY-MM-DD')
    
        except TypeError:
            raise BadRequestError('La fecha de check-out no debe ser vacía')
        
        if check_in < datetime.now().date():
            raise BadRequestError('La fecha de check-in debe ser una fecha futura')

        if check_out < datetime.now().date():
            raise BadRequestError('La fecha de check-out debe ser una fecha futura')
        
        if check_in >= check_out:
            raise BadRequestError('La fecha de check-out debe ser posterior a la fecha de check-in')

        return check_in, check_out

    @staticmethod
    def validacionCampoPrecio(precio_noche):
        try:
            precio_noche = float(precio_noche)

        except ValueError:
            raise BadRequestError('El campo de precio debe ser un número válido')
        
        if precio_noche == 0:
            raise BadRequestError('El campo de precio no puede ser cero')
        
        if not precio_noche:
            raise BadRequestError('El campo de precio no debe ser vacío')

        if precio_noche < 0:
            raise BadRequestError('El campo de precio no puede ser negativo')
        
        return precio_noche

    @staticmethod
    def validacionCampoDescuento(descuento):
        try:
            descuento = float(descuento)

        except ValueError:
            raise BadRequestError('El campo de descuento debe ser un número válido')
              
        if descuento < 0:
            raise BadRequestError('El campo de descuento no puede ser negativo')
        
        return descuento

    @staticmethod
    def validacionCampoPais(pais):
        if not pais:
            raise BadRequestError('El campo de país no debe ser vacío')
        
        if pais not in IMPUESTOS:
            raise BadRequestError(f'El campo de país debe ser uno de los siguientes: {", ".join(IMPUESTOS.keys())}')

    @staticmethod
    def calcularNoches(check_in, check_out):
        return (check_out - check_in).days

    @staticmethod
    def calcularTarifaTotal(check_in, check_out, precio_noche, descuento, pais):
        #Calculamos numeros de noches
        noches = ReservaHelper.calcularNoches(check_in, check_out)

        #Calculamos subtotal sin descuento e impuestos
        subtotal = noches * precio_noche

        #Calculamos descuento
        descuento_aplicado = subtotal * descuento

        #Calculamos impuestos
        impuestos = (subtotal - descuento_aplicado) * IMPUESTOS.get(pais)

        #Calculamos tarifa total
        tarifa_total = subtotal - descuento_aplicado + impuestos

        #DTO de respuesta
        response = {
            'precio_base': subtotal,
            'descuento': descuento_aplicado,
            'impuestos': impuestos,
            'tarifa_total': tarifa_total,
        }

        return response