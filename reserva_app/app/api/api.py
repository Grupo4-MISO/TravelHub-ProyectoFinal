from app.services.reserva_crud import ReservaCRUD
from app.services.hold_service import HoldService
from app.utils.seedHelper import SeedHelper
from app.utils.helper import ReservaHelper
from flask_restful import Resource
from datetime import datetime
from flask import request

#Instanciamos crud
reservas_crud = ReservaCRUD()

class ReservaHealth(Resource):
    def get(self):
        return {'status': 'healthy'}, 200

class VerificarDisponibilidad(Resource):
    def post(self):
        #Obtenemos los datos del request
        data = request.get_json()

        #Validamos campos de fechas
        check_in, check_out = ReservaHelper.validacionCampoFechas(data.get('check_in'), data.get('check_out'))

        #Obtenemos datos del request de ids
        habitaciones_ids = data.get('habitacion_ids')

        #Verificamos disponibilidad
        disponibilidad = reservas_crud.verificarDisponibilidad(habitaciones_ids, check_in, check_out)
    
        return disponibilidad, 200

class SeedReservas(Resource):
    def post(self, cantidad):
        if cantidad <= 0:
            return {'msg': 'La cantidad debe ser un entero positivo'}, 400

        result = SeedHelper.reset_and_seed(cantidad)

        if not result.get('ok'):
            return {'msg': 'Error al ejecutar el seed', 'error': result.get('error')}, 500

        response = {
            'msg': 'Seed ejecutado correctamente',
            'solicitadas': result['solicitadas'],
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
