from app.api.api import Search, SearchHealth, SeedDB
from app.errors.handlers import ErrorHandler
from flask_restful import Api
from flask_cors import CORS
from flask import Flask
from flasgger import Swagger

#Creamos la aplicacion de Flask
app = Flask(__name__)

#Registramos el manejador de errores
ErrorHandler.errors(app)

#Ponemos configuraciones de la app
app.config['JWT_SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = False
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600
app.config["SWAGGER"] = {
    "title": "TravelHub Busquedas API",
    "uiversion": 3
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "TravelHub Busquedas API",
        "description": "Documentación de endpoints del motor de búsquedas de TravelHub",
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
CORS(app, resources={r"/api/*": {"origins": "*"}})

#Registramos la API RESTful
api = Api(app)
api.add_resource(SearchHealth, '/api/v1/busquedas/health')
api.add_resource(Search, '/api/v1/busquedas/search')
api.add_resource(SeedDB, '/api/v1/busquedas/seed')

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=3002, debug=True)
