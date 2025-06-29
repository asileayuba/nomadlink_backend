from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import BookingViewSet

router = DefaultRouter()
router.register('', BookingViewSet, basename='bookings')

urlpatterns = [
    path('', include(router.urls)),
]
