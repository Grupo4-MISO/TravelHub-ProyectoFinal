from sqlalchemy.dialects.postgresql import UUID
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

# Crear instancia
db = SQLAlchemy()

class Manager(db.Model):
    __tablename__ = "providers"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    hospedajeId = db.Column(UUID(as_uuid=True), nullable=False)

    userId = db.Column(UUID(as_uuid=True), default=uuid.uuid4)

    userName = db.Column(db.String(50), unique=True, nullable=False, index=True)

    email = db.Column(db.String(100), unique=True, nullable=False, index=True)

    first_name = db.Column(db.String(50), nullable=True)
    
    last_name = db.Column(db.String(50), nullable=True)
  
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
