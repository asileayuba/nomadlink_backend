from django.urls import path
from .views import KYCDetailCreateView, verify_kyc

urlpatterns = [
    path('', KYCDetailCreateView.as_view(), name='kyc-detail'),
    path('verify/<int:user_id>/', verify_kyc, name='kyc-review'),
]
