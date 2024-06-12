from django.db import models


class Vendor(models.Model):
    id = models.AutoField(primary_key=True)


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    vendor = models.ForeignKey(
        Vendor, on_delete=models.PROTECT, related_name="orders", related_query_name="order")
    register_time = models.DateTimeField(auto_now_add=True)
    delivery_time = models.PositiveIntegerField()
