import json
from urllib.request import urlopen
from flask import g 
from authlib.oauth2.rfc7523 import JWTBearerTokenValidator
from authlib.jose.rfc7517.jwk import JsonWebKey
from authlib.jose.errors import JoseError
import logging


class Auth0JWTBearerTokenValidator(JWTBearerTokenValidator):
    def __init__(self, domain, audience):
        issuer = f"https://{domain}/"
        jsonurl = urlopen(f"{issuer}.well-known/jwks.json")
        public_key = JsonWebKey.import_key_set(
            json.loads(jsonurl.read())
        )
        super(Auth0JWTBearerTokenValidator, self).__init__(
            public_key
        )
        self.claims_options = {
            "exp": {"essential": True},
            "aud": {"essential": True, "value": audience},
            "iss": {"essential": True, "value": issuer},
        }
    

    def authenticate_token(self, token_string):
        try:
            token = super().authenticate_token(token_string)
            if token is not None:
                sub = token.get('sub')
                aid = sub.split('|')[1] if '|' in sub else sub  # Split by the pipe character and take the second part
                logging.info(f"Token is authenticated: {token}")
                g.aid = aid
            else:
                logging.warning(f"Token is not authenticated")
            return token
        except JoseError as e:
            logging.error(f"JWT validation failed: {str(e)}")
            return None