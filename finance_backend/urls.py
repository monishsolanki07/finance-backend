from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny

schema_view = get_schema_view(
    openapi.Info(
        title="Finance API",
        default_version='v1',
    ),
    public=True,
    permission_classes=[AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # API routes
    path('api/users/', include('users.urls')),
    path('api/records/', include('records.urls')),
    path('api/dashboard/', include('dashboard.urls')),

    # JWT token refresh (standalone)
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Swagger docs
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc'),
]