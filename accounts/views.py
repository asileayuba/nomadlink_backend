from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from .serializers import RegisterSerializer, LoginSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from web3 import Web3
from eth_account.messages import encode_defunct
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.utils.text import slugify
from datetime import timedelta
import uuid

# Swagger
from drf_spectacular.utils import (
    extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse, OpenApiTypes
)

# Web3 connection
w3 = Web3(Web3.HTTPProvider('https://rpc-amoy.polygon.technology'))


# --------------------
# Register View
# --------------------
@extend_schema(
    request=RegisterSerializer,
    responses={
        201: OpenApiResponse(
            description="Successfully registered",
            examples=[
                OpenApiExample(
                    "Register Success",
                    value={
                        "access": "eyJ0eXAiOiJKV1QiLCJhbG...",
                        "refresh": "eyJhbGciOiJIUzI1NiIsIn...",
                        "wallet_address": None,
                        "username": "asileayuba",
                        "email": "asile@example.com"
                    }
                )
            ]
        )
    },
    tags=["Authentication"]
)
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'wallet_address': user.wallet_address,
            'username': user.username,
            'email': user.email
        }, status=status.HTTP_201_CREATED)


# --------------------
# Email/Password Login View
# --------------------
@extend_schema(
    request=LoginSerializer,
    responses={
        200: OpenApiResponse(
            description="Successful login",
            examples=[
                OpenApiExample(
                    "Login Success",
                    value={
                        "access": "eyJ0eXAiOiJKV1QiLCJhbG...",
                        "refresh": "eyJhbGciOiJIUzI1NiIsIn...",
                        "wallet_address": None,
                        "username": "asileayuba",
                        "email": "asile@example.com"
                    }
                )
            ]
        )
    },
    tags=["Authentication"]
)
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'wallet_address': user.wallet_address,
            'username': user.username,
            'email': user.email
        }, status=status.HTTP_200_OK)


# --------------------
# Web3 Signature Auth View
# --------------------
@extend_schema(
    request={
        "application/json": {
            "example": {
                "wallet_address": "0x45517BeeFE934Ca1041F9E05f799184a32A29a7a",
                "signed_message": "0x1234abcd5678...",
                "original_message": "Sign this message to login: GZb116HDdwU6Bn8UySJh4s4L"
            }
        }
    },
    responses={
        200: OpenApiResponse(
            description="Login with signed wallet message",
            examples=[
                OpenApiExample(
                    "Web3 Login Success",
                    value={
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGci...",
                        "refresh": "eyJhbGciOiJIUzI1NiIsIn...",
                        "wallet_address": "0x45517BeeFE934Ca1041F9E05f799184a32A29a7a",
                        "username": "wallet-45517"
                    }
                )
            ]
        ),
        400: OpenApiResponse(
            description="Invalid signature or request format",
            examples=[
                OpenApiExample(
                    "Missing Data",
                    value={"error": "Missing data"}
                ),
                OpenApiExample(
                    "Signature Mismatch",
                    value={"error": "Signature mismatch"}
                ),
                OpenApiExample(
                    "Nonce expired",
                    value={"error": "Nonce expired. Please request a new one."}
                )
            ]
        )
    },
    tags=["Authentication"],
    description="Authenticates a user using MetaMask/Web3 signature and nonce. Returns access and refresh tokens."
)
class WalletSignatureAuthView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        wallet_address = request.data.get('wallet_address')
        signature = request.data.get('signed_message')
        original_message = request.data.get('original_message')

        if not all([wallet_address, signature, original_message]):
            return Response({"error": "Missing data"}, status=400)

        try:
            user = CustomUser.objects.get(wallet_address=wallet_address.lower())
        except CustomUser.DoesNotExist:
            return Response({"error": "Wallet not registered for nonce"}, status=400)

        expected_message = f"Sign this message to login: {user.nonce}"
        if original_message != expected_message:
            return Response({"error": "Nonce mismatch or invalid message"}, status=400)

        if not user.nonce_created_at or timezone.now() > user.nonce_created_at + timedelta(minutes=5):
            return Response({"error": "Nonce expired. Please request a new one."}, status=403)

        try:
            encoded = encode_defunct(text=original_message)
            recovered = w3.eth.account.recover_message(encoded, signature=signature)
        except Exception as e:
            return Response({"error": f"Signature verification failed: {str(e)}"}, status=400)

        if recovered.lower() != wallet_address.lower():
            return Response({"error": "Signature mismatch"}, status=401)

        # Reset nonce after successful login
        user.nonce = None
        user.nonce_created_at = None
        user.last_nonce_used = timezone.now()
        user.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "wallet_address": user.wallet_address,
            "username": user.username
        })


