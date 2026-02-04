"""
Custom permissions for the library API
"""
from rest_framework import permissions


class IsLibrarian(permissions.BasePermission):
    """
    Permission to check if user is a librarian (staff member)
    """
    message = "Only librarians can perform this action."
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)


class IsMemberOrLibrarian(permissions.BasePermission):
    """
    Permission to check if user is authenticated (librarian or member)
    """
    message = "Only authenticated members and librarians can access this resource."
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsLibrarianOrReadOnly(permissions.BasePermission):
    """
    Permission to allow read-only access to everyone,
    but only librarians can add/update/delete
    """
    message = "Only librarians can modify books."
    
    def has_permission(self, request, view):
        # Allow read-only methods
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only librarians can add/update/delete
        return bool(request.user and request.user.is_staff)
    
    def has_object_permission(self, request, view, obj):
        # Allow read-only access
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only librarians can modify
        return bool(request.user and request.user.is_staff)


class CanBorrowReturnBooks(permissions.BasePermission):
    """
    Permission to check if user can borrow/return books
    Only authenticated users can borrow/return
    """
    message = "Only authenticated members can borrow/return books."
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
