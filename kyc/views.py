from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from .models import KYC
from .serializers import KYCSerializer

# Swagger utils
from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes
)

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
                "id_document": "http://example.com/media/kyc/documents/id.pdf",
                "id_document_file_type": ".pdf",
                "id_document_file_size": 102394,
                "selfie_photo": "http://example.com/media/kyc/selfies/selfie.png",
                "selfie_file_type": ".png",
                "selfie_file_size": 204801,
                "level": "level_2",
                "review_status": "pending",
                "is_verified": False,
                "submitted_at": "2025-06-30T18:30:00Z",
                "reviewed_at": None
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
# Admin Verifies or Rejects KYC
# ----------------------------
@extend_schema(
    request=OpenApiTypes.OBJECT,
    responses=OpenApiTypes.OBJECT,
    tags=["KYC"],
    description="Admin endpoint to verify or reject a user's KYC submission by user ID",
    parameters=[
        OpenApiParameter(
            name="user_id",
            type=int,
            location=OpenApiParameter.PATH,
            required=True,
            description="ID of the user whose KYC you want to verify"
        )
    ],
    examples=[
        OpenApiExample(
            "Approve KYC Example",
            value={"review_status": "approved"},
            request_only=True
        ),
        OpenApiExample(
            "Reject KYC Example",
            value={"review_status": "rejected"},
            request_only=True
        ),
        OpenApiExample(
            "Success Response",
            value={
                "message": "KYC reviewed",
                "user": "0x45517BeeFE934Ca1041F9E05f799184a32A29a7a",
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
        kyc = KYC.objects.get(user__id=user_id)
    except KYC.DoesNotExist:
        return Response({"error": "KYC not found"}, status=404)

    status_value = request.data.get('review_status')
    if status_value not in ['approved', 'rejected']:
        return Response({"error": "Invalid review_status"}, status=400)

    kyc.review_status = status_value
    kyc.is_verified = True if status_value == 'approved' else False
    kyc.reviewed_at = timezone.now()
    kyc.save()

    return Response({
        "message": "KYC reviewed",
        "user": kyc.user.wallet_address,
        "review_status": kyc.review_status,
        "verified": kyc.is_verified
    })

# ----------------------------
# Get Lightweight KYC Status
# ----------------------------
@extend_schema(
    responses=OpenApiTypes.OBJECT,
    tags=["KYC"],
    description="Returns the current user's KYC level, review status, and verification flag",
    examples=[
        OpenApiExample(
            "KYC Status Response",
            value={
                "kyc_level": "level_2",
                "review_status": "approved",
                "is_verified": True
            },
            response_only=True
        ),
        OpenApiExample(
            "Unsubmitted User Response",
            value={
                "kyc_level": None,
                "review_status": "not_submitted",
                "is_verified": False
            },
            response_only=True
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
