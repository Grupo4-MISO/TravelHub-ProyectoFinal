import pytest
from flask import Flask
from flask_restful import Api
from app.api.api import TarifaReserva
from app.errors.exceptions import BadRequestError
from app.utils.helper import ReservaHelper

@pytest.fixture
def client():
    app = Flask(__name__)
    app.config["TESTING"] = True

    api = Api(app)
    api.add_resource(TarifaReserva, "/api/v1/reservas/tarifa")

    return app.test_client()

def test_calcular_tarifa_si_precio_no_es_numero():
    with pytest.raises(BadRequestError) as exc_info:
        ReservaHelper.validacionCampoPrecio("abc")

    assert str(exc_info.value) == "El campo de precio debe ser un número válido"

def test_calcular_tarifa_si_descuento_no_es_numero():
    with pytest.raises(BadRequestError) as exc_info:
        ReservaHelper.validacionCampoDescuento("abc")

    assert str(exc_info.value) == "El campo de descuento debe ser un número válido"

def test_calcular_tarifa_si_pais_no_valido():
    with pytest.raises(BadRequestError) as exc_info:
        ReservaHelper.validacionCampoPais("Argentina")

    assert str(exc_info.value) == "El campo de país debe ser uno de los siguientes: AR, CL, CO, EC, MX, PE"

def test_calcular_tarifa_valido(client):
    payload = {
        "check_in": "2026-07-01",
        "check_out": "2026-07-05",
        "precio": 100,
        "descuento": 0.1,
        "pais": "AR"
    }
    response = client.post("/api/v1/reservas/tarifa", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["tarifa_total"] == 435.60




