from django.urls import path

from . import views

urlpatterns = [
    path("", views.delay_report_announce, name="delay_report_announce"),
]
