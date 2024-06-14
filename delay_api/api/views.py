from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django_redis import get_redis_connection
from django.db.models import Count
from django.utils import timezone
from .models import *
import json
import requests

url = "https://run.mocky.io/v3/122c2796-5df4-461c-ab75-87c1192b17f7"


def get_new_arrive_time():
    try:
        response = requests.get(url)
        return response.json().get("new_arrive_time")

    except (requests.exceptions.RequestException, requests.exceptions.JSONDecodeError):
        return timezone.localtime(timezone.now() + timezone.timedelta(minutes=15))


def push_to_delay_queue(order):
    con = get_redis_connection("default")
    con.lpush('delay_queue', order.id)


def has_trip_on_the_way(order):
    return hasattr(order, "trip") and order.trip.status != "DELIVERED"


@csrf_exempt
@require_POST
def delay_report_announce(request):
    try:
        body = json.loads(request.body)
        order = Order.objects.get(id=body["id"])
        if order.is_now_late_for_delivery():
            return HttpResponse('not late', status=400)
        if has_trip_on_the_way(order):
            new_arrive_time = get_new_arrive_time()
            DelayReport.objects.create(order=order, action="RESCHEDULED")
            return HttpResponse({"new_arrive_time": new_arrive_time})
        else:
            DelayReport.objects.create(order=order, action="DELAY_QUEUED")
            push_to_delay_queue(order)

    except (json.decoder.JSONDecodeError, Order.DoesNotExist, KeyError):
        pass


@csrf_exempt
@require_GET
def get_delay_report_from_queue(request):
    body = json.loads(request.body)
    if "id" not in body:
        return HttpResponse('bad parameters')
    con = get_redis_connection("default")
    id = con.rpop('delay_queue')
    return HttpResponse(id)


@csrf_exempt
@require_GET
def get_vendors_delay_report(request):
    vendors = Vendor.objects \
        .annotate(num_delays=Count("order__delay_report"))\
        .order_by("-num_delays")
    return JsonResponse(list(vendors.values()), safe=False)
