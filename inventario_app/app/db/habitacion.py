from sqlalchemy.dialects.postgresql import UUID
from flask_sqlalchemy import SQLAlchemy
import uuid

#Creamos base de datos
db_habitacion = SQLAlchemy()

class HabitacionORM(db_habitacion.Model):
    __tablename__ = 'habitaciones'

    id = db_habitacion.Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
    propiedad_id = db_habitacion.Column(UUID(as_uuid = True), db_habitacion.ForeignKey('hospedajes.id'), nullable = False)
    descripcion = db_habitacion.Column(db_habitacion.String(255), nullable = False)
    capacidad = db_habitacion.Column(db_habitacion.Integer, nullable = False)
    precio = db_habitacion.Column(db_habitacion.Float, nullable = False)
    total_habitaciones = db_habitacion.Column(db_habitacion.Integer, nullable = False)
    disponibilidad = db_habitacion.Column(db_habitacion.Boolean, nullable = False)
    created_at = db_habitacion.Column(db_habitacion.DateTime, server_default = db_habitacion.func.now())
    updated_at = db_habitacion.Column(db_habitacion.DateTime, server_default = db_habitacion.func.now(), onupdate = db_habitacion.func.now())

    