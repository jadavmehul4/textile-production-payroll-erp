from django.utils.deprecation import MiddlewareMixin
from django.db import models

class UnitIsolationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            # Attach unit_id to request for easy access
            request.unit_id = getattr(request.user, 'unit_id', None)
            
            # Global Super Admin doesn't need isolation
            if request.user.is_superuser:
                request.unit_id = None
        else:
            request.unit_id = None

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Additional logic can be added here to inject filters into querysets
        pass
