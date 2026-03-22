from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductionEntryViewSet, CuttingLogViewSet

router = DefaultRouter()
router.register(r'entries', ProductionEntryViewSet)
router.register(r'cutting-logs', CuttingLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
