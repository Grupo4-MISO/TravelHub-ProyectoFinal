from app.api.api import ListadoCiudades
from flask_restful import Api
from flask import Flask

def test_listado_ciudades(mocker):
    #Creamos app
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(ListadoCiudades, '/ciudades')
    client = app.test_client()

    #Mockeamos la respuesta del CRUD
    ciudades = {
        "Barranquilla": "Colombia",
        "Cali": "Colombia",
        "Medellin": "Colombia"
    }
    mocker.patch('app.services.inventario_crud.InventarioCRUD.listadoCiudades', return_value = ciudades)

    #Hacemos peticion GET
    response = client.get('/ciudades')

    assert response.status_code == 200
    assert response.get_json() == ciudades
    assert len(response.get_json()) == len(ciudades)
    assert 'Barranquilla' in response.get_json()