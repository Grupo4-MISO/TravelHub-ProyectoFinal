import pytest
from app.db.models import db, Tarifa, TarifaStatus
import sys
import os
from datetime import datetime, timedelta

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
    def test_get_empty_tarifas(self, client, app_context):
        """Prueba obtener lista vacía de tarifas"""
        response = client.get('/tarifas')
        assert response.status_code == 200
        assert response.get_json() == []

    def test_create_tarifa(self, client, app_context):
        """Prueba crear nueva tarifa"""
        now = datetime.utcnow()
        data = {
            'nombre': 'Tarifa Test',
            'valor_noche': 50.0,
            'moneda': 'COP',
            'categoria_habitacion': 'DOBLE',
            'descripcion': 'Tarifa para pruebas',
            'vigencia_inicio': (now - timedelta(days=1)).isoformat(),
            'vigencia_fin': (now + timedelta(days=10)).isoformat(),
        }
        response = client.post('/tarifas', json=data)
        assert response.status_code == 201
        json_data = response.get_json()
        assert json_data['nombre'] == 'Tarifa Test'
        assert json_data['valor_noche'] == 50.0
        assert json_data['moneda'] == 'COP'
        assert json_data['categoria_habitacion'] == 'DOBLE'
        assert json_data['vigente'] is True

    def test_create_tarifa_missing_required_field(self, client, app_context):
        """Prueba crear tarifa sin campo requerido"""
        data = {
            'descripcion': 'Sin campos requeridos'
        }
        response = client.post('/tarifas', json=data)
        assert response.status_code == 400

    def test_filter_tarifas_vigentes(self, client, app_context):
        now = datetime.utcnow()
        vigente = Tarifa(
            nombre='Tarifa Vigente',
            valor_noche=120,
            moneda='COP',
            categoria_habitacion='SUITE',
            vigencia_inicio=now - timedelta(days=2),
            vigencia_fin=now + timedelta(days=2),
            estado=TarifaStatus.Active,
        )
        no_vigente = Tarifa(
            nombre='Tarifa Vencida',
            valor_noche=90,
            moneda='USD',
            categoria_habitacion='SENCILLA',
            vigencia_inicio=now - timedelta(days=20),
            vigencia_fin=now - timedelta(days=10),
            estado=TarifaStatus.Active,
        )
        db.session.add(vigente)
        db.session.add(no_vigente)
        db.session.commit()

        response_vigentes = client.get('/tarifas?vigentes=true')
        assert response_vigentes.status_code == 200
        data_vigentes = response_vigentes.get_json()
        assert len(data_vigentes) == 1
        assert data_vigentes[0]['nombre'] == 'Tarifa Vigente'

        response_no_vigentes = client.get('/tarifas?vigentes=false')
        assert response_no_vigentes.status_code == 200
        data_no_vigentes = response_no_vigentes.get_json()
        assert len(data_no_vigentes) == 1
        assert data_no_vigentes[0]['nombre'] == 'Tarifa Vencida'

    def test_filter_tarifas_invalid_vigentes_param(self, client, app_context):
        response = client.get('/tarifas?vigentes=talvez')
        assert response.status_code == 400


class TestTarifaResource:
    def test_get_nonexistent_tarifa(self, client, app_context):
        """Prueba obtener tarifa inexistente"""
        response = client.get('/tarifas/00000000-0000-0000-0000-000000000000')
        assert response.status_code == 404


class TestSeedDB:
    def test_seed_db(self, client, app_context):
        """Prueba poblar base de datos"""
        response = client.post('/seed')
        assert response.status_code == 200
        
        # Verificar que se crearon los datos
        response = client.get('/tarifas')
        assert len(response.get_json()) > 0
