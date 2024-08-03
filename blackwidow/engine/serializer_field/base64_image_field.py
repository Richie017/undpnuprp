import base64
import time
from random import choice
from string import ascii_uppercase

from django.core.files.base import ContentFile
from rest_framework import serializers

from blackwidow.core.models.file.imagefileobject import ImageFileObject

__author__ = 'Shamil on 10-Mar-16 12:12 PM'
__organization__ = 'FIS'


class Base64ImageField(serializers.Field):
    def to_representation(self, obj):
        return obj

    def to_internal_value(self, data):
        if data != '':
            base64_data = base64.b64decode(data)  # saving decoded image to database
            random_string = ''.join([choice(ascii_uppercase) for i in range(8)])
            current_time = int(time.time()) * 1000
            filename = "uploaded_image_%s_%s.png" % (current_time, random_string)
            image_object = ImageFileObject()
            image_object.file = ContentFile(base64_data, filename)
            image_object.name = filename
            image_object.save()
            self.context['request'].data[self.source] = image_object.pk
            return image_object.pk
        else:
            return 0

    @classmethod
    def string_to_base64(cls, string):
        return base64.b64encode(bytes(string, 'ascii'))

    @classmethod
    def base64_to_string(cls, base64_string):
        return base64.b64decode(base64_string)
