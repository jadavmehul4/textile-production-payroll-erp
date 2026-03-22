from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Sum, Count
from production.models import ProductionEntry
from attendance.models import Attendance
from payroll.models_salary import SalaryRecord
from erp_core.models import Employee

class AdminDashboardAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        unit_filter = {} if user.is_superuser else {'unit': user.unit}
        
        # Global or Unit Stats
        total_employees = Employee.objects.filter(**unit_filter, status=True).count()
        total_production = ProductionEntry.objects.filter(**unit_filter).aggregate(total=Sum('quantity'))['total'] or 0
        total_payroll = SalaryRecord.objects.filter(**unit_filter).aggregate(total=Sum('net_salary'))['total'] or 0
        
        # Recent Production
        recent_production = ProductionEntry.objects.filter(**unit_filter).order_by('-created_at')[:5]
        
        return Response({
            'stats': {
                'total_employees': total_employees,
                'total_production': total_production,
                'total_payroll': total_payroll,
            },
            'recent_production': [
                {
                    'employee': entry.employee.full_name,
                    'quantity': entry.quantity,
                    'amount': entry.total_amount,
                    'date': entry.date
                } for entry in recent_production
            ]
        })

class ProductionReportAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        unit_filter = {} if user.is_superuser else {'unit': user.unit}
        
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = ProductionEntry.objects.filter(**unit_filter)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
            
        data = queryset.values('date', 'buyer__name', 'item__name').annotate(
            total_qty=Sum('quantity'),
            total_val=Sum('total_amount')
        ).order_by('-date')
        
        return Response(data)
