from app.utils.token_helper import token_required, roles_required
from app.utils.one_signal_helper import OneSignalHelper
from app.services.reserva_crud import ReservaCRUD
from app.utils.tarifas_helper import TarifasHelper
from app.services.hold_service import HoldService
from app.errors.exceptions import APIError
from app.utils.seedHelper import SeedHelper
from app.utils.helper import ReservaHelper
from flask_restful import Resource
from datetime import datetime
from flask import request
import os

#Url de microservicios
INVENTARIOS_URL = os.getenv('INVENTARIOS_URL', 'http://127.0.0.1:3000')

#Variables de entorno para OneSignal
ONE_SIGNAL_APP_ID = os.getenv('ONE_SIGNAL_APP_ID')
ONE_SIGNAL_API_KEY = os.getenv('ONE_SIGNAL_API_KEY')
one_signal_helper = OneSignalHelper(ONE_SIGNAL_APP_ID, ONE_SIGNAL_API_KEY)

#Instanciamos crud
reservas_crud = ReservaCRUD()

class ReservaHealth(Resource):
    def get(self):
        return {'status': 'healthy'}, 200

class VerificarDisponibilidad(Resource):
    def post(self):
        try:
            #Obtenemos los datos del request
            data = request.get_json() or {}

            #Validamos campos de fechas
            check_in, check_out = ReservaHelper.validacionCampoFechas(data.get('check_in'), data.get('check_out'))

            #Obtenemos datos del request de ids
            habitaciones_ids = data.get('habitacion_ids') or []

            #Verificamos disponibilidad
            disponibilidad = reservas_crud.verificarDisponibilidad(habitaciones_ids, check_in, check_out)

            return disponibilidad, 200
        except APIError as e:
            return {'msg': e.message}, e.status_code
        except Exception as e:
            return {'msg': 'Error al verificar la disponibilidad', 'error': str(e)}, 500


class CrearReserva(Resource):
    def post(self):
        data = request.get_json() or {}

        habitacion_id = data.get('habitacion_id')
        if not habitacion_id:
            return {'msg': 'El campo habitacion_id es requerido'}, 400

        try:
            check_in, check_out = ReservaHelper.validacionCampoFechas(data.get('check_in'), data.get('check_out'))
        except APIError as e:
            return {'msg': e.message}, e.status_code

        user_id = data.get('user_id')

        reserva = reservas_crud.crearReserva(habitacion_id, check_in, check_out, user_id=user_id)
        if isinstance(reserva, str):
            if reserva == 'La habitación no está disponible para las fechas seleccionadas':
                return {'msg': reserva}, 409
            return {'msg': 'Error al crear la reserva', 'error': reserva}, 500

        return {'msg': 'Reserva creada correctamente', 'reserva': reserva}, 201
class CrearReserva(Resource):
    def post(self):
        data = request.get_json() or {}

        habitacion_id = data.get('habitacion_id')
        if not habitacion_id:
            return {'msg': 'El campo habitacion_id es requerido'}, 400

        try:
            check_in, check_out = ReservaHelper.validacionCampoFechas(data.get('check_in'), data.get('check_out'))
        except APIError as e:
            return {'msg': e.message}, e.status_code

        user_id = data.get('user_id')
        
        # NUEVO: Obtener datos de habitación e intentar aplicar tarifa
        tarifa_data = None
        try:
            import requests
            # Consultar datos de la habitación desde inventario
            habitacion_response = requests.get(
                f"{INVENTARIOS_URL}/api/v1/inventarios/habitacion-datos/{habitacion_id}",
                timeout=5
            )
            if habitacion_response.status_code == 200:
                habitacion_info = habitacion_response.json()
                hotel_id = habitacion_info.get('hospedaje_id')
                categoria = habitacion_info.get('categoria', '')
                
                if hotel_id and categoria:
                    # Consultar tarifa configurada
                    tarifa_data = ReservaHelper.obtener_tarifa_para_reserva(
                        hotel_id,
                        categoria,
                        check_in.isoformat(),
                        check_out.isoformat()
                    )
        except Exception as e:
            # Log pero no fallar - continuar sin tarifa
            print(f"Advertencia al procesar tarifa: {str(e)}")

        # Crear reserva con datos de tarifa (si existen)
        try:
            reserva = reservas_crud.crearReserva(
                habitacion_id,
                check_in,
                check_out,
                user_id=user_id,
                tarifa_data=tarifa_data
            )
        except TypeError as e:
            if 'tarifa_data' not in str(e):
                raise
            reserva = reservas_crud.crearReserva(
                habitacion_id,
                check_in,
                check_out,
                user_id=user_id
            )
        if isinstance(reserva, str):
            if reserva == 'La habitación no está disponible para las fechas seleccionadas':
                return {'msg': reserva}, 409
            return {'msg': 'Error al crear la reserva', 'error': reserva}, 500

        return {'msg': 'Reserva creada correctamente', 'reserva': reserva}, 201

