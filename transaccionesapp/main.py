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
    SeedDB,
)
from flask_restful import Api
from app.db.models import db
from flask_cors import CORS
from flask import Flask
import os
from flasgger import Swagger
from app.errors.handlers import ErrorHandler

API_PREFIX = '/api/v1/Transactions'

#Traemos del ambiente las variables de configuracion
DATABASE_URL = os.getenv('DATABASE_URL')

#Creamos la aplicacion de Flask
app = Flask(__name__)

#Registramos el manejador de errores
ErrorHandler.errors(app)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['JWT_SECRET_KEY'] = 'o+jGoFFM5+EZULQUkXUkmxNU9eGSxU89GlCG9hbNSYI='
app.config['SECRET_KEY'] = app.config['JWT_SECRET_KEY']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600
app.config['EXTERNAL_PAYMENT_SESSION_URL'] = os.getenv(
    'EXTERNAL_PAYMENT_SESSION_URL',
    'https://external-payment-provider.onrender.com/payment-sessions'
)
app.config['PAYMENT_WEBHOOK_URL'] = os.getenv(
    'PAYMENT_WEBHOOK_URL',
    'https://v7iqo4ymndw6lnektybll5za4y0udwfi.lambda-url.us-east-1.on.aws'
)
app.config['PAYMENT_SIMULATE_OUTCOME'] = os.getenv('PAYMENT_SIMULATE_OUTCOME', 'success')
app.config['PAYMENT_CALLBACK_DELAY_SECONDS'] = int(os.getenv('PAYMENT_CALLBACK_DELAY_SECONDS', '20'))
app.config['PAYMENT_SESSION_TIMEOUT_SECONDS'] = int(os.getenv('PAYMENT_SESSION_TIMEOUT_SECONDS', '10'))
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

db.init_app(app)

if not app.config.get('TESTING'):
    with app.app_context():
        db.create_all()

#Habilitamos CORS
CORS(app)

#Registramos la API RESTful
api = Api(app, prefix=API_PREFIX)

api.add_resource(Health, '/health')

api.add_resource(PaymentProviderResource, '/providers')
api.add_resource(PaymentProviderByIdResource, '/providers/<string:id>')

api.add_resource(PaymentResource, '/payments')
api.add_resource(PaymentResourceById, '/payments/<string:id>')
api.add_resource(PaymentByReservaIdResource, '/payments/reserva/<string:reserva_id>')
api.add_resource(PaymentByProviderIdResource, '/payments/provider/<string:provider_id>')

api.add_resource(PaymentTransactionByIdResource, '/attempts/<string:id>')
api.add_resource(PaymentTransactionByPaymentIdResource, '/attempts/payment/<string:payment_id>')

api.add_resource(SeedDB, '/seed')
