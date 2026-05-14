from app.errors.exceptions import BadRequestError, ExternalServiceError, InternalServerError
from app.services.reserva_crud import ReservaCRUD
from datetime import datetime
import requests
import json
from app.utils.tarifas_helper import TarifasHelper
import os

INVENTARIOS_URL = os.getenv('INVENTARIOS_URL', 'http://127.0.0.1:3000')

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
    def calcularTarifaTotal(check_in, check_out, precio_noche, descuento, pais, tarifa_data=None):
        """
        Calcula la tarifa total considerando precio base, descuentos e impuestos.
        
        Si tarifa_data es proporcionada, usa el precio_tarifa_aplicada (que ya tiene descuentos).
        Si no, usa el descuento genérico tradicional.
        
        Args:
            check_in: fecha de check-in
            check_out: fecha de check-out
            precio_noche: precio por noche (usado si no hay tarifa_data)
            descuento: descuento genérico en % (usado si no hay tarifa_data)
            pais: código de país para obtener tasa de impuesto
            tarifa_data: dict con tarifa_id, precio_tarifa_aplicada, descuentos_aplicados
        
        Returns:
            dict con desglose de precios
        """
        #Calculamos numeros de noches
        noches = ReservaHelper.calcularNoches(check_in, check_out)

        # Si tenemos tarifa configurada, usarla; sino, usar descuento genérico
        if tarifa_data and tarifa_data.get('precio_tarifa_aplicada'):
            precio_por_noche = tarifa_data.get('precio_tarifa_aplicada')
            descuentos_detalle = tarifa_data.get('descuentos_aplicados', [])
        else:
            precio_por_noche = precio_noche
            # Convertir descuento genérico a formato de detalle
            descuentos_detalle = [{"porcentaje": descuento * 100, "nombre": "Descuento manual"}] if descuento > 0 else []

        #Calculamos subtotal sin descuento e impuestos
        subtotal = noches * precio_por_noche

        #Calculamos descuento (si viene con tarifa, ya está incluido en precio_por_noche)
        if tarifa_data and tarifa_data.get('precio_tarifa_aplicada'):
            # El descuento ya está aplicado en la tarifa
            descuento_aplicado = 0.0
        else:
            # Descuento genérico tradicional
            descuento_aplicado = subtotal * descuento

        #Calculamos impuestos
        impuestos = (subtotal - descuento_aplicado) * IMPUESTOS.get(pais, 0)

        #Calculamos tarifa total
        tarifa_total = subtotal - descuento_aplicado + impuestos

        #DTO de respuesta
        response = {
            'precio_base': subtotal,
            'descuento': descuento_aplicado,
            'impuestos': impuestos,
            'tarifa_total': tarifa_total,
            'descuentos_detalle': descuentos_detalle,
            'tarifa_id': tarifa_data.get('tarifa_id') if tarifa_data else None,
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
    @staticmethod
    def obtener_datos_habitacion(habitacion_id: str):
        """
        Obtiene los datos de una habitación desde inventario.
        Retorna: hotel_id, categoria, pais, precio
        """
        try:
            response = requests.get(
                f"{INVENTARIOS_URL}/api/v1/inventarios/habitacion-datos/{habitacion_id}",
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ExternalServiceError(f"Error al consultar datos de habitación: {str(e)}")

    @staticmethod
    def obtener_tarifa_para_reserva(hotel_id: str, categoria: str, check_in: str, check_out: str, currency_code: str = None, auth_headers=None):
        """
        Obtiene la tarifa configurada para esta reserva.
        Retorna: dict con tarifa_id, precio_tarifa_aplicada, descuentos_aplicados
        o None si no existe tarifa configurada
        """
        try:
            return TarifasHelper.obtener_tarifa_para_reserva(
                hotel_id,
                categoria,
                check_in,
                check_out,
                currency_code=currency_code,
                auth_headers=auth_headers,
            )
        except Exception as e:
            # Log pero no fallar - si no hay tarifa, continuar sin ella
            print(f"Advertencia al obtener tarifa: {str(e)}")
            return None


        return None

