from django.urls import path
from .views import KYCDetailCreateView, verify_kyc, get_kyc_status

urlpatterns = [
    path('', KYCDetailCreateView.as_view(), name='kyc-detail'),  # PUT + GET
    path('status/', get_kyc_status, name='kyc-status'),           # GET KYC STATUS ONLY
    path('verify/<int:user_id>/', verify_kyc, name='kyc-review'),  # Admin
]
