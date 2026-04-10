from sqlalchemy.dialects.postgresql import UUID
from flask_sqlalchemy import SQLAlchemy
import uuid

#Creamos base de datos con SQLAlchemy
db = SQLAlchemy()


class Hospedaje_ImagenORM(db.Model):
    __tablename__ = 'hospedajes_imagenes'

    id = db.Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
    hospedaje_id = db.Column(UUID(as_uuid = True), db.ForeignKey('hospedajes.id'), nullable = False)
    url = db.Column(db.String(255), nullable = False)
    created_at = db.Column(db.DateTime, nullable = False, default = db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable = False, default = db.func.current_timestamp(), onupdate = db.func.current_timestamp())
    
class Hospedaje_AmenidadORM(db.Model):
    __tablename__ = 'hospedajes_amenidades'

    hospedaje_id = db.Column(UUID(as_uuid = True), db.ForeignKey('hospedajes.id'), primary_key = True)
    amenidad_id = db.Column(UUID(as_uuid = True), db.ForeignKey('amenidades.id'), primary_key = True)

class HospedajeORM(db.Model):
    __tablename__ = 'hospedajes'

    id = db.Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
    nombre = db.Column(db.String(255), nullable = False)
    descripcion = db.Column(db.String(255), nullable = False)
    countryCode = db.Column(db.String(10), nullable = False)
    pais = db.Column(db.String(255), nullable = False)
    ciudad = db.Column(db.String(255), nullable = False)
    direccion = db.Column(db.String(255), nullable = False)
    latitude = db.Column(db.Float, nullable = False)
    longitude = db.Column(db.Float, nullable = False)
    rating = db.Column(db.Float, nullable = False)
    reviews = db.Column(db.Integer, nullable = False)
    created_at = db.Column(db.DateTime, nullable = False, default = db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable = False, default = db.func.current_timestamp(), onupdate = db.func.current_timestamp())
    habitaciones = db.relationship('HabitacionORM', backref = 'hospedaje', lazy = True)
    amenidades = db.relationship('AmenidadORM', secondary = 'hospedajes_amenidades', back_populates = 'hospedajes', lazy = True)
    imagenes = db.relationship('Hospedaje_ImagenORM', backref = 'hospedaje', lazy = True)

class HabitacionORM(db.Model):
    __tablename__ = 'habitaciones'

    id = db.Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
    propiedad_id = db.Column(UUID(as_uuid = True), db.ForeignKey('hospedajes.id'), nullable = False)
    code = db.Column(db.String(50), nullable = False)
    descripcion = db.Column(db.String(255), nullable = False)
    capacidad = db.Column(db.Integer, nullable = False)
    precio = db.Column(db.Float, nullable = False)
    imageUrl = db.Column(db.String(255), nullable = True)
    created_at = db.Column(db.DateTime, nullable = False, default = db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable = False, default = db.func.current_timestamp(), onupdate = db.func.current_timestamp())

class AmenidadORM(db.Model):
    __tablename__ = 'amenidades'

    id = db.Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
    name = db.Column(db.String(100), nullable = False)
    icon = db.Column(db.String(50), nullable = False)
    created_at = db.Column(db.DateTime, nullable = False, default = db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable = False, default = db.func.current_timestamp(), onupdate = db.func.current_timestamp())
    hospedajes = db.relationship('HospedajeORM', secondary = 'hospedajes_amenidades', back_populates = 'amenidades', lazy = True)

class CountryORM(db.Model):
    __tablename__ = 'countries'

    id = db.Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
    name = db.Column(db.String(100), nullable = False)
    code = db.Column(db.String(10), nullable = False)
    CurrencyCode = db.Column(db.String(10), nullable = False)
    CurrencySymbol = db.Column(db.String(10), nullable = False)
    FlagEmoji = db.Column(db.String(10), nullable = False)
    PhoneCode = db.Column(db.String(10), nullable = False)
    created_at = db.Column(db.DateTime, nullable = False, default = db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable = False, default = db.func.current_timestamp(), onupdate = db.func.current_timestamp())

