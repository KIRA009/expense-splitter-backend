import django.middleware.common as common
from .utils import make_hash


class CustomMiddleware(common.CommonMiddleware):
    def process_request(self, request):
        return super().process_request(request)

    def process_response(self, request, response):
        response = super().process_response(request, response)
        if request.user.is_authenticated:
            response._headers['token'] = 'Token', make_hash(request.user)
        return response
