from sqlalchemy.dialects.postgresql import UUID
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid, enum

# Crear instancia
db = SQLAlchemy()

# Enum de roles
class UserRole(enum.Enum):
    ACCOMODATION = "Accomodation"
    TRAVELER = "Traveler"

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)

    password_hash = db.Column(db.String(255), nullable=False)

    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)

    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)

    role = db.Column(
        db.Enum(UserRole, name="user_roles"),
        default=UserRole.TRAVELER,
        nullable=False
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    last_login = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<User(username={self.username}, role={self.role.value})>"