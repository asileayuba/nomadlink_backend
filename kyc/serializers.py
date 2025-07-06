from rest_framework import serializers
from .models import KYC

class KYCSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = KYC
        fields = '__all__'
        read_only_fields = [
            'user', 'submitted_at', 'reviewed_at',
            'is_verified', 'review_status', 'level',
        ]

    # Return username for better API readability
    def get_user(self, obj):
        return obj.user.username if hasattr(obj.user, 'username') else str(obj.user)

    # Hide review metadata from normal users
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get('request')
        if not request or not request.user.is_staff:
            rep.pop('review_status', None)
            rep.pop('reviewed_at', None)
            rep.pop('is_verified', None)
        return rep
