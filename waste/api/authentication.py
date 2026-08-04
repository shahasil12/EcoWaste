"""
Custom JWT authentication backend for the Citizen model.
Since Citizen does not extend Django's auth.User, we decode the JWT
manually and attach the Citizen instance to request.user.
"""
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from waste.models import Citizen


class CitizenJWTAuthentication(BaseAuthentication):
    """
    Reads `Authorization: Bearer <token>` header, decodes the JWT,
    and returns the matching Citizen as request.user.
    """

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None  # Let other authenticators try or allow anonymous

        raw_token = auth_header.split(' ')[1]

        try:
            validated_token = AccessToken(raw_token)
        except (TokenError, InvalidToken) as e:
            raise AuthenticationFailed(f'Invalid or expired token: {e}')

        citizen_id = validated_token.get('citizen_id')
        if not citizen_id:
            raise AuthenticationFailed('Token payload missing citizen_id.')

        try:
            citizen = Citizen.objects.get(id=citizen_id)
        except Citizen.DoesNotExist:
            raise AuthenticationFailed('Citizen not found.')

        return (citizen, validated_token)
