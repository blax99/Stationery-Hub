from rest_framework.permissions import BasePermission


def has_admin_access(user):
    return user.is_authenticated and (
        user.role == "admin" or user.is_superuser
    )


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return has_admin_access(request.user)


class IsVendor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "vendor"


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "customer"


class IsAdminOrVendor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            "admin",
            "vendor",
        ]
