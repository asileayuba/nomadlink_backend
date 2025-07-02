from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)
from emergency.views import emergency_dashboard

urlpatterns = [
    path('', include('core.urls')),
    path('admin/emergency-dashboard/', emergency_dashboard, name='emergency-dashboard'),
    path('admin/', admin.site.urls),

    # App APIs
    path('api/auth/', include('accounts.urls')),
    path('api/bookings/', include('bookings.urls')),
    path('api/kyc/', include('kyc.urls')),
    path('api/emergency/', include('emergency.urls')),



    # DRF Spectacular - OpenAPI schema and docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 = 'core.views.custom_404'
