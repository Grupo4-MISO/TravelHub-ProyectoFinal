from sqlalchemy.dialects.postgresql import UUID
from flask_sqlalchemy import SQLAlchemy
import uuid

#Creamos base de datos
db = SQLAlchemy()

class HospedajeORM(db.Model):
    __tablename__ = 'hospedajes'

    id = db.Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
    nombre = db.Column(db.String(255), nullable = False)
    pais = db.Column(db.String(255), nullable = False)
    ciudad = db.Column(db.String(255), nullable = False)
    direccion = db.Column(db.String(255), nullable = False)
    rating = db.Column(db.Float, nullable = False)
    created_at = db.Column(db.DateTime, server_default = db.func.now())
    updated_at = db.Column(db.DateTime, server_default = db.func.now(), onupdate = db.func.now())

    