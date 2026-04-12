from app.api.api import (
    ListadoCiudades,
    ListadoPaises,
    CountryList,
    PopularCitiesByCountry,
    InventarioHealth,
    FiltroHabitaciones,
    buscarHotel,
    HabitacionesporId,
    SeedDB,
    HospedajeCollection,
    HospedajeById,
    SeedReservations,
)
from app.errors.handlers import ErrorHandler
from app.errors.exceptions import BadRequestError, DatababaseError
from app.utils.helper import InventarioHelper
from app.utils import seedHelper as seed_module
from app.db.models import db
from flask_restful import Api
from flask import Flask
import pytest
from types import SimpleNamespace
from uuid import uuid4


def build_app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    ErrorHandler.errors(app)
    db.init_app(app)
    api = Api(app)
    return app, api

def test_listado_ciudades(mocker):
    #Creamos app
    app, api = build_app()
    api.add_resource(ListadoCiudades, '/ciudades')
    client = app.test_client()

    #Mockeamos la respuesta del CRUD
    ciudades = [
        {'ciudad': 'Barranquilla', 'pais': 'Colombia'},
        {'ciudad': 'Cartagena', 'pais': 'Colombia'},
        {'ciudad': 'Medellín', 'pais': 'Colombia'},
    ]
    mocker.patch('app.services.inventario_crud.InventarioCRUD.listadoCiudades', return_value = ciudades)

    #Hacemos peticion GET
    response = client.get('/ciudades')

    assert response.status_code == 200
    assert response.get_json() == ciudades
    assert len(response.get_json()) == len(ciudades)
    assert {'ciudad': 'Barranquilla', 'pais': 'Colombia'} in response.get_json()

def test_listado_paises(mocker):
    #Creamos app
    app, api = build_app()
    api.add_resource(ListadoPaises, '/paises')
    client = app.test_client()

    #Mockeamos la respuesta del CRUD
    paises = ['Colombia', 'Argentina', 'Peru']
    mocker.patch('app.services.inventario_crud.InventarioCRUD.listadoPaises', return_value = paises)

    #Hacemos peticion GET
    response = client.get('/paises')

    assert response.status_code == 200
    assert response.get_json() == paises
    assert len(response.get_json()) == len(paises)
    assert 'Colombia' in response.get_json()


def test_country_list(mocker):
    app, api = build_app()
    api.add_resource(CountryList, '/paises')
    client = app.test_client()

    #Mockeamos la respuesta del CRUD
    paises = ['Colombia', 'Argentina', 'Peru']
    mocker.patch('app.services.inventario_crud.CountriesCRUD.obtener_paises', return_value = paises)
    #Hacemos peticion GET
    response = client.get('/paises')

    assert response.status_code == 200
    assert response.get_json() == paises

def test_popular_cities_by_country(mocker):
    app, api = build_app()
    api.add_resource(PopularCitiesByCountry, '/countries/<code>/popular-cities')
    client = app.test_client()

    #Mockeamos la respuesta del CRUD
    ciudades = ['Bogotá', 'Medellín', 'Cartagena']
    mocker.patch('app.services.inventario_crud.CountriesCRUD.obtener_ciudades_por_codigo', return_value = ciudades)

    #Hacemos peticion GET
    response = client.get('/countries/CO/popular-cities') 
    response_without_code = client.get('/countries/popular-cities')


    assert response.status_code == 200
    assert response.get_json() == ciudades
    assert response_without_code.status_code == 404


def test_inventario_health():
    app, api = build_app()
    api.add_resource(InventarioHealth, '/health')
    client = app.test_client()

    response = client.get('/health')

    assert response.status_code == 200
    assert response.get_json() == {'status': 'healthy'}


def test_popular_cities_by_country_empty_list(mocker):
    app, api = build_app()
    api.add_resource(PopularCitiesByCountry, '/countries/<code>/popular-cities')
    client = app.test_client()

    mocker.patch('app.api.api.countries_CRUD.obtener_ciudades_por_codigo', return_value=[])

    response = client.get('/countries/CO/popular-cities')

    assert response.status_code == 400
    assert response.get_json() == {'msg': 'No hay ciudades registradas para el código de país CO'}


