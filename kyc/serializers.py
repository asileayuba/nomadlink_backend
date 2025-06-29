from rest_framework import serializers
from .models import KYC

class KYCSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYC
        fields = '__all__'
        read_only_fields = ['user', 'submitted_at', 'reviewed_at', 'is_verified', 'review_status', 'level']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get('request')
        if not request or not request.user.is_staff:
            rep.pop('review_status', None)
            rep.pop('reviewed_at', None)
            rep.pop('is_verified', None)
        return rep
