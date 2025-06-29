from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from accounts.models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Booking

class BookingTests(APITestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            wallet_address="0xbooker456def123",
            username="bookingtest",
            password="TestBooking123"
        )
        self.token = str(RefreshToken.for_user(self.user).access_token)
        self.auth_header = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}

    def test_create_booking(self):
        url = reverse('bookings-list')
        data = {
            "destination": "Nairobi",
            "start_date": "2025-07-01",
            "end_date": "2025-07-05",
            "status": "pending"
        }
        response = self.client.post(url, data, **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.count(), 1)

    def test_get_user_bookings(self):
        Booking.objects.create(
            user=self.user,
            destination="Lagos",
            start_date="2025-07-02",
            end_date="2025-07-04",
            status="confirmed"
        )
        url = reverse('bookings-list')
        response = self.client.get(url, **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