def test_popular_cities_by_country_db_error(mocker):
    app, api = build_app()
    api.add_resource(PopularCitiesByCountry, '/countries/<code>/popular-cities')
    client = app.test_client()

    mocker.patch(
        'app.api.api.countries_CRUD.obtener_ciudades_por_codigo',
        return_value=DatababaseError('Error en la base de datos: fallo simulado')
    )

    response = client.get('/countries/CO/popular-cities')

    assert response.status_code == 500
    assert response.get_json() == {'msg': 'Error en la base de datos: fallo simulado'}


def test_filtro_habitaciones_ok(mocker):
    app, api = build_app()
    api.add_resource(FiltroHabitaciones, '/filtro')
    client = app.test_client()

    expected = [{'id': '1', 'nombre': 'Habitación 1'}]
    mocker.patch('app.api.api.InventarioHelper.validacionCampoCiudad', return_value='Bogota')
    mocker.patch('app.api.api.InventarioHelper.validacionCampoCapacidad', return_value=2)
    mocker.patch('app.api.api.inventario_CRUD.habitacionesDisponibles', return_value=expected)

    response = client.get('/filtro?ciudad=bogota&capacidad=2&currency_code=COP')

    assert response.status_code == 200
    assert response.get_json() == expected


def test_buscar_hotel_ok_and_not_found(mocker):
    app, api = build_app()
    api.add_resource(buscarHotel, '/hotel')
    client = app.test_client()

    hotel = SimpleNamespace(
        id=uuid4(),
        nombre='Hotel Andino',
        pais='Colombia',
        ciudad='Bogota',
        direccion='Calle 1',
        rating=4.7,
    )
    mocker.patch('app.api.api.inventario_CRUD.buscarHotelByName', return_value=hotel, create=True)

    response = client.get('/hotel?nombre=Hotel Andino')

    assert response.status_code == 200
    assert response.get_json()['nombre'] == 'Hotel Andino'
    assert response.get_json()['pais'] == 'Colombia'

    mocker.patch('app.api.api.inventario_CRUD.buscarHotelByName', return_value=None, create=True)
    not_found = client.get('/hotel?nombre=NoExiste')

    assert not_found.status_code == 404
    assert not_found.get_json() == {'msg': 'Hotel no encontrado'}


def test_habitaciones_por_id_ok_and_empty(mocker):
    app, api = build_app()
    api.add_resource(HabitacionesporId, '/habitaciones')
    client = app.test_client()

    room = SimpleNamespace(
        id=uuid4(),
        precio=250000,
        capacidad=2,
        descripcion='Habitación doble',
    )
    mocker.patch('app.api.api.inventario_CRUD.habitacionesporIdHotel', return_value=[room], create=True)

    response = client.get('/habitaciones?id=hotel-1')

    assert response.status_code == 200
    assert response.get_json() == [{
        'habitacion_id': str(room.id),
        'precio': 250000,
        'capacidad': 2,
        'descripcion': 'Habitación doble',
    }]

    mocker.patch('app.api.api.inventario_CRUD.habitacionesporIdHotel', return_value=None, create=True)
    empty_response = client.get('/habitaciones?id=hotel-2')

    assert empty_response.status_code == 200
    assert empty_response.get_json() == []


def test_seed_db_success_and_error(mocker):
    app, api = build_app()
    api.add_resource(SeedDB, '/seed')
    client = app.test_client()

    mocker.patch(
        'app.api.api.SeedHelper.reset_and_seed',
        return_value={
            'ok': True,
            'countries_insertados': 2,
            'hospedajes_insertados': 3,
            'habitaciones_insertadas': 4,
        },
    )

    response = client.post('/seed')

    assert response.status_code == 200
    assert response.get_json() == {
        'msg': 'Seed ejecutado correctamente',
        'countries_insertados': 2,
        'hospedajes_insertados': 3,
        'habitaciones_insertadas': 4,
    }

    mocker.patch(
        'app.api.api.SeedHelper.reset_and_seed',
        return_value={'ok': False, 'error': 'fallo seed'},
    )

    error_response = client.post('/seed')

    assert error_response.status_code == 500
    assert error_response.get_json() == {
        'msg': 'Error al ejecutar el seed',
        'error': 'fallo seed',
    }


