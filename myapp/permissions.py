from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'admin'

class IsLandlord(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'landlord'

class IsCaretaker(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'caretaker'

class IsTenant(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'tenant'

class IsUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'user'
