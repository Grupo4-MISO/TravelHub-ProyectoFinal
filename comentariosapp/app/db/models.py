from sqlalchemy.dialects.postgresql import UUID
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

# Crear instancia
db = SQLAlchemy()

class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    hospedajeId = db.Column(UUID(as_uuid=True), nullable=False)

    userId = db.Column(UUID(as_uuid=True), default=uuid.uuid4)

    userName = db.Column(db.String(100), nullable=False)

    rating = db.Column(db.Float, nullable=False)

    comment = db.Column(db.Text, nullable=False)
  
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
