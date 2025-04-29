from flask import jsonify
import jwt

def verificar_token(auth_header: str, secret_key: str) -> str | int:
    # Obtém o token do cabeçalho da requisição

    if not auth_header:
        return 403

    parts = auth_header.split()
    if parts[0].lower() != 'bearer' or len(parts) != 2:
        return 401

    token = parts[1]

    try:
        # Decodifica o token
        decoded = jwt.decode(token, secret_key, algorithms=["HS256"])
        return decoded['user']
    except jwt.ExpiredSignatureError:
        return 401
    except jwt.InvalidTokenError:
        return 403