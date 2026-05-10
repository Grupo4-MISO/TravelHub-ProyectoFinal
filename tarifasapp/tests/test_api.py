import pytest
import jwt
from app.db.models import db, Tarifa, TarifaStatus, Descuento
import sys
import os
from datetime import datetime, timedelta
from uuid import UUID

sys.path.append(os.path.abspath(os.path.dirname(__file__)))


@pytest.fixture
def app():
    """Crear instancia de la aplicación para testing"""
    from main import app
    
    # Configurar para pruebas
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Crear cliente de prueba"""
    return app.test_client()


@pytest.fixture
def auth_headers(app):
    payload = {
        'sub': 'HTL-99281',
        'username': 'Hotel Las Colinas Manizales',
        'role': 'Accomodation',
        'exp': int((datetime.utcnow() + timedelta(hours=1)).timestamp()),
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def app_context(app):
    """Proporcionar contexto de aplicación"""
    with app.app_context():
        yield app


class TestHealth:
    def test_health_check(self, client):
        """Prueba del endpoint de salud"""
        response = client.get('/health')
        assert response.status_code == 200
        assert response.get_json()['status'] == 'healthy'


class TestTarifaList:
    def test_get_empty_tarifas(self, client, app_context, auth_headers):
        """Prueba obtener lista vacía de tarifas"""
        response = client.get('/tarifas', headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json() == []

    def test_create_tarifa(self, client, app_context, auth_headers):
        """Prueba crear nueva tarifa"""
        now = datetime.utcnow()
        data = {
            'nombre': 'Tarifa Test',
            'valor_base': 50.0,
            'moneda': 'COP',
            'categoria_habitacion': 'DOBLE',
            'descripcion': 'Tarifa para pruebas',
            'vigencia_inicio': (now - timedelta(days=1)).isoformat(),
            'vigencia_fin': (now + timedelta(days=10)).isoformat(),
        }
        response = client.post('/tarifas', json=data, headers=auth_headers)
        assert response.status_code == 201
        json_data = response.get_json()
        assert json_data['nombre'] == 'Tarifa Test'
        assert json_data['hotel_id'] == 'HTL-99281'
        assert json_data['valor_base'] == 50.0
        assert json_data['moneda'] == 'COP'
        assert json_data['categoria_habitacion'] == 'DOBLE'
        assert json_data['vigente'] is True

    def test_create_tarifa_missing_required_field(self, client, app_context, auth_headers):
        """Prueba crear tarifa sin campo requerido"""
        data = {
            'descripcion': 'Sin campos requeridos'
        }
        response = client.post('/tarifas', json=data, headers=auth_headers)
        assert response.status_code == 400

    def test_filter_tarifas_vigentes(self, client, app_context, auth_headers):
        now = datetime.utcnow()
        vigente = Tarifa(
            nombre='Tarifa Vigente',
            hotel_id='HTL-99281',
            valor_base=120,
            moneda='COP',
            categoria_habitacion='SUITE',
            vigencia_inicio=now - timedelta(days=2),
            vigencia_fin=now + timedelta(days=2),
            estado=TarifaStatus.Active,
        )
        no_vigente = Tarifa(
            nombre='Tarifa Vencida',
            hotel_id='HTL-99281',
            valor_base=90,
            moneda='USD',
            categoria_habitacion='SENCILLA',
            vigencia_inicio=now - timedelta(days=20),
            vigencia_fin=now - timedelta(days=10),
            estado=TarifaStatus.Active,
        )
        db.session.add(vigente)
        db.session.add(no_vigente)
        db.session.commit()

        response_vigentes = client.get('/tarifas?vigentes=true', headers=auth_headers)
        assert response_vigentes.status_code == 200
        data_vigentes = response_vigentes.get_json()
        assert len(data_vigentes) == 1
        assert data_vigentes[0]['nombre'] == 'Tarifa Vigente'

        response_no_vigentes = client.get('/tarifas?vigentes=false', headers=auth_headers)
        assert response_no_vigentes.status_code == 200
        data_no_vigentes = response_no_vigentes.get_json()
        assert len(data_no_vigentes) == 1
        assert data_no_vigentes[0]['nombre'] == 'Tarifa Vencida'

    def test_filter_tarifas_invalid_vigentes_param(self, client, app_context, auth_headers):
        response = client.get('/tarifas?vigentes=talvez', headers=auth_headers)
        assert response.status_code == 400


class TestTarifaResource:
    def test_get_nonexistent_tarifa(self, client, app_context, auth_headers):
        """Prueba obtener tarifa inexistente"""
        response = client.get('/tarifas/00000000-0000-0000-0000-000000000000', headers=auth_headers)
        assert response.status_code == 404

    def test_get_tarifa_includes_active_discounts(self, client, app_context, auth_headers):
        now = datetime.utcnow()
        tarifa_response = client.post('/tarifas', json={
            'nombre': 'Tarifa con descuentos',
            'valor_base': 250.0,
            'moneda': 'USD',
            'categoria_habitacion': 'SUITE',
            'vigencia_inicio': (now - timedelta(days=1)).isoformat(),
            'vigencia_fin': (now + timedelta(days=10)).isoformat(),
        }, headers=auth_headers)
        assert tarifa_response.status_code == 201
        tarifa_id = tarifa_response.get_json()['id']

        tarifa = Tarifa.query.filter_by(id=UUID(tarifa_id)).first()
        descuento_activo = Descuento(
            nombre='Descuento activo',
            tarifa_id=tarifa.id,
            porcentaje=12,
            activo=True,
            vigencia_inicio=now - timedelta(days=1),
            vigencia_fin=now + timedelta(days=5),
        )
        descuento_inactivo = Descuento(
            nombre='Descuento inactivo',
            tarifa_id=tarifa.id,
            porcentaje=20,
            activo=False,
            vigencia_inicio=now - timedelta(days=1),
            vigencia_fin=now + timedelta(days=5),
        )
        db.session.add_all([descuento_activo, descuento_inactivo])
        db.session.commit()

        response = client.get(f'/tarifas/{tarifa_id}', headers=auth_headers)
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'descuentos_activos' in json_data
        assert len(json_data['descuentos_activos']) == 1
        assert json_data['descuentos_activos'][0]['nombre'] == 'Descuento activo'
        assert json_data['descuentos_activos'][0]['porcentaje'] == 12
        assert json_data['descuentos_activos'][0]['valor_descuento_calculado'] == 30.0
        assert json_data['valor_descuento_total'] == 30.0
        assert json_data['valor_final'] == 220.0


class TestSeedDB:
    def test_seed_db(self, client, app_context, auth_headers):
        """Prueba poblar base de datos"""
        response = client.post('/seed', headers=auth_headers)
        assert response.status_code == 200
        
        # Verificar que se crearon los datos
        response = client.get('/tarifas', headers=auth_headers)
        assert len(response.get_json()) > 0


class TestDescuentos:
    def _create_tarifa(self, client, auth_headers):
        now = datetime.utcnow()
        response = client.post('/tarifas', json={
            'nombre': 'Tarifa base',
            'valor_base': 200.0,
            'moneda': 'USD',
            'categoria_habitacion': 'SENCILLA',
            'vigencia_inicio': (now - timedelta(days=1)).isoformat(),
            'vigencia_fin': (now + timedelta(days=10)).isoformat(),
        }, headers=auth_headers)
        assert response.status_code == 201
        return response.get_json()['id']

    def test_create_discount_and_filter(self, client, app_context, auth_headers):
        tarifa_id = self._create_tarifa(client, auth_headers)
        now = datetime.utcnow()

        create_response = client.post('/descuentos', json={
            'nombre': 'Promo verano',
            'tarifa_id': tarifa_id,
            'porcentaje': 15,
            'activo': True,
            'vigencia_inicio': (now - timedelta(days=1)).isoformat(),
            'vigencia_fin': (now + timedelta(days=5)).isoformat(),
        }, headers=auth_headers)
        assert create_response.status_code == 201
        descuento = create_response.get_json()
        assert descuento['porcentaje'] == 15
        assert descuento['tarifa_id'] == tarifa_id
        assert descuento['activo'] is True

        inactive_response = client.post('/descuentos', json={
            'nombre': 'Promo vieja',
            'tarifa_id': tarifa_id,
            'porcentaje': 10,
            'activo': False,
            'vigencia_inicio': (now - timedelta(days=1)).isoformat(),
            'vigencia_fin': (now + timedelta(days=5)).isoformat(),
        }, headers=auth_headers)
        assert inactive_response.status_code == 201

        active_list = client.get('/descuentos?activos=true', headers=auth_headers)
        assert active_list.status_code == 200
        assert len(active_list.get_json()) == 1
        assert active_list.get_json()[0]['nombre'] == 'Promo verano'

        tarifa_filter = client.get(f'/descuentos?tarifa_id={tarifa_id}', headers=auth_headers)
        assert tarifa_filter.status_code == 200
        assert len(tarifa_filter.get_json()) == 2

    def test_create_discount_rejects_percentage_over_100(self, client, app_context, auth_headers):
        tarifa_id = self._create_tarifa(client, auth_headers)
        now = datetime.utcnow()

        response = client.post('/descuentos', json={
            'nombre': 'Promo invalida',
            'tarifa_id': tarifa_id,
            'porcentaje': 101,
            'vigencia_inicio': (now - timedelta(days=1)).isoformat(),
            'vigencia_fin': (now + timedelta(days=10)).isoformat(),
        }, headers=auth_headers)

        assert response.status_code == 400
        assert response.get_json()['error'] == "El campo 'porcentaje' no puede ser mayor a 100"

    def test_create_discount_rejects_vigencia_outside_tarifa(self, client, app_context, auth_headers):
        tarifa_id = self._create_tarifa(client, auth_headers)
        now = datetime.utcnow()

        response = client.post('/descuentos', json={
            'nombre': 'Promo fuera de vigencia tarifa',
            'tarifa_id': tarifa_id,
            'porcentaje': 10,
            'vigencia_inicio': (now - timedelta(days=5)).isoformat(),
            'vigencia_fin': (now + timedelta(days=30)).isoformat(),
        }, headers=auth_headers)

        assert response.status_code == 400
        assert response.get_json()['error'] == 'La vigencia del descuento debe estar dentro de la vigencia de la tarifa'

    def test_update_get_and_delete_discount(self, client, app_context, auth_headers):
        tarifa_id = self._create_tarifa(client, auth_headers)
        now = datetime.utcnow()
        create_response = client.post('/descuentos', json={
            'nombre': 'Promo update',
            'tarifa_id': tarifa_id,
            'porcentaje': 5,
            'vigencia_inicio': (now - timedelta(days=1)).isoformat(),
            'vigencia_fin': (now + timedelta(days=5)).isoformat(),
        }, headers=auth_headers)
        descuento_id = create_response.get_json()['id']

        update_response = client.put(f'/descuentos/{descuento_id}', json={
            'porcentaje': 20,
            'activo': False,
        }, headers=auth_headers)
        assert update_response.status_code == 200
        assert update_response.get_json()['porcentaje'] == 20
        assert update_response.get_json()['activo'] is False

        get_response = client.get(f'/descuentos/{descuento_id}', headers=auth_headers)
        assert get_response.status_code == 200

        delete_response = client.delete(f'/descuentos/{descuento_id}', headers=auth_headers)
        assert delete_response.status_code == 200

        missing_response = client.get(f'/descuentos/{descuento_id}', headers=auth_headers)
        assert missing_response.status_code == 404

    def test_update_discount_rejects_percentage_over_100(self, client, app_context, auth_headers):
        tarifa_id = self._create_tarifa(client, auth_headers)
        now = datetime.utcnow()
        create_response = client.post('/descuentos', json={
            'nombre': 'Promo update invalida',
            'tarifa_id': tarifa_id,
            'porcentaje': 5,
            'vigencia_inicio': (now - timedelta(days=1)).isoformat(),
            'vigencia_fin': (now + timedelta(days=5)).isoformat(),
        }, headers=auth_headers)
        descuento_id = create_response.get_json()['id']

        update_response = client.put(f'/descuentos/{descuento_id}', json={
            'porcentaje': 101,
        }, headers=auth_headers)

        assert update_response.status_code == 400
        assert update_response.get_json()['error'] == "El campo 'porcentaje' no puede ser mayor a 100"

    def test_update_discount_rejects_vigencia_outside_tarifa(self, client, app_context, auth_headers):
        tarifa_id = self._create_tarifa(client, auth_headers)
        now = datetime.utcnow()
        create_response = client.post('/descuentos', json={
            'nombre': 'Promo vigencia update invalida',
            'tarifa_id': tarifa_id,
            'porcentaje': 5,
            'vigencia_inicio': (now - timedelta(days=1)).isoformat(),
            'vigencia_fin': (now + timedelta(days=5)).isoformat(),
        }, headers=auth_headers)
        descuento_id = create_response.get_json()['id']

        update_response = client.put(f'/descuentos/{descuento_id}', json={
            'vigencia_fin': (now + timedelta(days=30)).isoformat(),
        }, headers=auth_headers)

        assert update_response.status_code == 400
        assert update_response.get_json()['error'] == 'La vigencia del descuento debe estar dentro de la vigencia de la tarifa'
