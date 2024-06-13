from django.urls import path

from . import views

urlpatterns = [
    path("1/", views.delay_report_announce, name="delay_report_announce"),
    path("2/", views.get_delay_report_from_queue, name="get_delay_report_from_queue"),
]
