from rest_framework import viewsets, permissions
from .models import Employee
from .serializers import EmployeeSerializer
from authentication.permissions import HasModulePermission

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated, HasModulePermission]
    permission_module = 'employee'

    def get_queryset(self):
        return Employee.objects.for_user(self.request.user)
