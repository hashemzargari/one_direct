from rest_framework import serializers
from url_shortener import models


class UrlSerializer(serializers.ModelSerializer):
    redirect_count = serializers.IntegerField(read_only=True)
    short_version = serializers.CharField(read_only=True)

    class Meta:
        model = models.Url
        fields = '__all__'


class VisitUrlSerializer(serializers.ModelSerializer):
    url = serializers.CharField(read_only=True)
    client_browser = serializers.CharField(read_only=True)
    client_device = serializers.CharField(read_only=True)
    client_ip = serializers.CharField(read_only=True)

    class Meta:
        model = models.VisitUrl
        fields = '__all__'
