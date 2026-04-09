from app.api.api import ListadoCiudades
from app.api.api import ListadoPaises
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