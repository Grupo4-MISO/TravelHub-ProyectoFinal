from app.utils.inventario_helper import InventarioHelper
from app.utils.busquedas_helper import BusquedasHelper
from app.utils.reserva_helper import ReservaHelper
from app.utils.cache_helper import CacheHelper

def test_validacion_campo_ciudad_vacio():
    resultado = BusquedasHelper.validacionCampoCiudad('')

    assert resultado == 'El campo ciudad no debe ser vacío'

def test_validacion_campo_ciudad_numero():
    resultado = BusquedasHelper.validacionCampoCiudad('123')

    assert resultado == 'El campo ciudad debe ser un texto'

def test_validacion_campo_ciudad_valido():
    resultado = BusquedasHelper.validacionCampoCiudad('Bogota')

    assert resultado is None

def test_validacion_campo_capacidad_vacio():
    resultado = BusquedasHelper.validacionCampoCapacidad('')

    assert resultado == 'El campo capacidad no debe ser vacío'

def test_validacion_campo_capacidad_no_numero():
    resultado = BusquedasHelper.validacionCampoCapacidad('abc')

    assert resultado == 'El campo capacidad debe ser un número entero'

def test_validacion_campo_capacidad_negativo():
    resultado = BusquedasHelper.validacionCampoCapacidad('-1')

    assert resultado == 'El campo capacidad debe ser un número entero positivo'

def test_validacion_campo_capacidad_valido():
    resultado = BusquedasHelper.validacionCampoCapacidad('2')

    assert resultado is None

def test_validacion_campo_fechas_check_in_vacio():
    resultado = BusquedasHelper.validacionCampoFechas('', '2024-12-31')

    assert resultado == 'La fecha de check-in no debe ser vacía'

def test_validacion_campo_fechas_check_out_vacio():
    resultado = BusquedasHelper.validacionCampoFechas('2024-12-31', '')

    assert resultado == 'La fecha de check-out no debe ser vacía'

def test_validacion_campo_fechas_check_in_formato_invalido():
    resultado = BusquedasHelper.validacionCampoFechas('31-12-2024', '2024-12-31')

    assert resultado == 'La fecha de check-in debe estar en formato YYYY-MM-DD'

def test_validacion_campo_fechas_check_out_formato_invalido():
    resultado = BusquedasHelper.validacionCampoFechas('2024-12-31', '31-12-2024')

    assert resultado == 'La fecha de check-out debe estar en formato YYYY-MM-DD'

def test_validacion_campo_fechas_check_in_mayor_check_out():
    resultado = BusquedasHelper.validacionCampoFechas('2024-12-31', '2024-12-30')

    assert resultado == 'La fecha de check-out debe ser posterior a la fecha de check-in'

def test_validacion_campo_fechas_check_in_menor_fecha_actual():
    resultado = BusquedasHelper.validacionCampoFechas('2020-01-01', '2024-12-31')

    assert resultado == 'La fecha de check-in debe ser una fecha futura'

def test_validacion_campo_fechas_check_out_menor_fecha_actual():
    resultado = BusquedasHelper.validacionCampoFechas('2027-01-01', '2024-12-31')

    assert resultado == 'La fecha de check-out debe ser una fecha futura'

def test_construir_cache_key():
    resultado = CacheHelper.construirCacheKey('Bogota', '2', '2024-12-01', '2024-12-31')

    assert resultado == 'search:Bogota:2:2024-12-01:2024-12-31'

def test_obtener_inventario_error(mocker):
    #Mockeamos una excepción al hacer la consulta al microservicio de inventario
    mocker.patch('app.utils.inventario_helper.requests.get', side_effect = Exception('Error de conexión'))

    try:
        InventarioHelper.getInventario('http://inventarios', 'Bogota', '2')

    except Exception as e:
        assert str(e) == 'Error al consultar el microservicio de inventario: Error de conexión'

def test_obtener_inventario_exitoso(mocker):
    #Creamos una respuesta mock del microservicio de inventario
    inventario_mock = [
        {
            'habitacion_id': '1',
            'hospedaje_id': '1',
            'nombre': 'Habitación 1',
            'pais': 'Colombia',
            'ciudad': 'Bogota',
            'direccion': 'Calle 123',
            'rating': 4.5,
            'capacidad': 2,
            'precio': 100.0
        }
    ]
    
    #Mockeamos la respuesta del microservicio de inventario
    mocker.patch('app.utils.inventario_helper.requests.get', return_value = inventario_mock)

    resultado = InventarioHelper.getInventario('http://inventarios', 'Bogota', '2')

    assert resultado == inventario_mock

def test_obtener_reserva_error(mocker):
    #Mockeamos una excepción al hacer la consulta al microservicio de reservas
    mocker.patch('app.utils.reserva_helper.requests.post', side_effect = Exception('Error de conexión'))

    #Creamos parametros de la funcion
    habitaciones_ids = ['1', '2']
    check_in = '2024-12-01'
    check_out = '2024-12-31'

    try:
        ReservaHelper.disponibilidadReserva('http://reservas', habitaciones_ids, check_in, check_out)

    except Exception as e:
        assert str(e) == 'Error al consultar el microservicio de reservas: Error de conexión'

def test_obtener_reserva_exitoso(mocker):
    #Creamos una respuesta mock del microservicio de reservas
    disponibles = ['1', '2']

    #Mockeamos la respuesta del microservicio de reservas
    mocker.patch('app.utils.reserva_helper.requests.post', return_value = disponibles)

    #Creamos parametros de la funcion
    habitaciones_ids = ['1', '2']
    check_in = '2024-12-01'
    check_out = '2024-12-31'

    resultado = ReservaHelper.disponibilidadReserva('http://reservas', habitaciones_ids, check_in, check_out)

    assert resultado == disponibles

def test_filtrar_habitaciones_disponibles():
    #Creamos el inventario
    inventario = [
        {
            'habitacion_id': '1',
            'hospedaje_id': '1',
            'nombre': 'Habitación 1',
            'pais': 'Colombia',
            'ciudad': 'Bogota',
            'direccion': 'Calle 123',
            'rating': 4.5,
            'capacidad': 2,
            'precio': 100.0
        },
        {
            'habitacion_id': '2',
            'hospedaje_id': '1',
            'nombre': 'Habitación 2',
            'pais': 'Colombia',
            'ciudad': 'Bogota',
            'direccion': 'Calle 123',
            'rating': 4.0,
            'capacidad': 2,
            'precio': 80.0
        }
    ]

    #Creamos la lista de habitaciones disponibles
    disponibles = ['1']

    resultado = BusquedasHelper.filtrarHabitacionesDisponibles(inventario, disponibles)

    assert resultado == [inventario[0]]
    assert len(resultado) == 1