def test_hospedaje_collection_validation_and_db_error(mocker):
    app, api = build_app()
    api.add_resource(HospedajeCollection, '/hospedajes')
    with app.test_request_context('/hospedajes', method='POST', json={'nombre': 'Hotel'}):
        with pytest.raises(BadRequestError) as error:
            HospedajeCollection().post()
        assert 'Faltan campos requeridos' in str(error.value)

    with app.test_request_context(
        '/hospedajes',
        method='POST',
        json={
            'nombre': 'Hotel',
            'descripcion': 'Desc',
            'countryCode': 'CO',
            'pais': 'Colombia',
            'ciudad': 'Bogota',
            'direccion': 'Calle 1',
            'latitude': 'abc',
            'longitude': -74.0,
            'rating': 4.5,
            'reviews': 10,
        },
    ):
        with pytest.raises(BadRequestError) as error:
            HospedajeCollection().post()
        assert 'deben ser numéricos válidos' in str(error.value)

    mocker.patch('app.api.api.inventario_CRUD.crear_hospedaje', return_value=DatababaseError('Error en la base de datos: fallo simulado'))
    valid_payload = {
        'nombre': 'Hotel',
        'descripcion': 'Desc',
        'countryCode': 'CO',
        'pais': 'Colombia',
        'ciudad': 'Bogota',
        'direccion': 'Calle 1',
        'latitude': 4.7,
        'longitude': -74.0,
        'rating': 4.5,
        'reviews': 10,
    }
    with app.test_request_context('/hospedajes', method='POST', json=valid_payload):
        db_error = HospedajeCollection().post()

    assert db_error == ({'msg': 'Error en la base de datos: fallo simulado'}, 500)


def test_hospedaje_collection_success(mocker):
    app, api = build_app()
    api.add_resource(HospedajeCollection, '/hospedajes')

    created = {'id': '1', 'nombre': 'Hotel', 'descripcion': 'Desc'}
    mocker.patch('app.api.api.inventario_CRUD.crear_hospedaje', return_value=created)

    with app.test_request_context(
        '/hospedajes',
        method='POST',
        json={
            'nombre': 'Hotel',
            'descripcion': 'Desc',
            'countryCode': 'co',
            'pais': 'Colombia',
            'ciudad': 'Bogota',
            'direccion': 'Calle 1',
            'latitude': 4.7,
            'longitude': -74.0,
            'rating': 4.5,
            'reviews': 10,
        },
    ):
        response = HospedajeCollection().post()

    assert response == (created, 201)


def test_hospedaje_by_id_variants(mocker):
    app, api = build_app()
    api.add_resource(HospedajeById, '/hospedajes/<string:hospedaje_id>/<string:currency_code>')

    mocker.patch('app.api.api.inventario_CRUD.obtener_hospedaje_por_id', return_value=DatababaseError('uuid inválido'))
    invalid = HospedajeById().get('abc', 'COP')
    assert invalid == ({'msg': 'uuid inválido'}, 400)

    mocker.patch('app.api.api.inventario_CRUD.obtener_hospedaje_por_id', return_value=DatababaseError('fallo db'))
    server_error = HospedajeById().get('abc', 'COP')
    assert server_error == ({'msg': 'fallo db'}, 500)

    mocker.patch('app.api.api.inventario_CRUD.obtener_hospedaje_por_id', return_value=None)
    not_found = HospedajeById().get('abc', 'COP')
    assert not_found == ({'msg': 'Hospedaje no encontrado para id abc'}, 404)

    hospedaje = {
        'id': '1',
        'nombre': 'Hotel',
        'pais': 'Colombia',
        'ciudad': 'Bogota',
    }
    mocker.patch('app.api.api.inventario_CRUD.obtener_hospedaje_por_id', return_value=hospedaje)
    ok = HospedajeById().get('123e4567-e89b-12d3-a456-426614174000', 'COP')
    assert ok == (hospedaje, 200)


