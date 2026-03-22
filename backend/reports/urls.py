from django.urls import path
from .views import AdminDashboardAPIView, ProductionReportAPIView

urlpatterns = [
    path('dashboard/', AdminDashboardAPIView.as_view(), name='admin-dashboard'),
    path('production/', ProductionReportAPIView.as_view(), name='production-report'),
]
