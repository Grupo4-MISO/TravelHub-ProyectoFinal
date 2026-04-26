import jwt
from uuid import UUID
from datetime import datetime, timedelta
from functools import wraps
from flask import request, current_app
from app.db.models import db, User


def generate_token(user):
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role.value,
        "exp": datetime.utcnow() + timedelta(hours=24),
        "iat": datetime.utcnow()
    }

    token = jwt.encode(
        payload,
        current_app.config["JWT_SECRET_KEY"],
        algorithm="HS256"
    )

    return token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "Authorization" in request.headers:
            bearer = request.headers["Authorization"]
            if bearer.startswith("Bearer "):
                token = bearer.split(" ")[1]

        if not token:
            return {"message": "Token missing"}, 401

        try:
            data = jwt.decode(
                token,
                current_app.config["JWT_SECRET_KEY"],
                algorithms=["HS256"]
            )

            user_id = UUID(data["sub"])
            current_user = db.session.get(User, user_id)

            if not current_user:
                return {"message": "User not found"}, 404

        except jwt.ExpiredSignatureError:
            return {"message": "Token expired"}, 401
        except jwt.InvalidTokenError:
            return {"message": "Invalid token"}, 401

        return f(current_user, *args, **kwargs)

    return decorated

def roles_required(*roles):
    def wrapper(f):
        @wraps(f)
        def decorated(current_user, *args, **kwargs):

            if current_user.role.value not in roles:
                return {"message": "Unauthorized"}, 403

            return f(current_user, *args, **kwargs)

        return decorated
    return wrapper