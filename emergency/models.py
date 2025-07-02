from django.db import models
from accounts.models import CustomUser

class EmergencyAlert(models.Model):
    ALERT_TYPE_CHOICES = [
        ('medical', 'Medical'),
        ('threat', 'Threat'),
        ('accident', 'Accident'),
        ('lost', 'Lost'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="emergencies")
    message = models.CharField(max_length=255, blank=True, null=True)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES, default='other')
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    is_resolved = models.BooleanField(default=False)
    triggered_at = models.DateTimeField(auto_now_add=True)