def test_inventario_helper_validations():
    assert InventarioHelper.validacionCampoCiudad('Bogota') == 'Bogota'
    with pytest.raises(BadRequestError):
        InventarioHelper.validacionCampoCiudad('')
    with pytest.raises(BadRequestError):
        InventarioHelper.validacionCampoCiudad('123')

    assert InventarioHelper.validacionCampoCapacidad('2') == 2
    with pytest.raises(BadRequestError):
        InventarioHelper.validacionCampoCapacidad('')
    with pytest.raises(BadRequestError):
        InventarioHelper.validacionCampoCapacidad('abc')
    with pytest.raises(BadRequestError):
        InventarioHelper.validacionCampoCapacidad('0')


def test_inventario_helper_currency_conversion():
    assert InventarioHelper.convertirMoneda(100, 'COP', 'COP') == 100
    assert InventarioHelper.convertirMoneda(100, 'USD', 'COP') == 400000.0 or InventarioHelper.convertirMoneda(100, 'USD', 'COP') == 400000
    with pytest.raises(ValueError):
        InventarioHelper.convertirMoneda(100, 'XXX', 'COP')

    habitaciones = [
        {'precio': 100, 'currency_code': 'USD'},
        {'precio': 4000, 'currency_code': 'COP'},
    ]
    converted = InventarioHelper.convertirPrecios(habitaciones, 'COP')
    assert converted[0]['precio'] == 400000.0 or converted[0]['precio'] == 400000
    assert converted[1]['precio'] == 4000


def test_seed_helper_pure_functions():
    assert seed_module._normalize_city(None) == ''
    assert seed_module._normalize_city('Bogotá') == 'bogota'
    assert seed_module._resolve_description({'ciudad': 'Lima'}) == 'Hospedaje en Lima'
    assert seed_module._resolve_description({'descripcion': 'Hermoso'}) == 'Hermoso'
    assert seed_module._resolve_coordinates({'latitude': 1, 'longitude': 2}) == (1.0, 2.0)
    assert seed_module._resolve_coordinates({'ciudad': 'Bogotá'}) == seed_module.CITY_COORDINATES['bogota']


def test_seed_helper_loaders(monkeypatch):
    monkeypatch.setattr(seed_module, '_load_json_file', lambda name: {'countries': [{'countryCode': code} for code in {country['code'] for country in seed_module.COUNTRIES_SEED}]})
    catalog = seed_module._load_hospedajes_catalog()
    assert 'countries' in catalog

    monkeypatch.setattr(seed_module, '_load_json_file', lambda name: [{'id': '1'}])
    monkeypatch.setattr(seed_module, '_load_hospedajes_catalog', lambda: {'countries': [{'sources': [{'file': 'a.json'}]}]})
    assert seed_module._load_hospedajes_seed() == [{'id': '1'}]


