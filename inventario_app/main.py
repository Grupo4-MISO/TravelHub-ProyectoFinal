from app.api.api import InventarioHealth, FiltroHabitaciones
from flask_restful import Api
from app.db.models import db
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
        #Creamos tablas en la base de datos
        db.init_app(app)
        db.create_all()

#Habilitamos CORS
CORS(app)

#Registramos la API RESTful
api = Api(app)
api.add_resource(InventarioHealth, 'api/v1/health')
api.add_resource(FiltroHabitaciones, 'api/v1/habitaciones/filtro')