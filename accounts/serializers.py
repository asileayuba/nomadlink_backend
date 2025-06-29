from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import authenticate

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    class Meta:
        model = CustomUser
        fields = ['wallet_address', 'username', 'email', 'password']
        extra_kwargs = {'email': {'required': False}}

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)

class LoginSerializer(serializers.Serializer):
    wallet_address = serializers.CharField()  # Can rename to 'username'
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['wallet_address'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        return user
