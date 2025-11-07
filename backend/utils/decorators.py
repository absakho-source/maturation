from functools import wraps
from flask import request, jsonify

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            role = request.headers.get('Role')
            if role not in roles:
                return jsonify({"error": "Accès non autorisé"}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator
