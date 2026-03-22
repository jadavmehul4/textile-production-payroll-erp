from rest_framework import viewsets, permissions
from .models import ProductionEntry, CuttingLog
from .serializers import ProductionEntrySerializer, CuttingLogSerializer
from authentication.permissions import HasModulePermission

class ProductionEntryViewSet(viewsets.ModelViewSet):
    queryset = ProductionEntry.objects.all()
    serializer_class = ProductionEntrySerializer
    permission_classes = [permissions.IsAuthenticated, HasModulePermission]
    permission_module = 'production'

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return ProductionEntry.objects.all()
        return ProductionEntry.objects.filter(unit=user.unit)

class CuttingLogViewSet(viewsets.ModelViewSet):
    queryset = CuttingLog.objects.all()
    serializer_class = CuttingLogSerializer
    permission_classes = [permissions.IsAuthenticated, HasModulePermission]
    permission_module = 'cutting'

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return CuttingLog.objects.all()
        return CuttingLog.objects.filter(unit=user.unit)