# --------------------
# Nonce Generation Endpoint
# --------------------
@extend_schema(
    parameters=[
        OpenApiParameter(
            name='wallet',
            type=str,
            location=OpenApiParameter.QUERY,
            required=True,
            description="Wallet address to generate a unique nonce for"
        )
    ],
    responses={
        200: OpenApiResponse(
            description="Returns nonce for signing",
            examples=[
                OpenApiExample(
                    "Nonce Response",
                    value={
                        "message": "Sign this message to login: j8DKsm123X",
                        "nonce": "j8DKsm123X"
                    }
                )
            ]
        )
    },
    tags=["Authentication"],
    description="Generates a nonce that the frontend must sign to login with wallet"
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_wallet_nonce(request):
    wallet_address = request.GET.get("wallet")
    if not wallet_address:
        return Response({"error": "Missing wallet address"}, status=400)

    wallet_address = wallet_address.lower()
    user = CustomUser.objects.filter(wallet_address=wallet_address).first()

    # Create new user if doesn't exist
    if not user:
        base_username = slugify(wallet_address)[:20]
        for _ in range(5):
            candidate = f"{base_username}-{uuid.uuid4().hex[:6]}"
            if not CustomUser.objects.filter(username=candidate).exists():
                username = candidate
                break
        else:
            return Response({"error": "Could not generate unique username"}, status=500)

        user = CustomUser.objects.create_user(wallet_address=wallet_address, username=username)

    nonce = get_random_string(24)
    user.nonce = nonce
    user.nonce_created_at = timezone.now()
    user.save()

    return Response({
        "message": f"Sign this message to login: {nonce}",
        "nonce": nonce
    })


# --------------------
# User Profile View
# --------------------
@extend_schema(
    responses={
        200: OpenApiResponse(
            description="Authenticated user's profile info",
            examples=[
                OpenApiExample(
                    "User Profile",
                    value={
                        "wallet_address": "0x45517meeFE934Ca1041F9E05f799184a87A29a7b",
                        "username": "wallet-45517",
                        "email": "asile@example.com",
                        "kyc": {
                            "is_verified": False,
                            "level": "level_1",
                            "review_status": "pending"
                        },
                        "bookings": [
                            {
                                "destination": "Lagos",
                                "start_date": "2025-07-10",
                                "end_date": "2025-07-15",
                                "status": "pending"
                            }
                        ]
                    }
                )
            ]
        )
    },
    tags=["User"],
    description="Returns authenticated user's wallet, KYC status, and bookings"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user
    try:
        kyc = user.kyc
        kyc_data = {
            "is_verified": kyc.is_verified,
            "level": kyc.level,
            "review_status": kyc.review_status
        }
    except:
        kyc_data = {
            "is_verified": False,
            "level": None,
            "review_status": "not_submitted"
        }

    bookings = user.bookings.all().values('destination', 'start_date', 'end_date', 'status')

    return Response({
        "wallet_address": user.wallet_address,
        "username": user.username,
        "email": user.email,
        "kyc": kyc_data,
        "bookings": list(bookings)
    })
