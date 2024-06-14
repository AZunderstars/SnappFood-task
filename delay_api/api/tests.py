from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIRequestFactory
from .models import *
from .views import *


class OrderModelTestCase(TestCase):
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


class VendorsDelayReportTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.v1 = Vendor.objects.create()
        self.v2 = Vendor.objects.create()
        self.v3 = Vendor.objects.create()
        self.o1 = Order.objects.create(vendor=self.v1, delivery_time=15)
        self.o2 = Order.objects.create(vendor=self.v2, delivery_time=15)

    def test_vendors_delay_report_api(self):
        DelayReport.objects.create(order=self.o1)
        DelayReport.objects.create(order=self.o1)
        DelayReport.objects.create(order=self.o1)
        DelayReport.objects.create(order=self.o2)
        request = self.factory.get('/api/3/')
        response = get_vendors_delay_report(request)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, json.dumps(
            [{"id": self.v1.id, "num_delays": 3}, {"id": self.v2.id, "num_delays": 1}, {"id": self.v3.id, "num_delays": 0}]))
        
    
