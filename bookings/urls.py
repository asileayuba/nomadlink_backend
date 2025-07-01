from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import BookingViewSet, mint_trailproof

router = DefaultRouter()
router.register('', BookingViewSet, basename='bookings')

urlpatterns = [
    path('', include(router.urls)),
    path('mint/', mint_trailproof, name='mint-trailproof'),

]
