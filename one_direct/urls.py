from django.contrib import admin
from django.urls import re_path, path, include
from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from url_shortener.api import views as api_view

schema_view = get_schema_view(
    openapi.Info(
        title="One-Direct API",
        default_version='v1',
        description="Welcome to One-Direct API",
        terms_of_service="",
        contact=openapi.Contact(email="hashemzargari@gmail.com"),
        license=openapi.License(name="One-Direct API"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # admin
    path('admin/', admin.site.urls),

    # redirect endpoint
    path('r/<str:short_version>/', api_view.redirect_client),

    # api endpoints
    path('api/v1/', include('url_shortener.api.urls')),

    # documents
    re_path(r'^doc(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('doc/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0),
         name='schema-redoc'),
]
