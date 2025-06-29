
from django.contrib import admin
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

schema_view = get_schema_view(
   openapi.Info(
      title="NomadLink API",
      default_version='v1',
      description="API documentation for NomadLink hackathon backend",
      contact=openapi.Contact(
         name="Asile Ayuba (Backend Dev)", 
         email="asileayuba@gmail.com"
      ),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/bookings/', include('bookings.urls')),
    path('api/kyc/', include('kyc.urls')),
    path('schema-viewer/', include('schema_viewer.urls')),

    # Swagger routes
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)






