import jwt
from functools import wraps

from flask import current_app, request


def _extract_bearer_token():
    authorization = request.headers.get("Authorization", "")
    if authorization.startswith("Bearer "):
        return authorization.split(" ", 1)[1].strip()
    return None


def get_token_claims():
    token = _extract_bearer_token()
    if not token:
        return None, ({"error": "Se requiere token de autorizacion"}, 401)

    secret_key = current_app.config.get("SECRET_KEY") or current_app.config.get("JWT_SECRET_KEY")
    if not secret_key:
        return None, ({"error": "JWT no configurado correctamente"}, 500)

    try:
        claims = jwt.decode(token, secret_key, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None, ({"error": "El token ha expirado"}, 401)
    except jwt.InvalidTokenError:
        return None, ({"error": "Token invalido"}, 401)

    if not claims.get("sub"):
        return None, ({"error": "El token debe incluir el claim 'sub'"}, 401)

    return claims, None


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        claims, error_response = get_token_claims()
        if error_response:
            return error_response
        return f(*args, claims, **kwargs)

    return decorated