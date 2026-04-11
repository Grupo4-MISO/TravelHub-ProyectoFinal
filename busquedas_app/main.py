from app.api.api import Search, SearchHealth, SeedDB
from app.errors.handlers import ErrorHandler
from flask_restful import Api
from flask_cors import CORS
from flask import Flask

#Creamos la aplicacion de Flask
app = Flask(__name__)

#Registramos el manejador de errores
ErrorHandler.errors(app)

#Ponemos configuraciones de la app
app.config['JWT_SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600

#Habilitamos CORS
CORS(app)

#Registramos la API RESTful
api = Api(app)
api.add_resource(SearchHealth, '/api/v1/busquedas/health')
api.add_resource(Search, '/api/v1/busquedas/search')
api.add_resource(SeedDB, '/api/v1/busquedas/seed')
