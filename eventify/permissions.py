from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrReadOnly(BasePermission):
    """
    - Allow GET (safe methods) for everyone
    - Allow POST only for admin users
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True  # GET, HEAD, OPTIONS allowed for anyone
        return request.user and request.user.is_authenticated and request.user.is_staff
