from urllib.parse import urlparse

from functools import wraps
from flask import request, make_response, jsonify
import datetime
import jwt


def jwt_required(f):
    """
    Ensure jwt token is provided and valid
    :param f: function to decorated
    :return: decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            auth_header = request.headers.get('Authorization').split(' ')[-1]
        except Exception as e:
            print(e)
            return make_response(jsonify({"message": 'Unauthorized. Please login'})), 401
        result = decode_auth_token(auth_header)
        try:
            if int(result):
                pass
        except Exception as e:
            print(e)
            return make_response(jsonify({"message": result})), 401
        return f(*args, **kwargs)
    return decorated_function


def encode_auth_token(user_id):
    """
    Encodes a payload to generate JWT Token
    :param user_id: Logged in user Id
    :return: JWT token
    :TODO add secret key to app configuration
    """
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1, seconds=30),
        'iat': datetime.datetime.utcnow(),
        'sub': user_id
    }
    return jwt.encode(
        payload,
        'SECRET_KEY',
        algorithm='HS256'
    )


def decode_auth_token(auth_token):
    """
    Validates the auth token
    :param auth_token:
    :return: integer|string
    """
    try:
        payload = jwt.decode(auth_token, 'SECRET_KEY', algorithm='HS256')
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'


def db_config(config_file):
    """
    This function extracts postgres url
    and return database login information
    :param config_file: Configuration file
    :return: database login information
    """
    result = urlparse(config_file)
    config = {
        'database': result.path[1:],
        'user': result.username,
        'password': result.password,
        'host': result.hostname
    }
    return config

