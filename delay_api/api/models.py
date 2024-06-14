from django.db import models
from datetime import datetime, timedelta


class Vendor(models.Model):
    id = models.AutoField(primary_key=True)


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    vendor = models.ForeignKey(
        Vendor, on_delete=models.PROTECT, related_name="orders", related_query_name="order")
    register_time = models.DateTimeField(auto_now_add=True)
    delivery_time = models.PositiveIntegerField()

    def is_now_late_for_delivery(self):
        now = datetime.now()
        delivery_deadline = self.register_time + timedelta(minutes=self.delivery_time)
        return delivery_deadline > now

class Trip(models.Model):
    class Statuses(models.TextChoices):
        ASSIGNED = "ASSIGNED"
        AT_VENDOR = "AT_VENDOR"
        PICKED = "PICKED"
        DELIVERED = "DELIVERED"

    order = models.OneToOneField(
        Order, primary_key=True, on_delete=models.CASCADE, related_name="trip")
    status = models.CharField(max_length=50, choices=Statuses)


class DelayReport(models.Model):
    class Actions(models.TextChoices):
        DELAY_QUEUED = "DELAY_QUEUED"
        RESCHEDULED = "RESCHEDULED"

    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE,
                              related_name="delay_reports", related_query_name="delay_report")
    action = models.CharField(max_length=50, choices=Actions)


class Employee(models.Model):
    id = models.AutoField(primary_key=True)
