from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("api/monitors/", include("apps.monitors.urls")),
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.authentication.urls", namespace="authentication")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    
    path("api/v1/monitors/", include("apps.monitors.urls", namespace="monitors")),
]
