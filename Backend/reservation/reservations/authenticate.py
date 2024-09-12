import logging

from rest_framework_simplejwt.authentication import JWTStatelessUserAuthentication
from django.conf import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# https://stackoverflow.com/questions/66247988/how-to-store-jwt-tokens-in-httponly-cookies-with-drf-djangorestframework-simplej
class CustomAuthentication(JWTStatelessUserAuthentication):

    def authenticate(self, request):
        header = self.get_header(request)

        if header is not None:
            raw_token = self.get_raw_token(header)
        else:
            raw_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE'])

        if raw_token is None:
            logger.warning("No token provided in the request.")
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
        except Exception as e:
            logger.error(f"Token validation failed: {str(e)}")
            return None

        return self.get_user(validated_token), validated_token
