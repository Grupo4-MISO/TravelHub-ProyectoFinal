import token

import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, current_app

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
            secret_key = current_app.config.get("SECRET_KEY") or current_app.config.get("JWT_SECRET_KEY")
            data = jwt.decode(
                token,
                secret_key,
                algorithms=["HS256"]
            )

            current_user = data

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

            user_role = current_user.get("role") if isinstance(current_user, dict) else None

            if user_role not in roles:
                return {"message": "Unauthorized"}, 403

            return f(current_user, *args, **kwargs)

        return decorated
    return wrapper

def get_userId_from_token():
    token = None

    if "Authorization" in request.headers:
        bearer = request.headers["Authorization"]
        if bearer.startswith("Bearer "):
            token = bearer.split(" ")[1]

    if not token:
        return {"message": "Token missing"}, 401

    try:
        secret_key = current_app.config.get("SECRET_KEY") or current_app.config.get("JWT_SECRET_KEY")
        data = jwt.decode(
            token,
            secret_key,
            algorithms=["HS256"]
        )
        return data["sub"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    
def get_userName_from_token():
    token = None

    if "Authorization" in request.headers:
        bearer = request.headers["Authorization"]
        if bearer.startswith("Bearer "):
            token = bearer.split(" ")[1]

    if not token:
        return {"message": "Token missing"}, 401
    try:
        secret_key = current_app.config.get("SECRET_KEY") or current_app.config.get("JWT_SECRET_KEY")
        data = jwt.decode(
            token,
            secret_key,
            algorithms=["HS256"]
        )
        return data["username"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None