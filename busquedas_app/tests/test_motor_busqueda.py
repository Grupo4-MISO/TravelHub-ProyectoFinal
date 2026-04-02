from app.utils.inventario_helper import InventarioHelper
from app.utils.busquedas_helper import BusquedasHelper
from app.utils.reserva_helper import ReservaHelper
from app.errors.exceptions import BadRequestError
from app.utils.cache_helper import CacheHelper
from app.api.api import Search
from flask_restful import Api
from flask import Flask
import pytest

def test_validacion_campo_ciudad_vacio():
    with pytest.raises(BadRequestError) as exc_info:
        BusquedasHelper.validacionCampoCiudad()

    assert str(exc_info.value) == 'El campo ciudad no debe ser vacío'

def test_validacion_campo_ciudad_numero():
    with pytest.raises(BadRequestError) as exc_info:
        BusquedasHelper.validacionCampoCiudad('123')

    assert str(exc_info.value) == 'El campo ciudad debe ser un texto'

def test_validacion_campo_ciudad_valido():
    resultado = BusquedasHelper.validacionCampoCiudad('Bogota')

    assert resultado is None

def test_limpieza_campo_ciudad():
    resultado = BusquedasHelper.limpiarCampoCiudad('  Bogotá  ')

    assert resultado == 'Bogota'

def test_validacion_campo_capacidad_vacio():
    with pytest.raises(BadRequestError) as exc_info:
        BusquedasHelper.validacionCampoCapacidad()

    assert str(exc_info.value) == 'El campo capacidad no debe ser vacío'

def test_validacion_campo_capacidad_no_numero():
    with pytest.raises(BadRequestError) as exc_info:
        BusquedasHelper.validacionCampoCapacidad('abc')

    assert str(exc_info.value) == 'El campo capacidad debe ser un número entero'

def test_validacion_campo_capacidad_negativo():
    with pytest.raises(BadRequestError) as exc_info:
        BusquedasHelper.validacionCampoCapacidad('-1')

    assert str(exc_info.value) == 'El campo capacidad debe ser un número entero positivo'

def test_validacion_campo_capacidad_valido():
    resultado = BusquedasHelper.validacionCampoCapacidad('2')

    assert resultado is None

def test_validacion_campo_fechas_check_in_vacio():
    with pytest.raises(BadRequestError) as exc_info:
        BusquedasHelper.validacionCampoFechas(None, '2024-12-31')

    assert str(exc_info.value) == 'La fecha de check-in no debe ser vacía'

def test_validacion_campo_fechas_check_out_vacio():
    with pytest.raises(BadRequestError) as exc_info:
        BusquedasHelper.validacionCampoFechas('2024-12-31', None)

    assert str(exc_info.value) == 'La fecha de check-out no debe ser vacía'

def test_validacion_campo_fechas_check_in_formato_invalido():
    with pytest.raises(BadRequestError) as exc_info:
        BusquedasHelper.validacionCampoFechas('31-12-2024', '2024-12-31')

    assert str(exc_info.value) == 'La fecha de check-in debe estar en formato YYYY-MM-DD'

def test_validacion_campo_fechas_check_out_formato_invalido():
    with pytest.raises(BadRequestError) as exc_info:
        BusquedasHelper.validacionCampoFechas('2024-12-31', '31-12-2024')

    assert str(exc_info.value) == 'La fecha de check-out debe estar en formato YYYY-MM-DD'

def test_validacion_campo_fechas_check_in_mayor_check_out():
    with pytest.raises(BadRequestError) as exc_info:
        BusquedasHelper.validacionCampoFechas('2027-12-31', '2027-12-30')

    assert str(exc_info.value) == 'La fecha de check-out debe ser posterior a la fecha de check-in'

def test_validacion_campo_fechas_check_in_menor_fecha_actual():
    with pytest.raises(BadRequestError) as exc_info:
        BusquedasHelper.validacionCampoFechas('2020-01-01', '2024-12-31')

    assert str(exc_info.value) == 'La fecha de check-in debe ser una fecha futura'

def test_validacion_campo_fechas_check_out_menor_fecha_actual():
    with pytest.raises(BadRequestError) as exc_info:
        BusquedasHelper.validacionCampoFechas('2027-03-25', '2024-12-31')

    assert str(exc_info.value) == 'La fecha de check-out debe ser una fecha futura'

