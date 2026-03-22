from rest_framework import viewsets, permissions
from .models import Unit, Department, Designation, Buyer, Item, Operation, Size, OperationRate
from .serializers import (
    UnitSerializer, DepartmentSerializer, DesignationSerializer,
    BuyerSerializer, ItemSerializer, OperationSerializer,
    SizeSerializer, OperationRateSerializer
)

class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    permission_classes = [permissions.IsAuthenticated]

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        unit_id = self.request.query_params.get('unit_id')
        if unit_id:
            return self.queryset.filter(unit_id=unit_id)
        return self.queryset

class DesignationViewSet(viewsets.ModelViewSet):
    queryset = Designation.objects.all()
    serializer_class = DesignationSerializer
    permission_classes = [permissions.IsAuthenticated]

class BuyerViewSet(viewsets.ModelViewSet):
    queryset = Buyer.objects.all()
    serializer_class = BuyerSerializer
    permission_classes = [permissions.IsAuthenticated]

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

class OperationViewSet(viewsets.ModelViewSet):
    queryset = Operation.objects.all()
    serializer_class = OperationSerializer
    permission_classes = [permissions.IsAuthenticated]

class SizeViewSet(viewsets.ModelViewSet):
    queryset = Size.objects.all()
    serializer_class = SizeSerializer
    permission_classes = [permissions.IsAuthenticated]

class OperationRateViewSet(viewsets.ModelViewSet):
    queryset = OperationRate.objects.all()
    serializer_class = OperationRateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        unit_id = self.request.query_params.get('unit_id')
        if unit_id:
            return self.queryset.filter(unit_id=unit_id)
        return self.queryset