class SeedReservas(Resource):
    def post(self, cantidad):
        if cantidad <= 0:
            return {'msg': 'La cantidad debe ser un entero positivo'}, 400

        result = SeedHelper.reset_and_seed(cantidad)

        if not result.get('ok'):
            return {'msg': 'Error al ejecutar el seed', 'error': result.get('error')}, 500

        response = {
            'msg': 'Seed ejecutado correctamente',
            'solicitadas por habitacion': result['solicitadas'],
            'reservas_insertadas': result['reservas_insertadas'],
        }

        if 'advertencia' in result:
            response['advertencia'] = result['advertencia']

        return response, 200

# Aqui va el post de crear la reserva temporal en redis mientras el cliente 
# se decide a pagar o no, con un hold de 15 minutos. 

# Aqui va sacar la reserva de redis y crear la reserva definitiva en postgres cuando el usuario se decide a pagar
# y creamos un registro de transacción con el servicio de pagos

# -----------------------------------------------------------------------
# Instanciamos el servicio de hold
# -----------------------------------------------------------------------
hold_service = HoldService()

class HoldReserva(Resource):
    def post(self):
        # Obtenemos los datos del request
        data = request.get_json()

        # Validamos campos requeridos
        campos_requeridos = ['user_id', 'habitacion_id', 'check_in', 'check_out']
        for campo in campos_requeridos:
            if not data.get(campo):
                return {'msg': f'El campo {campo} es requerido'}, 400

        # Parseamos y validamos fechas
        try:
            check_in  = datetime.strptime(data.get('check_in'),  '%Y-%m-%d').date()
            check_out = datetime.strptime(data.get('check_out'), '%Y-%m-%d').date()
        except ValueError:
            return {'msg': 'Formato de fecha inválido, use YYYY-MM-DD'}, 400

        if check_in >= check_out:
            return {'msg': 'La fecha de check-out debe ser posterior a la fecha de check-in'}, 400

        if check_out < datetime.now().date():
            return {'msg': 'La fecha de check-out debe ser una fecha futura'}, 400

        user_id       = data.get('user_id')
        habitacion_id = data.get('habitacion_id')

        print(f"HoldReserva - user_id: {user_id}, habitacion_id: {habitacion_id}, check_in: {check_in}, check_out: {check_out}")

        # Delegamos la lógica al servicio de hold
        try:
            resultado = hold_service.crear_hold(user_id, habitacion_id, check_in, check_out)
        except NotImplementedError as e:
            return {'msg': 'Funcionalidad pendiente de implementación', 'detalle': str(e)}, 501

        # Si el servicio retornó un error (string), lo propagamos como 500
        if isinstance(resultado, str):
            return {'msg': 'Error al crear la reserva temporal', 'error': resultado}, 500

        # Si la habitación no está disponible, retornamos 409 Conflict
        if not resultado.get('disponible'):
            return {'msg': resultado.get('motivo', 'La habitación no está disponible')}, 409

        return resultado, 201
    
