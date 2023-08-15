from functools import wraps
from flask import request, jsonify
import os
import http.client

AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN")
API_IDENTIFIER = os.environ.get("API_IDENTIFIER")
SECRET = os.environ.get("AUTH0_SECRET")
ALGORITHM = os.environ.get("ALGORITHM")

print(API_IDENTIFIER)


# def verify_token(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = request.headers.get("Authorization")
#         if not token:
#             return jsonify({"error": "Token is missing"}), 401
#         token=token.split()[1] #removing bearer
#         try:
#             payload = jwt.decode(
#                 token,
#                 SECRET,
#                 algorithms=[ALGORITHM],
#                 audience=API_IDENTIFIER,
#                 issuer=f'https://{AUTH0_DOMAIN}/'
#             )
#         except JWTError:
#             return jsonify({"error": "Token is invalid"}), 401
#         request.aid = payload['sub'] #adds the auth_id to the request object
#         return f(*args, **kwargs)
#     return decorated


def get_email(f):  # gets email from auth_token. should only be used after verify_token
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Token is missing"}), 401
        token = token.split()[1]  # removing bearer
        conn = http.client.HTTPSConnection("")
        try:
            payload = jwt.decode(
                token,
                SECRET,
                algorithms=[ALGORITHM],
                audience=API_IDENTIFIER,
                issuer=f"https://{AUTH0_DOMAIN}/",
            )
        except JWTError:
            return jsonify({"error": "Token is invalid"}), 401
        request.aid = payload["sub"]  # adds the auth_id to the request object
        return f(*args, **kwargs)

    return decorated
