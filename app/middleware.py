import django.middleware.common as common


class CustomMiddleware(common.CommonMiddleware):
    def process_request(self, request):
        super().process_request(request)
