from sqlalchemy.dialects.postgresql import UUID
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
import enum

# Crear instancia
db = SQLAlchemy()

class TravelerStatus(enum.Enum):
    Pending = "Pending"
    Active = "Active"
    Suspended = "Suspended"
    Blocked = "Blocked"

class document_type(enum.Enum):
    File = "File"
    Image = "Image"
    Video = "Video"

class Traveler(db.Model):
    __tablename__ = "travelers"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    documentNumber = db.Column(db.String(50), nullable=True)
    userId = db.Column(UUID(as_uuid=True), default=uuid.uuid4)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    photo = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    travelerStatus = db.Column(db.Enum(TravelerStatus), default=TravelerStatus.Pending, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

class TravelerDocument(db.Model):
    __tablename__ = "traveler_documents"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    traveler_id = db.Column(UUID(as_uuid=True), db.ForeignKey("travelers.id"), nullable=False)
    document_type = db.Column(db.Enum(document_type), nullable=False)
    document_url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

class TravelerAddress(db.Model):
    __tablename__ = "traveler_addresses"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    traveler_id = db.Column(UUID(as_uuid=True), db.ForeignKey("travelers.id"), nullable=False)
    line1 = db.Column(db.String(255), nullable=False)
    line2 = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    countryCode = db.Column(db.String(10), nullable = False)
    postal_code = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )