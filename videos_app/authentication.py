from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings


class TokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return None
        
        token = auth_header.split(' ')[1] if ' ' in auth_header else None

        if token != settings.API_TOKEN:
            raise AuthenticationFailed('Invalid API token.')

        return (None, None)
