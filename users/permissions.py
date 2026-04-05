from rest_framework.permissions import BasePermission


class IsActiveUser(BasePermission):
    """Blocks inactive users even if they have a valid JWT token."""
    message = "Your account has been deactivated."

    def has_permission(self, request, view):
        return (
            request.user is not None
            and request.user.is_authenticated
            and request.user.is_active
        )


class IsAdmin(BasePermission):
    """Only users with role='admin' are allowed."""
    message = "You do not have permission to perform this action. Admin role required."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_active
            and request.user.role == 'admin'
        )


class IsAnalyst(BasePermission):
    """Only users with role='analyst' are allowed."""
    message = "You do not have permission to perform this action. Analyst role required."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_active
            and request.user.role == 'analyst'
        )


class IsViewer(BasePermission):
    """Only users with role='viewer' are allowed."""
    message = "Viewer role access only."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_active
            and request.user.role == 'viewer'
        )


class IsAdminOrAnalyst(BasePermission):
    """Admin or Analyst — used for read-heavy endpoints like records and dashboard."""
    message = "You do not have permission to perform this action. Analyst or Admin role required."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_active
            and request.user.role in ['admin', 'analyst']
        )