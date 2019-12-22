from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serialiser
from itsdangerous.exc import SignatureExpired
import os

from .models import User


def make_hash(user):
    try:
        s = Serialiser(os.getenv('SECRET_KEY'), expires_in=999999999999999999)
        data = {'user': user.contact}
        return s.dumps(data).decode('utf-8')
    except Exception as e:
        return None


def check_hash(token):
    try:
        data = Serialiser(os.getenv('SECRET_KEY')).loads(str(token))
        if not User.objects.get_by_natural_key(data['user']):
            return False, 'No user found with this number'
        return True, User.objects.get_by_natural_key(data['user'])
    except Exception as e:
        return False, None
