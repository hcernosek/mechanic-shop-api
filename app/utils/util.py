
from datetime import datetime, timedelta, timezone
from jose import jwt
import jose
from functools import wraps
from flask import request, jsonify

SECRET_KEY = "secret-key"

def encode_token(customer_id):  # using unique pieces of info to make our tokens user specific
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=0, hours=1),  # expires in 1 hour
        'iat': datetime.now(timezone.utc),  # issued at
        'sub': str(customer_id)  # must be string, else decoding fails
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

# Decorator for encode token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:

            token = request.headers['Authorization'].split(" ")[1] # Returns the token with 'Bearer' removed.

            if not token:
                return jsonify({'message': 'Token is missing'}), 400
            
            try:
                data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
                print(data)
                customer_id = data['sub']

            # May have some issues with running this code. Double check later.
            except jwt.ExpiredSignatureError as e:
                return jsonify({'message': 'Invalid Expired'}), 400
            except jwt.InvalidTokenError as e:
                return jsonify({'message': 'Invalid Token'}), 400
            
            return f(customer_id, *args, **kwargs)
        
        else: # Authorization header not found
            return jsonify({'message': 'Login to access this resource'}), 400
        
    return decorated

