from django.urls import path, include
from rest_framework.routers import DefaultRouter
from url_shortener.api import views as api_view

router = DefaultRouter()
router.register(r'urls', api_view.UrlViewSet)

urlpatterns = [

    path('', include(router.urls)),
]