def test_seed_helper_reset_and_seed(monkeypatch):
    class FakeTable:
        @staticmethod
        def create(bind=None, checkfirst=None):
            return None

    class FakeQuery:
        @staticmethod
        def delete():
            return None

        @staticmethod
        def all():
            return [SimpleNamespace(id=uuid4())]

    class FakeModel:
        query = FakeQuery()
        __table__ = FakeTable()

        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
            if not hasattr(self, 'created_at'):
                self.created_at = SimpleNamespace(isoformat=lambda: '2026-04-01T00:00:00')
            if not hasattr(self, 'updated_at'):
                self.updated_at = SimpleNamespace(isoformat=lambda: '2026-04-02T00:00:00')

    monkeypatch.setattr(seed_module, 'CountryORM', FakeModel)
    monkeypatch.setattr(seed_module, 'AmenidadORM', FakeModel)
    monkeypatch.setattr(seed_module, 'HospedajeORM', FakeModel)
    monkeypatch.setattr(seed_module, 'HabitacionORM', FakeModel)
    monkeypatch.setattr(seed_module, 'Hospedaje_ImagenORM', FakeModel)
    monkeypatch.setattr(seed_module, 'HOSPEDAJES_SEED', [
        {
            'id': str(uuid4()),
            'nombre': 'Hotel Uno',
            'countryCode': 'CO',
            'pais': 'Colombia',
            'ciudad': 'Bogota',
            'direccion': 'Calle 1',
            'rating': 4.5,
            'reviews': 10,
            'habitaciones': [
                {'code': '101', 'descripcion': 'Habitación', 'capacidad': 2, 'precio': 100},
            ],
            'imagenes': [
                {'id': str(uuid4()), 'url': 'https://example.com/img.png'},
            ],
        }
    ])
    monkeypatch.setattr(seed_module.random, 'randint', lambda a, b: 3)
    monkeypatch.setattr(seed_module.random, 'sample', lambda seq, k: list(seq)[:k])
    class FakeSeedSession:
        def add(self, obj):
            return None

        def flush(self):
            return None

        def commit(self):
            return None

        def rollback(self):
            return None

        def execute(self, *args, **kwargs):
            return []

        def remove(self):
            return None

    monkeypatch.setattr(seed_module.db, 'session', FakeSeedSession())
    monkeypatch.setattr(seed_module.SeedHelper, '_ensure_habitaciones_code_column', lambda: None)
    monkeypatch.setattr(seed_module.SeedHelper, '_ensure_hospedajes_country_code_column', lambda: None)
    monkeypatch.setattr(seed_module.SeedHelper, '_ensure_hospedajes_extended_columns', lambda: None)

    with build_app()[0].app_context():
        result = seed_module.SeedHelper.reset_and_seed()

    assert isinstance(result, dict)
    assert 'ok' in result


def test_seed_reservations(mocker):
    app, api = build_app()
    api.add_resource(SeedReservations, '/seed-reservas')

    mocker.patch('app.api.api.SeedHelper.seed_reservations', return_value={'habitacion_ids': ['1', '2']})

    result = SeedReservations().get()

    assert result == ({'habitacion_ids': ['1', '2']}, 200)


def test_inventario_crud_paises_ciudades_and_errors(monkeypatch):
    from app.services.inventario_crud import InventarioCRUD
    from app.services import inventario_crud as crud_module

    crud = InventarioCRUD()

    class FakeSession:
        def __init__(self):
            self.deleted = []

        def query(self, *args):
            self.args = args
            return self

        def distinct(self):
            return self

        def all(self):
            if len(self.args) == 1:
                return [('Colombia',), ('Peru',)]
            return [('Bogota', 'Colombia'), ('Lima', 'Peru')]

        def filter(self, *args, **kwargs):
            return self

        def order_by(self, *args, **kwargs):
            return self

        def first(self):
            return None

        def rollback(self):
            return None

        def remove(self):
            return None

    fake_session = FakeSession()
    monkeypatch.setattr(crud_module.db, 'session', fake_session)
    crud.db = fake_session

    with build_app()[0].app_context():
        assert crud.listadoPaises() == ['Colombia', 'Peru']
        assert crud.listadoCiudades() == [
            {'ciudad': 'Bogota', 'pais': 'Colombia'},
            {'ciudad': 'Lima', 'pais': 'Peru'},
        ]

        def boom(*args, **kwargs):
            raise Exception('boom')

        monkeypatch.setattr(fake_session, 'all', boom)
        with pytest.raises(DatababaseError):
            crud.listadoPaises()
        with pytest.raises(DatababaseError):
            crud.listadoCiudades()


