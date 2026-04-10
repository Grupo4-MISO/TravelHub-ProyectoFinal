from app.api.api import Health, ReviewResource, ReviewResourceById, ReviewByHospedajeResource, SeedDB
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

#Ponemos configuraciones de la app
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    "DATABASE_URL",
    "sqlite:///travelhub.db"
)
#app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['JWT_SECRET_KEY'] = 'o+jGoFFM5+EZULQUkXUkmxNU9eGSxU89GlCG9hbNSYI='
app.config['SECRET_KEY'] = app.config['JWT_SECRET_KEY']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600
app.config["SWAGGER"] = {
    "title": "TravelHub Comments API",
    "uiversion": 3
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "TravelHub Comments API",
        "description": "Documentación de endpoints de comentarios",
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

# Configuración de base de datos (pruebas locales)
# app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://usuario:password@localhost:5432/travelhub"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///travelhub.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

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

api.add_resource(Health, '/api/v1/health')
api.add_resource(ReviewResource, '/api/v1/reviews')
api.add_resource(ReviewResourceById, '/api/v1/reviews/<string:id>')
api.add_resource(
    ReviewByHospedajeResource,
    '/api/v1/reviews/hospedajes/<string:id>'
)
api.add_resource(SeedDB, '/api/v1/seed')

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5004, debug=True)
