from app.api.api import Health, TarifaResource, TarifaListResource, SeedDB, DescuentoListResource, DescuentoResource
from flask_restful import Api
from app.db.models import db
from flask_cors import CORS
from flask import Flask
import os
from flasgger import Swagger

# Traemos del ambiente las variables de configuracion
DATABASE_URL = os.getenv('DATABASE_URL')

# Creamos la aplicacion de Flask
app = Flask(__name__)

# Ponemos configuraciones de la app
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///travelhub.db")
app.config['JWT_SECRET_KEY'] = 'o+jGoFFM5+EZULQUkXUkmxNU9eGSxU89GlCG9hbNSYI='
app.config['SECRET_KEY'] = app.config['JWT_SECRET_KEY']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600
app.config["SWAGGER"] = {
    "title": "TravelHub Tarifas API",
    "uiversion": 3
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "TravelHub Tarifas API",
        "description": "Documentación de endpoints de tarifas",
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

# Inicializar Swagger
swagger = Swagger(app, template=swagger_template, config=swagger_config)

# Inicializar base de datos
db.init_app(app)

# Habilitar CORS
CORS(app)

# Crear API
api = Api(app)

# Rutas de la API
api.add_resource(Health, '/health')
api.add_resource(TarifaListResource, '/tarifas')
api.add_resource(TarifaResource, '/tarifas/<tarifa_id>')
api.add_resource(DescuentoListResource, '/descuentos')
api.add_resource(DescuentoResource, '/descuentos/<descuento_id>')
api.add_resource(SeedDB, '/seed')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=3008)