def test_inventario_crud_hospedajes_and_detail(monkeypatch):
    from app.services.inventario_crud import InventarioCRUD
    from app.services import inventario_crud as crud_module

    crud = InventarioCRUD()

    fake_hospedaje = SimpleNamespace(
        id=uuid4(),
        nombre='Hotel Uno',
        descripcion='Desc',
        countryCode='CO',
        pais='Colombia',
        ciudad='Bogota',
        direccion='Calle 1',
        latitude=1.2,
        longitude=2.3,
        rating=4.5,
        reviews=10,
        created_at=SimpleNamespace(isoformat=lambda: '2026-04-01T00:00:00'),
        updated_at=SimpleNamespace(isoformat=lambda: '2026-04-02T00:00:00'),
        habitaciones=[],
        amenidades=[],
        imagenes=[],
    )

    class FakeQuery:
        def __init__(self, result=None, raise_on_all=False):
            self.result = result
            self.raise_on_all = raise_on_all

        def filter(self, *args, **kwargs):
            return self

        def order_by(self, *args, **kwargs):
            return self

        def all(self):
            if self.raise_on_all:
                raise Exception('boom')
            return self.result

        def first(self):
            return self.result

    class FakeSession:
        def __init__(self):
            self.added = []
            self.committed = 0
            self.rolled_back = 0

        def add(self, obj):
            self.added.append(obj)

        def commit(self):
            self.committed += 1

        def rollback(self):
            self.rolled_back += 1

        def remove(self):
            return None

        def remove(self):
            return None

        def remove(self):
            return None

        def query(self, *args):
            return FakeQuery(result=fake_hospedaje)

    fake_session = FakeSession()
    monkeypatch.setattr(crud_module.db, 'session', fake_session)
    crud.db = fake_session

    with build_app()[0].app_context():
        created = crud.crear_hospedaje({
            'nombre': 'Hotel Uno',
            'descripcion': 'Desc',
            'countryCode': 'CO',
            'pais': 'Colombia',
            'ciudad': 'Bogota',
            'direccion': 'Calle 1',
            'latitude': 1.2,
            'longitude': 2.3,
            'rating': 4.5,
            'reviews': 10,
        })
        assert created['nombre'] == 'Hotel Uno'
        assert fake_session.committed == 1

        monkeypatch.setattr(
            crud_module.db.session,
            'query',
            lambda *args: (
                FakeQuery(result=SimpleNamespace(CurrencyCode='COP'))
                if args and args[0] is crud_module.CountryORM
                else FakeQuery(result=fake_hospedaje)
            ),
        )
        hospedaje = crud.obtener_hospedaje_por_id(str(uuid4()), 'COP')
        assert hospedaje['nombre'] == 'Hotel Uno'

        assert crud.obtener_hospedaje_por_id('no-es-uuid', 'COP').message == 'El id del hospedaje no tiene un formato UUID válido'

        monkeypatch.setattr(
            crud_module.db.session,
            'query',
            lambda *args: FakeQuery(result=[fake_hospedaje], raise_on_all=True),
        )
        assert isinstance(crud.obtener_hospedajes(), DatababaseError)


