from sqlalchemy.dialects.postgresql import UUID
from flask_sqlalchemy import SQLAlchemy
import uuid

#Creamos base de datos con SQLAlchemy
db = SQLAlchemy()

class HospedajeORM(db.Model):
    __tablename__ = 'hospedajes'

    id = db.Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
    nombre = db.Column(db.String(255), nullable = False)
    pais = db.Column(db.String(255), nullable = False)
    ciudad = db.Column(db.String(255), nullable = False)
    direccion = db.Column(db.String(255), nullable = False)
    rating = db.Column(db.Float, nullable = False)
    created_at = db.Column(db.DateTime, nullable = False, default = db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable = False, default = db.func.current_timestamp(), onupdate = db.func.current_timestamp())
    habitaciones = db.relationship('HabitacionORM', backref = 'hospedaje', lazy = True)


class HabitacionORM(db.Model):
    __tablename__ = 'habitaciones'

    id = db.Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
    propiedad_id = db.Column(UUID(as_uuid = True), db.ForeignKey('hospedajes.id'), nullable = False)
    descripcion = db.Column(db.String(255), nullable = False)
    capacidad = db.Column(db.Integer, nullable = False)
    precio = db.Column(db.Float, nullable = False)
    created_at = db.Column(db.DateTime, nullable = False, default = db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable = False, default = db.func.current_timestamp(), onupdate = db.func.current_timestamp())