from app.api.api import InventarioHealth, HospedajeSearchResource
from app.db.habitacion import db_habitacion
from app.db.hospedaje import db_hospedaje
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_cors import CORS
from flask import Flask

#Creamos la aplicacion de Flask
app = Flask(__name__)

#Ponemos configuraciones de la app
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://proyectogrupo10:proyectogrupo10@terraform-20251122212627271800000001.cifuwoics1ov.us-east-1.rds.amazonaws.com:5432/proyect_db'
app.config['JWT_SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600

#Inicializamos la base de datos
if not app.config.get('TESTING'):
    with app.app_context():
        #Creamos tabla de hospedaje
        db_hospedaje.init_app(app)
        db_hospedaje.create_all()

        #Creamos tabla de habitacion
        db_habitacion.init_app(app)
        db_habitacion.create_all()

#Habilitamos CORS
CORS(app)

#Inicializamos el JWTManager
jwt = JWTManager(app)

#Registramos la API RESTful
api = Api(app)
api.add_resource(InventarioHealth, 'api/v1/health')
api.add_resource(HospedajeSearchResource, 'api/v1/hospedajes/search')

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5000, debug = True)