class darReservas(Resource):
    def post(self):
        try:
            data = request.get_json()
            habitaciones = data.get('habitaciones')
            reservas = []
            for idHabitacion in habitaciones:
                reservas.extend(reservas_crud.obtenerReservasPorHabitacion(idHabitacion))
            return reservas, 200
        except Exception as e:
            return {'msg': 'Error al obtener las reservas', 'error': str(e)}, 500

class TarifaReserva(Resource):
    def post(self):
        #Obtenemos payload del request
        data = request.get_json()

        #Parametros requeridos
        check_in = data.get('check_in')
        check_out = data.get('check_out')
        precio_noche = data.get('precio')
        descuento = data.get('descuento', 0)
        pais = data.get('pais')

        #Validamos parametros del request
        check_in, check_out = ReservaHelper.validacionCampoFechas(check_in, check_out)
        precio_noche = ReservaHelper.validacionCampoPrecio(precio_noche)
        descuento = ReservaHelper.validacionCampoDescuento(descuento)
        ReservaHelper.validacionCampoPais(pais)

        #Calculamos tarifa total
        calculo_tarifa = ReservaHelper.calcularTarifaTotal(check_in, check_out, precio_noche, descuento, pais)
        
        return calculo_tarifa, 200
class TarifaReserva(Resource):
    def post(self):
        """
        Calcula el total de una reserva.
        
        Opciones:
        1. Con tarifa configurada (tarifa_id): consulta tarifas y aplica precio_tarifa_aplicada
        2. Con descuento genérico (descuento + precio): modo tradicional
        
        Payload esperado (opción 1 con tarifa):
        {
            "check_in": "2026-05-10",
            "check_out": "2026-05-15",
            "tarifa_id": "uuid-de-tarifa",
            "pais": "CO"
        }
        
        Payload esperado (opción 2 genérico - legacy):
        {
            "check_in": "2026-05-10",
            "check_out": "2026-05-15",
            "precio": 100,
            "descuento": 0.1,
            "pais": "CO"
        }
        """
        try:
            #Obtenemos payload del request
            data = request.get_json()

            #Parametros requeridos básicos
            check_in = data.get('check_in')
            check_out = data.get('check_out')
            pais = data.get('pais')

            #Validamos parametros del request
            check_in, check_out = ReservaHelper.validacionCampoFechas(check_in, check_out)
            ReservaHelper.validacionCampoPais(pais)

            tarifa_data = None
            
            # Opción 1: Si viene tarifa_id, usarla
            tarifa_id = data.get('tarifa_id')
            if tarifa_id:
                try:
                    # Aquí podrías consultar tarifa específica por ID
                    # Por ahora, se asume que ya tiene precio_tarifa_aplicada
                    tarifa_data = {
                        'tarifa_id': tarifa_id,
                        'precio_tarifa_aplicada': data.get('precio_tarifa_aplicada'),
                        'descuentos_aplicados': data.get('descuentos_aplicados', [])
                    }
                except Exception as e:
                    return {'msg': 'Error al procesar tarifa', 'error': str(e)}, 400
            else:
                # Opción 2: Modo genérico - requiere precio y descuento
                precio_noche = data.get('precio')
                descuento = data.get('descuento', 0)
                
                precio_noche = ReservaHelper.validacionCampoPrecio(precio_noche)
                descuento = ReservaHelper.validacionCampoDescuento(descuento)

            #Calculamos tarifa total
            if tarifa_data:
                calculo_tarifa = ReservaHelper.calcularTarifaTotal(
                    check_in, 
                    check_out, 
                    0,  # precio_noche no se usa cuando hay tarifa_data
                    0,  # descuento no se usa cuando hay tarifa_data
                    pais,
                    tarifa_data=tarifa_data
                )
            else:
                calculo_tarifa = ReservaHelper.calcularTarifaTotal(
                    check_in, 
                    check_out, 
                    precio_noche, 
                    descuento, 
                    pais
                )
            
            return calculo_tarifa, 200
        except Exception as e:
            return {'msg': str(e)}, 400