def test_inventario_crud_habitaciones_and_countries(monkeypatch):
    from app.services.inventario_crud import InventarioCRUD, CountriesCRUD
    from app.services import inventario_crud as crud_module

    class Row(SimpleNamespace):
        pass

    room = Row(
        habitacion_id=uuid4(),
        code='101',
        precio=100,
        capacidad=2,
        descripcion='Desc',
        hospedaje_id=uuid4(),
        nombre='Hotel',
        pais='Colombia',
        ciudad='Bogota',
        direccion='Calle 1',
        rating=4.5,
        reviews=10,
        currency_code='USD',
        image_url='url',
    )
    country = Row(
        id=uuid4(),
        name='Colombia',
        code='CO',
        CurrencyCode='COP',
        CurrencySymbol='$',
        FlagEmoji='🇨🇴',
        PhoneCode='+57',
    )

    class FakeQuery:
        def __init__(self, result=None, raise_on_all=False, raise_on_first=False):
            self.result = result
            self.raise_on_all = raise_on_all
            self.raise_on_first = raise_on_first

        def join(self, *args, **kwargs):
            return self

        def filter(self, *args, **kwargs):
            return self

        def filter_by(self, **kwargs):
            return self

        def group_by(self, *args, **kwargs):
            return self

        def order_by(self, *args, **kwargs):
            return self

        def all(self):
            if self.raise_on_all:
                raise Exception('boom')
            return self.result

        def first(self):
            if self.raise_on_first:
                raise Exception('boom')
            return self.result

        def get(self, _id):
            return self.result

    class FakeSession:
        def __init__(self):
            self.committed = 0
            self.rolled_back = 0

        def add(self, obj):
            return None

        def commit(self):
            self.committed += 1

        def rollback(self):
            self.rolled_back += 1

        def remove(self):
            return None

        def query(self, *args):
            return FakeQuery(result=[room])

    fake_session = FakeSession()
    monkeypatch.setattr(crud_module.db, 'session', fake_session)

    hotel_detail = SimpleNamespace(
        id=uuid4(),
        nombre='Hotel',
        descripcion='Desc',
        countryCode='CO',
        pais='Colombia',
        ciudad='Bogota',
        direccion='Calle 1',
        latitude=1.0,
        longitude=2.0,
        rating=4.5,
        reviews=10,
        created_at=SimpleNamespace(isoformat=lambda: '2026-04-01T00:00:00'),
        updated_at=SimpleNamespace(isoformat=lambda: '2026-04-02T00:00:00'),
        habitaciones=[room],
        amenidades=[SimpleNamespace(id=uuid4(), name='WiFi', icon='wifi')],
        imagenes=[SimpleNamespace(id=uuid4(), url='url')],
    )

    monkeypatch.setattr('app.services.inventario_crud.InventarioHelper.convertirPrecios', lambda habitaciones, destino: habitaciones)

    crud = InventarioCRUD()
    countries_crud = CountriesCRUD()

    with build_app()[0].app_context():
        monkeypatch.setattr(
            crud_module.db.session,
            'query',
            lambda *args: FakeQuery(result=[SimpleNamespace(
                habitacion_id=room.habitacion_id,
                code=room.code,
                precio=room.precio,
                capacidad=room.capacidad,
                descripcion=room.descripcion,
                hospedaje_id=room.hospedaje_id,
                nombre=room.nombre,
                pais=room.pais,
                ciudad=room.ciudad,
                direccion=room.direccion,
                rating=room.rating,
                reviews=room.reviews,
                currency_code=room.currency_code,
                image_url=room.image_url,
            )]),
        )
        habitaciones = crud.habitacionesDisponibles('Bogota', 2, 'COP')
        assert habitaciones[0]['nombre'] == 'Hotel'

        monkeypatch.setattr(crud_module.db.session, 'query', lambda *args: FakeQuery(result=[room], raise_on_all=True))
        with pytest.raises(DatababaseError):
            crud.habitacionesDisponibles('Bogota', 2, 'COP')

        monkeypatch.setattr(
            crud_module.db.session,
            'query',
            lambda *args: FakeQuery(result=[country]),
        )
        assert countries_crud.obtener_paises()[0]['name'] == 'Colombia'

        monkeypatch.setattr(
            crud_module.db.session,
            'query',
            lambda *args: FakeQuery(result=[SimpleNamespace(ciudad='Bogota')]),
        )
        assert countries_crud.obtener_ciudades_por_codigo('CO') == ['Bogota']

        monkeypatch.setattr(
            crud_module.db.session,
            'query',
            lambda *args: FakeQuery(result=hotel_detail),
        )
        assert crud.buscarHotelByName('Hotel').nombre == 'Hotel'

        monkeypatch.setattr(
            crud_module.db.session,
            'query',
            lambda *args: FakeQuery(result=[room]),
        )
        assert crud.habitacionesporIdHotel('hotel-id') == [room]


def test_seed_helper_error_branches(monkeypatch):
    monkeypatch.setattr(seed_module, '_data_file_path', lambda file_name: 'missing.json')
    with pytest.raises(FileNotFoundError):
        seed_module._load_json_file('missing.json')

    monkeypatch.setattr(seed_module, '_load_json_file', lambda file_name: {'bad': []})
    with pytest.raises(ValueError):
        seed_module._load_hospedajes_catalog()

    monkeypatch.setattr(seed_module, '_load_json_file', lambda file_name: {'countries': [{'countryCode': 'XX'}]})
    with pytest.raises(ValueError):
        seed_module._load_hospedajes_catalog()
