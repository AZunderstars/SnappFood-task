from rest_framework import serializers
from .models import *


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'vendor', 'register_time', 'delivery_time']


class VendorSerializer(serializers.ModelSerializer):
    num_delays = serializers.IntegerField()
    class Meta:
        model = Vendor
        fields = ['id', 'num_delays']
