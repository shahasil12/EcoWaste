"""
Custom JWT authentication backend for Role-based authentication.
Decodes the JWT and attaches the appropriate instance (Citizen, Company, or User)
to request.user based on the role specified in the token payload.
"""
from django.contrib.auth.models import User
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from waste.models import Citizen, Company

class RoleBasedJWTAuthentication(BaseAuthentication):
    """
    Reads `Authorization: Bearer <token>` header, decodes the JWT,
    and returns the matching instance as request.user.
    It also sets request.auth to the token payload.
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

        role = validated_token.get('role')
        if not role:
            raise AuthenticationFailed('Token payload missing role.')

        if role == 'citizen':
            citizen_id = validated_token.get('citizen_id')
            try:
                user_obj = Citizen.objects.get(id=citizen_id)
            except Citizen.DoesNotExist:
                raise AuthenticationFailed('Citizen not found.')
        elif role == 'company':
            company_id = validated_token.get('company_id')
            try:
                user_obj = Company.objects.get(id=company_id)
            except Company.DoesNotExist:
                raise AuthenticationFailed('Company not found.')
        elif role == 'admin':
            user_id = validated_token.get('user_id')
            try:
                user_obj = User.objects.get(id=user_id)
            except User.DoesNotExist:
                raise AuthenticationFailed('Admin not found.')
        else:
            raise AuthenticationFailed('Invalid role.')

        return (user_obj, validated_token)