def test_construir_cache_key():
    resultado = CacheHelper.construirCacheKey('Bogota', '2', '2024-12-01', '2024-12-31')

    assert resultado == 'search:Bogota:2:2024-12-01:2024-12-31'

def test_obtener_inventario_error(mocker):
    error = 'Error al consultar el microservicio de inventario: Error de conexión'

    #Mockeamos una excepción al hacer la consulta al microservicio de inventario
    mocker.patch('app.utils.inventario_helper.requests.get', side_effect = Exception(error))

    try:
        InventarioHelper.getInventario('http://inventarios', 'Bogota', '2')

    except Exception as e:
        assert str(e) == error

def test_obtener_inventario_exitoso(mocker):
    #Hacemos el mock
    mock_response = mocker.Mock()
    mock_response.raise_for_status.return_value = None

    #Creamos una respuesta mock del microservicio de inventario
    mock_response.json.return_value = [
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
    mocker.patch('app.utils.inventario_helper.requests.get', return_value = mock_response)

    resultado = InventarioHelper.getInventario('http://inventarios', 'Bogota', '2')

    assert resultado == mock_response.json.return_value

def test_obtener_reserva_error(mocker):
    error = 'Error al consultar el microservicio de reservas: Error de conexión'

    #Mockeamos una excepción al hacer la consulta al microservicio de reservas
    mocker.patch('app.utils.reserva_helper.requests.post', side_effect = Exception(error))

    #Creamos parametros de la funcion
    habitaciones_ids = ['1', '2']
    check_in = '2024-12-01'
    check_out = '2024-12-31'

    try:
        ReservaHelper.disponibilidadReserva('http://reservas', habitaciones_ids, check_in, check_out)

    except Exception as e:
        assert str(e) == error

def test_obtener_reserva_exitoso(mocker):
    #Hacemos el mock
    mock_response = mocker.Mock()
    mock_response.raise_for_status.return_value = None

    #Creamos una respuesta mock del microservicio de inventario
    mock_response.json.return_value = ['1', '2']

    #Mockeamos la respuesta del microservicio de reservas
    mocker.patch('app.utils.reserva_helper.requests.post', return_value = mock_response)

    #Creamos parametros de la funcion
    habitaciones_ids = ['1', '2']
    check_in = '2024-12-01'
    check_out = '2024-12-31'

    resultado = ReservaHelper.disponibilidadReserva('http://reservas', habitaciones_ids, check_in, check_out)

    assert resultado == mock_response.json.return_value

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

def test_busqueda_completa(mocker):
    #Creamos app
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(Search, "/search")
    client = app.test_client()

    #Parametros de busqueda
    ciudad = 'Bogota'
    capacidad = '2'
    check_in = '2027-12-01'
    check_out = '2027-12-31'

    #Inventario mock del microservicio de inventario
    mock_inventario = [
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

    #Reserva mock del microservicio de reservas
    mock_reserva = ['1']

    #Mockeamos la validación de los campos
    mocker.patch('app.utils.busquedas_helper.BusquedasHelper.validacionCampoCiudad', return_value = None)
    mocker.patch('app.utils.busquedas_helper.BusquedasHelper.validacionCampoCapacidad', return_value = None)
    mocker.patch('app.utils.busquedas_helper.BusquedasHelper.validacionCampoFechas', return_value = None)

    #Mockeamos la construccion del cache key y obtener cache
    mocker.patch('app.utils.cache_helper.CacheHelper.construirCacheKey', return_value = f"search:{ciudad}:{capacidad}:{check_in}:{check_out}")
    mocker.patch('app.utils.cache_helper.CacheHelper.obtenerCache', return_value = None)

    #Mockeamos la consulta al microservicio de inventario
    mocker.patch('app.utils.inventario_helper.InventarioHelper.getInventario', return_value = mock_inventario)

    #Mockeamos la consulta al microservicio de reservas
    mocker.patch('app.utils.reserva_helper.ReservaHelper.disponibilidadReserva', return_value = mock_reserva)

    #Mockeamos guardado de cache
    mocker.patch('app.utils.cache_helper.CacheHelper.guardarCache', return_value = None)

    #Realizamos consulta a la API
    response = client.get('/search', query_string = {
        'ciudad': ciudad,
        'capacidad': capacidad,
        'check_in': check_in,
        'check_out': check_out
    })

    assert response.status_code == 200
    assert response.json == [mock_inventario[0]]
    assert response.json[0]['habitacion_id'] == '1'
    assert len(response.json) == 1

