from rest_framework import permissions

class HasModulePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True

        module = getattr(view, 'permission_module', None)
        if not module:
            return True # If no module specified, allow authenticated

        from .models import PermissionMatrix
        perm = PermissionMatrix.objects.filter(role=request.user.role, module=module).first()
        if not perm:
            return False

        if request.method in permissions.SAFE_METHODS:
            return perm.can_view
        
        return perm.can_edit
