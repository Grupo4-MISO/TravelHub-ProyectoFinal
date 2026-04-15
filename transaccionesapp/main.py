from app.api.api import (
    Health,
    PaymentByProviderIdResource,
    PaymentByReservaIdResource,
    PaymentProviderByIdResource,
    PaymentProviderResource,
    PaymentResource,
    PaymentResourceById,
    PaymentTransactionByIdResource,
    PaymentTransactionByPaymentIdResource,
    PaymentTransactionResource,
    SeedDB,
)
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
    "title": "TravelHub Managers API",
    "uiversion": 3
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "TravelHub Transactions API",
        "description": "Documentación de endpoints de transacciones",
        "version": "1.0.0"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Formato: Bearer <token_jwt>"
        }
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

api.add_resource(Health, '/api/v1/Transactions/health')

api.add_resource(PaymentProviderResource, '/api/v1/Transactions/providers')
api.add_resource(PaymentProviderByIdResource, '/api/v1/Transactions/providers/<string:id>')

api.add_resource(PaymentResource, '/api/v1/Transactions/payments')
api.add_resource(PaymentResourceById, '/api/v1/Transactions/payments/<string:id>')
api.add_resource(PaymentByReservaIdResource, '/api/v1/Transactions/payments/reserva/<string:reserva_id>')
api.add_resource(PaymentByProviderIdResource, '/api/v1/Transactions/payments/provider/<string:provider_id>')

api.add_resource(PaymentTransactionResource, '/api/v1/Transactions/attempts')
api.add_resource(PaymentTransactionByIdResource, '/api/v1/Transactions/attempts/<string:id>')
api.add_resource(PaymentTransactionByPaymentIdResource, '/api/v1/Transactions/attempts/payment/<string:payment_id>')

api.add_resource(SeedDB, '/api/v1/Transactions/seed')

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5006, debug=True)
