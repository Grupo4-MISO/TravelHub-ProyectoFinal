from sqlalchemy.dialects.postgresql import UUID
from flask_sqlalchemy import SQLAlchemy
import uuid

#Creamos base de datos
db_hospedaje = SQLAlchemy()

class HospedajeORM(db_hospedaje.Model):
    __tablename__ = 'hospedajes'

    id = db_hospedaje.Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
    nombre = db_hospedaje.Column(db_hospedaje.String(255), nullable = False)
    pais = db_hospedaje.Column(db_hospedaje.String(255), nullable = False)
    ciudad = db_hospedaje.Column(db_hospedaje.String(255), nullable = False)
    direccion = db_hospedaje.Column(db_hospedaje.String(255), nullable = False)
    rating = db_hospedaje.Column(db_hospedaje.Float, nullable = False)
    created_at = db_hospedaje.Column(db_hospedaje.DateTime, server_default = db_hospedaje.func.now())
    updated_at = db_hospedaje.Column(db_hospedaje.DateTime, server_default = db_hospedaje.func.now(), onupdate = db_hospedaje.func.now())

    