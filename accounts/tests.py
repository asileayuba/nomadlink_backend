from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from accounts.models import CustomUser

class AuthTests(APITestCase):

    def test_wallet_user_registration(self):
        url = reverse('register')
        data = {
            "wallet_address": "0x123abc456def7890",
            "username": "walletuser",
            "password": "StrongPass123",
            "email": "optional@example.com"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CustomUser.objects.filter(wallet_address=data["wallet_address"]).exists())

    def test_wallet_user_login(self):
        CustomUser.objects.create_user(
            wallet_address="0x123login789def456",
            username="logintest",
            email="logintest@example.com",
            password="TestLogin123"
        )
        url = reverse('login')
        data = {
            "wallet_address": "0x123login789def456",
            "password": "TestLogin123"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
