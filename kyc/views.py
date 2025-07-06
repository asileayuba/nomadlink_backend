from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from .models import KYC, KYCReview
from .serializers import KYCSerializer
from django.contrib.auth import get_user_model

# Swagger utils
from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes
)

User = get_user_model()

# ----------------------------
# KYC GET & PUT (User Scope)
# ----------------------------
@extend_schema(
    methods=["GET", "PUT"],
    request=KYCSerializer,
    responses=KYCSerializer,
    tags=["KYC"],
    description="Authenticated users can retrieve or update their KYC Level 1 and Level 2 info",
    examples=[
        OpenApiExample(
            "KYC Submission Example",
            value={
                "full_name": "Asile Ayuba",
                "date_of_birth": "2000-06-28",
                "id_type": "passport",
                "id_document": None,
                "selfie_photo": None
            },
            request_only=True
        ),
        OpenApiExample(
            "KYC Response Example",
            value={
                "id": 5,
                "user": 12,
                "full_name": "Asile Ayuba",
                "date_of_birth": "2000-06-28",
                "id_type": "passport",
                "id_document": "http://example.com/id.pdf",
                "selfie_photo": "http://example.com/selfie.png",
                "review_status": "pending"
            },
            response_only=True
        )
    ]
)
class KYCDetailCreateView(generics.RetrieveUpdateAPIView):
    serializer_class = KYCSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        kyc, _ = KYC.objects.get_or_create(user=self.request.user)
        return kyc

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

# ----------------------------
# Admin Verifies or Rejects KYC (Using KYCReview model)
# ----------------------------
@extend_schema(
    request=OpenApiTypes.OBJECT,
    responses=OpenApiTypes.OBJECT,
    tags=["KYC"],
    description="Admin endpoint to verify or reject a user's KYC using KYCReview model",
    parameters=[
        OpenApiParameter(
            name="user_id",
            type=int,
            location=OpenApiParameter.PATH,
            required=True,
            description="ID of the user whose KYC is being reviewed"
        )
    ],
    examples=[
        OpenApiExample(
            "Approve Example",
            value={"review_status": "approved", "notes": "Looks good."},
            request_only=True
        ),
        OpenApiExample(
            "Reject Example",
            value={"review_status": "rejected", "notes": "Document is blurry."},
            request_only=True
        ),
        OpenApiExample(
            "Success Response",
            value={
                "message": "KYC reviewed",
                "user": "0x4551...a29a7a",
                "review_status": "approved",
                "verified": True
            },
            response_only=True
        )
    ]
)
@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def verify_kyc(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        kyc = KYC.objects.get(user=user)
    except (User.DoesNotExist, KYC.DoesNotExist):
        return Response({"error": "KYC not found"}, status=404)

    status_value = request.data.get("review_status")
    notes = request.data.get("notes", "")

    if status_value not in ["approved", "rejected"]:
        return Response({"error": "Invalid review_status"}, status=400)

    # Create or update review
    review, _ = KYCReview.objects.get_or_create(kyc=kyc)
    review.review_status = status_value
    review.reviewer = request.user
    review.notes = notes
    review.save()

    return Response({
        "message": "KYC reviewed",
        "user": user.wallet_address if hasattr(user, 'wallet_address') else user.username,
        "review_status": review.review_status,
        "verified": kyc.is_verified
    })

# ----------------------------
# Get Lightweight KYC Status
# ----------------------------
@extend_schema(
    responses=OpenApiTypes.OBJECT,
    tags=["KYC"],
    description="Returns current user's KYC status, review status, and verification status",
    examples=[
        OpenApiExample(
            "KYC Approved",
            value={
                "kyc_level": "level_2",
                "review_status": "approved",
                "is_verified": True
            }
        ),
        OpenApiExample(
            "No Submission",
            value={
                "kyc_level": None,
                "review_status": "not_submitted",
                "is_verified": False
            }
        )
    ]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_kyc_status(request):
    try:
        kyc = KYC.objects.get(user=request.user)
        return Response({
            "kyc_level": kyc.level,
            "review_status": kyc.review_status,
            "is_verified": kyc.is_verified
        })
    except KYC.DoesNotExist:
        return Response({
            "kyc_level": None,
            "review_status": "not_submitted",
            "is_verified": False
        })
