from app.api.api import CleanDB, ReservaHealth, Reservas_por_usuario, VerificarDisponibilidad, SeedReservas, HoldReserva, darReservas, TarifaReserva, Confirmar_Reserva, Revocar_Reserva, CrearReserva
from app.errors.handlers import ErrorHandler
from app.db.models import db
from flask_restful import Api
from app.db.models import db
from flask_cors import CORS
from flask import Flask
import os

API_PREFIX = '/api/v1/reservas'

#Traemos del ambiente las variables de configuracion
DATABASE_URL = os.getenv('DATABASE_URL') 

#Creamos la aplicacion de Flask
app = Flask(__name__)

#Registramos el manejador de errores
ErrorHandler.errors(app)

#Ponemos configuraciones de la app
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    "DATABASE_URL",
    "sqlite:///travelhub.db"
)
#app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['JWT_SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600
app.config['HOLD_TTL_SECONDS'] = os.getenv('HOLD_TTL_SECONDS', 900)

#Inicializamos la base de datos
if not app.config.get('TESTING'):
    with app.app_context():
        #Creamos tabla de reservas en la base de datos
        db.init_app(app)
        db.create_all()

#Habilitamos CORS
CORS(app)

#Registramos la API RESTful
api = Api(app, prefix=API_PREFIX)
api.add_resource(ReservaHealth, '/health')
api.add_resource(VerificarDisponibilidad, '/disponibilidad')
api.add_resource(CrearReserva, '/crear')
api.add_resource(SeedReservas, '/seed/<int:cantidad>')
api.add_resource(HoldReserva, '/hold')
api.add_resource(darReservas, '')
api.add_resource(TarifaReserva, '/tarifa')
api.add_resource(CleanDB, '/clean')
api.add_resource(Confirmar_Reserva, '/confirmar/<string:reserva_id>')
api.add_resource(Revocar_Reserva, '/revocar/<string:reserva_id>')
api.add_resource(Reservas_por_usuario, '/api/v1/reservas/usuario/<string:user_id>')
