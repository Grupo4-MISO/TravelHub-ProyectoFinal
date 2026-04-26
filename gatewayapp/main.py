from app.api.api import (
    Health, InventarioProxy, BusquedasProxy, ReservaProxy, AuthProxy, 
    ClientesProxy, ComentariosProxy, TransaccionesProxy, ProveedoresProxy, StartAllServices
)
from flask_restful import Api
from flask_cors import CORS
from flask import Flask
import os
from flasgger import Swagger


#Creamos la aplicacion de Flask
app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = 'o+jGoFFM5+EZULQUkXUkmxNU9eGSxU89GlCG9hbNSYI='
app.config['SECRET_KEY'] = app.config['JWT_SECRET_KEY']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600
app.config["SWAGGER"] = {
    "title": "TravelHub Managers API",
    "uiversion": 3
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "TravelHub Gateway API",
        "description": "Documentación de endpoints del gateway de TravelHub",
        "version": "1.0.0"
    },
    "basePath": "/",
    "schemes": ["http"]
}

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec_1",
            "route": "/apispec_1.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/swagger/"
}

Swagger(app, config=swagger_config, template=swagger_template)

#Habilitamos CORS
CORS(app)

#Registramos la API RESTful
api = Api(app)

api.add_resource(Health, '/api/v1/Gateway/health')
api.add_resource(InventarioProxy, '/api/v1/inventarios/<path:path>')
api.add_resource(BusquedasProxy, '/api/v1/busquedas/<path:path>')
api.add_resource(ReservaProxy, '/api/v1/reservas/<path:path>')
api.add_resource(AuthProxy, '/api/v1/auth/<path:path>')
api.add_resource(ClientesProxy, '/api/v1/Travelers/<path:path>')
api.add_resource(ComentariosProxy, '/api/v1/reviews/<path:path>')
api.add_resource(TransaccionesProxy, '/api/v1/Transactions/<path:path>')
api.add_resource(ProveedoresProxy, '/api/v1/Managers/<path:path>')
api.add_resource(StartAllServices, '/api/v1/Gateway/start-services')


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=3010, debug=True)
