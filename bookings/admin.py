from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'destination', 'start_date', 'end_date', 'status', 'created_at')
    search_fields = ('user__wallet_address', 'destination', 'status')
    list_filter = ('status', 'start_date', 'end_date')
