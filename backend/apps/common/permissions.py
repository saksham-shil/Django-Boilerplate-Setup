"""
Centralized permission classes for the CSR Matchmaking project.

This module contains reusable permission classes that can be used across
all API views to enforce consistent access control.
"""

from rest_framework.permissions import BasePermission


class HasRequiredPermissions(BasePermission):
    """
    Generic permission class that checks required permissions on the view.
    
    This permission class allows views to declare their required permissions
    explicitly, supporting both single and multiple permission requirements.
    
    Usage:
        class YourAPIView(APIView):
            permission_classes = [IsAuthenticated, HasRequiredPermissions]
            required_permissions = ['app.permission_name']
            
            # For multiple permissions (ALL must be satisfied):
            # required_permissions = ['app.perm1', 'app.perm2', 'app.perm3']
            
            # For optional permissions (ANY can be satisfied):
            # required_permissions_any = ['app.perm1', 'app.perm2']
    
    Attributes on view class:
        required_permissions (list): List of permissions ALL of which must be satisfied (AND logic)
        required_permissions_any (list): List of permissions ANY of which must be satisfied (OR logic)
        
    If both are specified, the user must satisfy ALL required_permissions 
    AND at least one from required_permissions_any.
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has the required permissions.
        
        Args:
            request: The HTTP request object
            view: The view being accessed
            
        Returns:
            bool: True if user has required permissions, False otherwise
        """
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Get required permissions from view
        required_permissions = getattr(view, 'required_permissions', [])
        required_permissions_any = getattr(view, 'required_permissions_any', [])
        
        # If no permissions specified, allow access (assumes other permission classes handle auth)
        if not required_permissions and not required_permissions_any:
            return True
        
        # Check ALL required permissions (AND logic)
        if required_permissions:
            has_all_required = all(
                request.user.has_perm(perm) for perm in required_permissions
            )
            if not has_all_required:
                return False
        
        # Check ANY required permissions (OR logic)
        if required_permissions_any:
            has_any_required = any(
                request.user.has_perm(perm) for perm in required_permissions_any
            )
            if not has_any_required:
                return False
        
        return True


class IsSuperUserOrAdmin(BasePermission):
    """
    Permission class that allows access only to superusers or admin users.
    
    Usage:
        class AdminOnlyView(APIView):
            permission_classes = [IsAuthenticated, IsSuperUserOrAdmin]
    """
    
    def has_permission(self, request, view):
        """Check if user is superuser or admin."""
        if not request.user or not request.user.is_authenticated:
            return False
        
        return request.user.is_superuser or request.user.is_staff


class IsOwnerOrHasPermission(BasePermission):
    """
    Permission class that allows access to object owners or users with specific permissions.
    
    This is useful for APIs where users can access their own data OR 
    admin users can access any data.
    
    Usage:
        class MyProjectView(APIView):
            permission_classes = [IsAuthenticated, IsOwnerOrHasPermission]
            required_permissions = ['projects.can_view_all_projects']  # Admin permission
            owner_field = 'created_by'  # Field name that identifies the owner
    """
    
    def has_object_permission(self, request, view, obj):
        """Check if user is owner or has required permissions."""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user is the owner
        owner_field = getattr(view, 'owner_field', 'created_by')
        if hasattr(obj, owner_field):
            owner = getattr(obj, owner_field)
            if owner == request.user:
                return True
        
        # Check if user has admin permissions
        required_permissions = getattr(view, 'required_permissions', [])
        if required_permissions:
            return all(request.user.has_perm(perm) for perm in required_permissions)
        
        return False