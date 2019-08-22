import requests
import jwt
import logging
import traceback

from functools import wraps
<<<<<<< HEAD
from flask import request, escape, Response, current_app, jsonify
=======
from flask import request, escape, Response, current_app
>>>>>>> cd1fc8cfa900dcdcc411498fa38d8bbae4af0852
from parse import parse
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)

OPENID_CONF_URL = 'https://login.microsoftonline.com/common/.well-known/openid-configuration'

def azure_aad_required(client_id, jwks_url=None):
    def azure_aad_required_real(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request(client_id=client_id, jwks_url=jwks_url)
            except Exception as ex:
                logger.error(ex)
                traceback.print_exc()
<<<<<<< HEAD
                if 'Signature has expired' in str(ex):
                    return jsonify({'message': 'Access token has expired'}), 429
=======
>>>>>>> cd1fc8cfa900dcdcc411498fa38d8bbae4af0852
                return Response(str(ex), status=401)
            return fn(*args, **kwargs)
        return wrapper
    return azure_aad_required_real

def _get_jwks_uri():
    logger.warning("Searching for default JWKS URI")
    res = requests.get(OPENID_CONF_URL)
    jwks_url = res.json()['jwks_uri']
    return jwks_url

def _get_jwk_key(kid, jwks_url):
    keys_object = requests.get(jwks_url or _get_jwks_uri()).json()
    public_key = None

    for key in keys_object['keys']:
        if key['kid'] == kid:
            cert = ''.join([
                '-----BEGIN CERTIFICATE-----\n',
                key['x5c'][0],
                '\n-----END CERTIFICATE-----\n',
            ])
            public_key = load_pem_x509_certificate(cert.encode(), default_backend()).public_key()
            break

    if not public_key:
        raise Exception('Falied to fetch public key for verification!')

    return public_key

def verify_jwt_in_request(client_id, jwks_url):
    token = parse('Bearer {}', request.headers['authorization'])[0]

    token_header = jwt.get_unverified_header(token)

    key = _get_jwk_key(kid=token_header['kid'], jwks_url=jwks_url)

    decoded = jwt.decode(token, key, algorithms=token_header['alg'], audience=client_id)
    return decoded

def get_user():
    token_decoded = verify_jwt_in_request(current_app.config['OIDC_RP_CLIENT_ID'], current_app.config['OIDC_OP_JWKS_ENDPOINT'])
    if token_decoded:
        if 'preferred_username' in token_decoded:
            return token_decoded['preferred_username'].lower()
        if 'appid' in token_decoded:
            return token_decoded['appid']
    else:
<<<<<<< HEAD
        return None
=======
        return None
>>>>>>> cd1fc8cfa900dcdcc411498fa38d8bbae4af0852
