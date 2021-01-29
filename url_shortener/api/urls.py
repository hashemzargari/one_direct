from django.urls import path
from url_shortener.api import views as api_view

urlpatterns = [

    path('urls/', api_view.UrlListApiView.as_view(), name='list_urls'),
    path('urls/<pk>', api_view.UrlRetrieveUpdateDestroyApiView.as_view(), name='view_url'),
    path('urls/create/', api_view.UrlCreateApiView.as_view(), name='create_url'),

]
