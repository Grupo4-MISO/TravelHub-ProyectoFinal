from app.api.api import ListadoCiudades
from app.api.api import ListadoPaises
from app.api.api import HospedajeById
from app.errors.exceptions import DatababaseError
from flask_restful import Api
from flask import Flask

def test_listado_ciudades(mocker):
    #Creamos app
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(ListadoCiudades, '/ciudades')
    client = app.test_client()

    #Mockeamos la respuesta del CRUD
    ciudades = [
        {'ciudad': 'Barranquilla', 'pais': 'Colombia'},
        {'ciudad': 'Cartagena', 'pais': 'Colombia'},
        {'ciudad': 'Medellín', 'pais': 'Colombia'},
    ]
    mocker.patch('app.services.inventario_crud.InventarioCRUD.listadoCiudades', return_value = ciudades)

    #Hacemos peticion GET
    response = client.get('/ciudades')

    assert response.status_code == 200
    assert response.get_json() == ciudades
    assert len(response.get_json()) == len(ciudades)
    assert {'ciudad': 'Barranquilla', 'pais': 'Colombia'} in response.get_json()

def test_listado_paises(mocker):
    #Creamos app
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(ListadoPaises, '/paises')
    client = app.test_client()

    #Mockeamos la respuesta del CRUD
    paises = ['Colombia', 'Argentina', 'Peru']
    mocker.patch('app.services.inventario_crud.InventarioCRUD.listadoPaises', return_value = paises)

    #Hacemos peticion GET
    response = client.get('/paises')

    assert response.status_code == 200
    assert response.get_json() == paises
    assert len(response.get_json()) == len(paises)
    assert 'Colombia' in response.get_json()


def test_hospedaje_por_id_ok(mocker):
    #Creamos app
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(HospedajeById, '/hospedajes/<string:hospedaje_id>/<string:currency_code>')
    client = app.test_client()

    hospedaje_id = '859f1435-879b-4590-b09c-33bb3ab9df0e'
    moneda = 'COP'
    hospedaje = {
        'id': hospedaje_id,
        'nombre': 'Sofitel Bogota Victoria Regia',
        'habitaciones': [],
        'amenidades': [],
        'imagenes': [],
    }
    mocker.patch(
        'app.services.inventario_crud.InventarioCRUD.obtener_hospedaje_por_id',
        return_value=hospedaje
    )

    #Hacemos peticion GET
    response = client.get(f'/hospedajes/{hospedaje_id}/{moneda}')

    assert response.status_code == 200
    assert response.get_json() == hospedaje


def test_hospedaje_por_id_no_encontrado(mocker):
    #Creamos app
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(HospedajeById, '/hospedajes/<string:hospedaje_id>/<string:currency_code>')
    client = app.test_client()

    hospedaje_id = '00000000-0000-0000-0000-000000000000'
    moneda = 'COP'
    mocker.patch(
        'app.services.inventario_crud.InventarioCRUD.obtener_hospedaje_por_id',
        return_value=None
    )

    #Hacemos peticion GET
    response = client.get(f'/hospedajes/{hospedaje_id}/{moneda}')

    assert response.status_code == 404
    assert response.get_json() == {
        'msg': f'Hospedaje no encontrado para id {hospedaje_id}'
    }


def test_hospedaje_por_id_uuid_invalido(mocker):
    #Creamos app
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(HospedajeById, '/hospedajes/<string:hospedaje_id>/<string:currency_code>')
    client = app.test_client()

    hospedaje_id = 'id-invalido'
    moneda = 'COP'
    error = DatababaseError('El id del hospedaje no tiene un formato UUID válido')
    mocker.patch(
        'app.services.inventario_crud.InventarioCRUD.obtener_hospedaje_por_id',
        return_value=error
    )

    #Hacemos peticion GET
    response = client.get(f'/hospedajes/{hospedaje_id}/{moneda}')

    assert response.status_code == 400
    assert response.get_json() == {'msg': error.message}


def test_hospedaje_por_id_error_db(mocker):
    #Creamos app
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(HospedajeById, '/hospedajes/<string:hospedaje_id>/<string:currency_code>')
    client = app.test_client()

    hospedaje_id = '859f1435-879b-4590-b09c-33bb3ab9df0e'
    moneda = 'COP'
    error = DatababaseError('Error en la base de datos: fallo inesperado')
    mocker.patch(
        'app.services.inventario_crud.InventarioCRUD.obtener_hospedaje_por_id',
        return_value=error
    )

    #Hacemos peticion GET
    response = client.get(f'/hospedajes/{hospedaje_id}/{moneda}')

    assert response.status_code == 500
    assert response.get_json() == {'msg': error.message}