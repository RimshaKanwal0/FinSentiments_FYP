# middleware.py within any of your apps, for example 'base' app

from threading import local

_user = local()

class GlobalRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _user.value = request.user
        response = self.get_response(request)
        return response

    @staticmethod
    def get_current_user():
        return _user.value
