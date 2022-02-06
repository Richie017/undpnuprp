from rest_framework import serializers
from rest_framework.authtoken.serializers import AuthTokenSerializer

__author__ = 'Mahmud'


class BWAuthTokenSerializer(AuthTokenSerializer):
    device_id = serializers.CharField(max_length=200, required=False, default='')