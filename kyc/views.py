from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone
from .models import KYC
from .serializers import KYCSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser

class KYCDetailCreateView(generics.RetrieveUpdateAPIView):
    serializer_class = KYCSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        kyc, _ = KYC.objects.get_or_create(user=self.request.user)
        return kyc

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


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
