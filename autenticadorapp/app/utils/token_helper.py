import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, current_app

from app.db.models import User


def generate_token(user):
    payload = {
        "sub": str(user.id),
        "role": user.role.value,
        "exp": datetime.utcnow() + timedelta(hours=24),
        "iat": datetime.utcnow()
    }

    token = jwt.encode(
        payload,
        current_app.config["SECRET_KEY"],
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
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )

            current_user = User.query.get(data["sub"])

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