class Confirmar_Reserva(Resource):
    @token_required
    @roles_required('Admin', 'Manager', 'Accomodation')
    def post(current_user, self, reserva_id):
        #Traemos la reserva por id
        reserva = reservas_crud.reservaById(reserva_id)

        #Llamamos a inventario para traer el id del hospedaje
        hospedaje_id = ReservaHelper.hospedajeId(INVENTARIOS_URL, reserva.get('habitacion_id'))

        #Validamos que el user_id del token pueda confirmar la reserva
        if hospedaje_id.get('id') != current_user.get('sub'):
            return {'msg': 'No tienes permisos para confirmar esta reserva'}, 403

        response = reservas_crud.confirmarReserva(reserva_id)
        
        if response == True:
            return {'msg': 'Reserva confirmada correctamente'}, 200
        else:
            return {'msg': response}, 500

class Completar_Reserva(Resource):
    @token_required
    @roles_required('Traveler')
    def post(current_user, self, reserva_id):
        #Traemos la reserva por id
        reserva = reservas_crud.reservaById(reserva_id)

        #Validamos que el user_id del token pueda completar la reserva
        if reserva.get('user_id') != current_user.get('sub'):
            return {'msg': 'No tienes permisos para completar esta reserva'}, 403

        #Llamamos a inventario para traer el id del hospedaje
        hospedaje_id = ReservaHelper.hospedajeId(INVENTARIOS_URL, reserva.get('habitacion_id'))
        
        response = reservas_crud.completarReserva(reserva_id)
        
        if response:
            return {
                'msg': 'Reserva completada correctamente',
                'reserva': {
                    'reserva_id': reserva.get('public_id'),
                    'check_in': reserva.get('check_in'),
                    'check_out': reserva.get('check_out'),
                    'nombre_hospedaje': hospedaje_id.get('nombre'),
                    'tipo_habitacion': hospedaje_id.get('tipo_habitacion'),
                }
            }
        
        else:
            return {'msg': response}, 500

class Revocar_Reserva(Resource):
    def post(self, reserva_id):
        response, reserva = reservas_crud.revocarReserva(reserva_id)

        #Enviamos notificación a OneSignal
        notification_title = f"Cancelación reserva: {reserva.get('public_id')}"
        notification_message = f"Tu reserva del {reserva.get('check_in')} al {reserva.get('check_out')} ha sido cancelada."
        one_signal_helper.sendNotificacion(notification_title, notification_message, reserva.get('user_id'))

        if response:
            return {'msg': 'Reserva revocada correctamente'}, 200

        return {'msg': response}, 500

class Reservas_por_usuario(Resource):
    @token_required
    def get(current_user, self, user_id):
        try:
            if current_user.get('sub') != user_id:
                return {'msg': 'No tienes permisos para ver las reservas de este usuario'}, 403
            
            reservas = reservas_crud.obtenerReservasPorUsuario(user_id)
            return reservas, 200
        except Exception as e:
            return {'msg': 'Error al obtener las reservas del usuario', 'error': str(e)}, 500

class ReservaById(Resource):
    def get(self, reserva_id):
        try:
            reserva = reservas_crud.reservaById(reserva_id)
            if reserva:
                return reserva, 200
            else:
                return {'msg': 'Reserva no encontrada'}, 404
        except Exception as e:
            return {'msg': 'Error al obtener la reserva', 'error': str(e)}, 500

class CleanDB(Resource):
    def post(self):
        reservas_crud.resetDb()
        return {'msg': 'Base de datos reiniciada correctamente'}, 200




        

