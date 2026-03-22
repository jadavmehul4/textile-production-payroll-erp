from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UnitViewSet, DepartmentViewSet, DesignationViewSet,
    BuyerViewSet, ItemViewSet, OperationViewSet,
    SizeViewSet, OperationRateViewSet
)

router = DefaultRouter()
router.register(r'units', UnitViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'designations', DesignationViewSet)
router.register(r'buyers', BuyerViewSet)
router.register(r'items', ItemViewSet)
router.register(r'operations', OperationViewSet)
router.register(r'sizes', SizeViewSet)
router.register(r'operation-rates', OperationRateViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
