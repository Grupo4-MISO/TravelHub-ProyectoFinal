from app.errors.exceptions import BadRequestError, ExternalServiceError, InternalServerError
from app.services.reserva_crud import ReservaCRUD
from datetime import datetime
import requests
import json

#Instancia del reserva crud
reserva_crud = ReservaCRUD()

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

    @staticmethod
    def hospedajeInfo(inventario_url, habitacion_id, currency_code):
        try:
            #Request al microservicio de inventario para obtener información del hospedaje
            response = requests.get(f"{inventario_url}/api/v1/inventarios/habitacion/{habitacion_id}/{currency_code}")

            #Genera expecion si el status code es diferente a 200
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            raise ExternalServiceError(f"Error al consultar el microservicio de inventario para obtener información del hospedaje: {str(e)}")

    @staticmethod
    def reservaInfo(reserva_id):
        try:
            return reserva_crud.reservaById(reserva_id)

        except Exception as e:
            raise InternalServerError(f'Error al consultar la reserva en la base de datos: {str(e)}')

    @staticmethod
    def mailMessage(reserva, hospedaje_info, message):
        #DTO del mensaje para la cola de mail
        mail_message = dict()

        #Construimos la informacion de reserva
        mail_message['reserva'] = {
            'codigo_reserva': reserva.get('public_id'),
            'check_in': reserva.get('check_in'),
            'check_out': reserva.get('check_out'),
            'tarifa_total': message.get('payment_info').get('amount'),
            'currency': message.get('payment_info').get('currency')
        }

        #Construimos la informacion del hospedaje
        mail_message['hospedaje'] = {
            'nombre': hospedaje_info.get('nombre'),
            'direccion': hospedaje_info.get('direccion'),
            'ciudad': hospedaje_info.get('ciudad'),
            'pais': hospedaje_info.get('pais'),
            'amenidades': hospedaje_info.get('amenidades'),
            'imagen': hospedaje_info.get('imagenes')[0].get('url')
        }

        #Construimos la informacion del cliente
        mail_message['cliente'] = {
            'email': message.get('email')
        }

        return mail_message
        

        