from rest_framework import viewsets, permissions
from .models import Advance
from .serializers import AdvanceSerializer
from authentication.permissions import HasModulePermission

class AdvanceViewSet(viewsets.ModelViewSet):
    queryset = Advance.objects.all()
    serializer_class = AdvanceSerializer
    permission_classes = [permissions.IsAuthenticated, HasModulePermission]
    permission_module = 'advance'

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Advance.objects.all()
        return Advance.objects.filter(unit=user.unit)
