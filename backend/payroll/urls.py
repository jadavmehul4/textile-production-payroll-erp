from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdvanceViewSet

router = DefaultRouter()
router.register(r'advances', AdvanceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
