from django.contrib.auth.models import User

from rest_framework import serializers

__author__ = 'Tareq'


class UserSerializer(serializers.ModelSerializer):
    def is_valid(self, raise_exception=False):
        return True

    def update(self, instance, attrs):
        instance = super().update(instance, attrs)
        if attrs.get('password', None):
            instance.set_password(attrs.get('password'))
        instance.save()
        return instance

    def create(self, attrs):
        obj = super().create(attrs)
        obj.set_password("as1234")
        obj.save()
        return obj

    def validate_username(self, value):
        """
        Check duplicate entry for username
        """
        _user = User.objects.filter(username__iexact=value)
        if _user.exists():
            # raise APIException( 'Cannot login with provided credentials.')
            raise serializers.ValidationError("Username already exists.")

        return value

    class Meta:
        model = User
        fields = ('id', 'username')
        read_only_fields = ('id',)
