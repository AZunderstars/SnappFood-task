from django.db import models


class Vendor(models.Model):
    id = models.AutoField(primary_key=True)


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    vendor = models.ForeignKey(
        Vendor, on_delete=models.PROTECT, related_name="orders", related_query_name="order")
    register_time = models.DateTimeField(auto_now_add=True)
    delivery_time = models.PositiveIntegerField()


class Trip(models.Model):
    class Statuses(models.TextChoices):
        ASSIGNED = "ASSIGNED"
        AT_VENDOR = "AT_VENDOR"
        PICKED = "PICKED"
        DELIVERED = "DELIVERED"
    order = models.OneToOneField(
        Order, primary_key=True, on_delete=models.CASCADE, related_name="trip")
    status = models.CharField(max_length=50, choices=Statuses)
