from rest_framework import mixins, viewsets, permissions
from .models import Booking
from .serializers import BookingSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Swagger
from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiResponse,
    OpenApiTypes
)

# ----------------------------
# BookingViewSet (GET + POST)
# ----------------------------
@extend_schema(
    tags=["Booking"],
    description="Authenticated user can view or create bookings. Only their own bookings are returned.",

    request=OpenApiExample(
        name="CreateBookingExample",
        value={
            "destination": "Nairobi",
            "start_date": "2025-07-10",
            "end_date": "2025-07-15",
            "status": "pending"
        },
        request_only=True
    ),

    responses={
        200: OpenApiResponse(
            response=BookingSerializer,
            description="Returns list of user's bookings or newly created booking",
            examples=[
                OpenApiExample(
                    name="BookingResponseExample",
                    value={
                        "id": 1,
                        "user": 3,
                        "destination": "Nairobi",
                        "start_date": "2025-07-10",
                        "end_date": "2025-07-15",
                        "status": "pending",
                        "created_at": "2025-06-30T15:00:00Z"
                    },
                    response_only=True
                )
            ]
        )
    }
)
class BookingViewSet(mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        request=BookingSerializer,
        responses=BookingSerializer,
        tags=["Booking"],
        description="Create a new booking for the authenticated user."
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

# ----------------------------
# Mint TrailProof (Post-booking action)
# ----------------------------
@extend_schema(
    request=None,
    responses={
        200: OpenApiResponse(
            description="Minting response",
            examples=[
                OpenApiExample(
                    name="MintTrailProofResponse",
                    value={
                        "message": "Minting request accepted (placeholder)",
                        "user": "0x123abc456def..."
                    }
                )
            ]
        )
    },
    tags=["Booking"],
    description="Endpoint to trigger TrailProof SBT minting after a successful booking (placeholder for smart contract integration)"
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mint_trailproof(request):
    return Response({
        "message": "Minting request accepted (placeholder)",
        "user": request.user.wallet_address
    })
