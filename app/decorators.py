from .utils import check_hash


def login_required(func):
    def inner(*args, **kwargs):
        token = args[1].context.headers.get('Token')
        if token:
            unhashed, user_or_message = check_hash(token)
            if unhashed:
                args[1].context.user = user_or_message
            else:
                return user_or_message
            return func(*args, **kwargs)
        return None
    return inner
