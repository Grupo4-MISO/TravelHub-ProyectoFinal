from app.api.api import Search
from flask_restful import Api
from flask import Flask
import pytest

@pytest.fixture
def app():
    #Creamos una aplicacion de Flask para pruebas
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(Search, "/search")

    return app.test_client()

def test_search_