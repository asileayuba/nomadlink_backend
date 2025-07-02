from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .models import EmergencyAlert
from .serializers import EmergencyAlertSerializer
from drf_spectacular.utils import extend_schema, OpenApiTypes
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


import logging

logger = logging.getLogger(__name__)



@extend_schema(
    request=EmergencyAlertSerializer,
    responses=EmergencyAlertSerializer,
    tags=["Emergency"],
    description="Trigger an emergency alert tied to the authenticated user"
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_emergency(request):
    serializer = EmergencyAlertSerializer(data=request.data)
    if serializer.is_valid():
        alert = serializer.save(user=request.user)
        
        # Send to WebSocket
        channel_layer = get_channel_layer()
        alert_data = EmergencyAlertSerializer(alert).data

        async_to_sync(channel_layer.group_send)(
            "emergency_alerts",
            {
                "type": "send.alert",
                "data": {
                    "type": "new_alert",
                    "alert": alert_data
                }
            }
        )

        # Send user confirmation email
        subject = "Emergency Alert Received"
        message = render_to_string("emails/emergency_alert_user.html", {
            "user": request.user,
            "alert": alert,
        })

        send_mail(
            subject,
            None,
            settings.DEFAULT_FROM_EMAIL,
            [request.user.email],
            html_message=message,
            fail_silently=False
        )

        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@extend_schema(
    responses=EmergencyAlertSerializer(many=True),
    tags=["Emergency"],
    description="List authenticated user's emergency alerts (filter with ?resolved=true|false)"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_emergencies(request):
    resolved_param = request.GET.get('resolved')
    alerts = EmergencyAlert.objects.filter(user=request.user)

    if resolved_param is not None:
        is_resolved = resolved_param.lower() == 'true'
        alerts = alerts.filter(is_resolved=is_resolved)

    alerts = alerts.order_by('-triggered_at')
    serializer = EmergencyAlertSerializer(alerts, many=True)
    return Response(serializer.data)



@staff_member_required
def emergency_dashboard(request):
    alerts = EmergencyAlert.objects.all().order_by('-triggered_at')
    return render(request, 'emergency/dashboard.html', {'alerts': alerts})


@extend_schema(
    request=None,
    responses=EmergencyAlertSerializer,
    tags=["Emergency"],
    description="Mark an emergency alert as resolved (Admin only)."
)
@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def resolve_emergency(request, alert_id):
    """
    Marks the specified emergency alert as resolved.
    Only accessible by admin users. Sends WebSocket and email notifications.
    """
    try:
        alert = EmergencyAlert.objects.get(id=alert_id)
    except EmergencyAlert.DoesNotExist:
        return Response({"error": "Alert not found"}, status=status.HTTP_404_NOT_FOUND)

    if alert.is_resolved:
        return Response({"message": "Already resolved"}, status=status.HTTP_200_OK)

    alert.is_resolved = True
    alert.save()

    # Notify WebSocket of resolution
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "emergency_alerts",
            {
                "type": "send.alert",
                "data": {
                    "type": "alert_resolved",
                    "alert_id": alert.id
                }
            }
        )
    except Exception as e:
        logger.warning(f"WebSocket notification failed: {e}")

    # Send admin email
    try:
        subject = f"Emergency Resolved: {alert.user.wallet_address}"
        html = render_to_string("emails/emergency_resolved_admin.html", {
            "alert": alert
        })

        send_mail(
            subject=subject,
            message=None,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            html_message=html,
            fail_silently=False
        )
    except Exception as e:
        logger.warning(f"Email sending failed: {e}")

    serializer = EmergencyAlertSerializer(alert)
    return Response(serializer.data, status=status.HTTP_200_OK)


@staff_member_required
def websocket_test_view(request):
    return render(request, 'emergency/ws_test.html')