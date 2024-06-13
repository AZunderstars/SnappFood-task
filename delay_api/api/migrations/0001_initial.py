# Generated by Django 5.0.6 on 2024-06-13 22:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Employee",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("register_time", models.DateTimeField(auto_now_add=True)),
                ("delivery_time", models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="Vendor",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name="Trip",
            fields=[
                (
                    "order",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        related_name="trip",
                        serialize=False,
                        to="api.order",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("ASSIGNED", "Assigned"),
                            ("AT_VENDOR", "At Vendor"),
                            ("PICKED", "Picked"),
                            ("DELIVERED", "Delivered"),
                        ],
                        max_length=50,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="DelayReport",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "action",
                    models.CharField(
                        choices=[
                            ("DELAY_QUEUED", "Delay Queued"),
                            ("RESCHEDULED", "Rescheduled"),
                        ],
                        max_length=50,
                    ),
                ),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="delay_reports",
                        related_query_name="delay_report",
                        to="api.order",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="order",
            name="vendor",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="orders",
                related_query_name="order",
                to="api.vendor",
            ),
        ),
    ]
