from sqlalchemy.dialects.postgresql import UUID
from flask_sqlalchemy import SQLAlchemy
import uuid

#Creamos base de datos
db = SQLAlchemy()

class ReservaORM(db.Model):
    __tablename__ = 'reservas'
    id = db.Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
    public_id = db.Column(db.String(12), unique=True, nullable=False, index=True, default=lambda: "RSV-" + uuid.uuid4().hex[:8].upper())
    habitacion_id = db.Column(UUID(as_uuid = True), nullable = False)
    check_in = db.Column(db.Date, nullable = False)
    check_out = db.Column(db.Date, nullable = False)
    estado = db.Column(db.String(20), nullable = False, default = 'pendiente')
    created_at = db.Column(db.DateTime, nullable = False, default = db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable = False, default = db.func.current_timestamp(), onupdate = db.func.current_timestamp())