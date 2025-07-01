from django.urls import path
from .views import RegisterView, LoginView, WalletSignatureAuthView, user_profile,get_wallet_nonce 

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('wallet-signin/', WalletSignatureAuthView.as_view(), name='wallet-signin'),
    path('nonce/', get_wallet_nonce, name='wallet-nonce'),
    path('profile/', user_profile, name='user-profile'),
]
