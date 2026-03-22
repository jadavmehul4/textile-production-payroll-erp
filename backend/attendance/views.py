from rest_framework import viewsets, permissions
from .models import Attendance
from .serializers import AttendanceSerializer
from authentication.permissions import HasModulePermission

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated, HasModulePermission]
    permission_module = 'attendance'

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Attendance.objects.all()
        return Attendance.objects.filter(unit=user.unit)
