from app.api.api import CountryList, PopularCitiesByCountry, InventarioHealth, FiltroHabitaciones, SeedDB, HospedajeCollection
from app.api.api import CountryList, PopularCitiesByCountry, InventarioHealth, FiltroHabitaciones, SeedDB, HospedajeCollection, HospedajeById
from app.errors.handlers import ErrorHandler
from flask_restful import Api
from app.db.models import db
from flask_cors import CORS
from flask import Flask
import os
from flasgger import Swagger

#Traemos del ambiente las variables de configuracion
DATABASE_URL = os.getenv('DATABASE_URL')

#Creamos la aplicacion de Flask
app = Flask(__name__)

#Registramos el manejador de errores
ErrorHandler.errors(app)

#Ponemos configuraciones de la app
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///inventario.db')
app.config['JWT_SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600
app.config["SWAGGER"] = {
    "title": "TravelHub Inventario API",
    "uiversion": 3
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "TravelHub Inventario API",
        "description": "Documentación de endpoints de inventario",
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

#Inicializamos la base de datos
if not app.config.get('TESTING'):
    with app.app_context():
        #Creamos tablas en la base de datos
        db.init_app(app)
        db.create_all()

#Habilitamos CORS
CORS(app)

#Registramos la API RESTful
api = Api(app)
api.add_resource(InventarioHealth, '/api/v1/inventarios/health')
api.add_resource(CountryList, '/api/v1/inventarios/countries')
api.add_resource(PopularCitiesByCountry, '/api/v1/inventarios/countries/<code>/popular-cities')
api.add_resource(FiltroHabitaciones, '/api/v1/inventarios/filtro')
api.add_resource(SeedDB, '/api/v1/inventarios/seed')
api.add_resource(HospedajeCollection, '/api/v1/inventarios/hospedajes')
api.add_resource(HospedajeById, '/api/v1/inventarios/hospedajes/<string:hospedaje_id>')
