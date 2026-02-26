from sqlalchemy.dialects.postgresql import UUID
from flask_sqlalchemy import SQLAlchemy
import uuid

#Creamos base de datos
db = SQLAlchemy()

class HabitacionORM(db.Model):
    __tablename__ = 'habitaciones'

    id = db.Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
    propiedad_id = db.Column(UUID(as_uuid = True), db.ForeignKey('hospedajes.id'), nullable = False)
    descripcion = db.Column(db.String(255), nullable = False)
    capacidad = db.Column(db.Integer, nullable = False)
    precio = db.Column(db.Float, nullable = False)
    total_habitaciones = db.Column(db.Integer, nullable = False)
    disponibilidad = db.Column(db.Boolean, nullable = False)
    created_at = db.Column(db.DateTime, server_default = db.func.now())
    updated_at = db.Column(db.DateTime, server_default = db.func.now(), onupdate = db.func.now())

    