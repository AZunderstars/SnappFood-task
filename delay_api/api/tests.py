from django.test import TestCase
from django.utils import timezone
from .models import *


class OrderTestCase(TestCase):
    def setUp(self):
        vendor = Vendor.objects.create()
        self.late_order = Order.objects.create(vendor=vendor, delivery_time=5)
        past_time = timezone.now()-timezone.timedelta(minutes=15)
        self.late_order.register_time = past_time
        self.late_order.save(update_fields=['register_time'])
        self.not_late_order = Order.objects.create(
            vendor=vendor, delivery_time=20)

    def test_is_now_late_for_delivery(self):
        self.assertEqual(self.late_order.is_now_late_for_delivery(), True)
        self.assertEqual(self.not_late_order.is_now_late_for_delivery(), False)

    