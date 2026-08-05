from rest_framework.permissions import BasePermission

class IsAdminRole(BasePermission):
    """
    Allows access only to users with an 'admin' role token.
    """
    def has_permission(self, request, view):
        if not request.auth:
            return False
        return request.auth.get('role') == 'admin'

class IsCompanyRole(BasePermission):
    """
    Allows access only to users with a 'company' role token.
    """
    def has_permission(self, request, view):
        if not request.auth:
            return False
        return request.auth.get('role') == 'company'
