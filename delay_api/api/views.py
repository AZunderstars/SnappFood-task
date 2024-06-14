from django.core import serializers
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django_redis import get_redis_connection
from django.db.models import Count
from django.utils import timezone
from .models import *
import json
import requests
import queue


url = "https://run.mocky.io/v3/122c2796-5df4-461c-ab75-87c1192b17f7"

default_minute_latency_to_add = 15


def get_new_arrive_time():
    try:
        response = requests.get(url)
        return response.json().get("new_arrive_time")

    except (requests.exceptions.RequestException, requests.exceptions.JSONDecodeError):
        return timezone.localtime(timezone.now() + timezone.timedelta(minutes=default_minute_latency_to_add))


def push_to_delay_queue(order):
    con = get_redis_connection("default")
    con.lpush('delay_queue', order.id)


def has_trip_on_the_way(order):
    return hasattr(order, "trip") and order.trip.status != "DELIVERED"


def pop_from_delay_queue():
    con = get_redis_connection("default")
    return con.rpop('delay_queue')


def is_delay_queue_empty():
    con = get_redis_connection("default")
    return con.llen('delay_queue') == 0


def get_order_from_delay_queue():
    if is_delay_queue_empty():
        raise queue.Empty
    order_id = pop_from_delay_queue()
    order = Order.objects.get(id=order_id)
    return order


@csrf_exempt
@require_POST
def delay_report_announce(request):
    try:
        body = json.loads(request.body)
        order = Order.objects.get(id=body["id"])
        if order.is_now_late_for_delivery():
            return HttpResponse('not late', status=400)
        if has_trip_on_the_way(order):
            if hasattr(order, "employee"):
                return HttpResponse('order is being examined by an employee', status=400)
            DelayReport.objects.create(order=order, action="RESCHEDULED")
            new_arrive_time = get_new_arrive_time()
            return JsonResponse({"new_arrive_time": new_arrive_time})
        else:
            DelayReport.objects.create(order=order, action="DELAY_QUEUED")
            push_to_delay_queue(order)
            return HttpResponse("queued to examine by an employee")

    except (json.decoder.JSONDecodeError, KeyError, Order.DoesNotExist):
        return HttpResponse('bad request', status=400)


@csrf_exempt
@require_GET
def get_delay_report_from_queue(request):
    try:
        body = json.loads(request.body)
        employee = Employee.objects.get(id=body["id"])
        if employee.working_on is not None:
            return HttpResponse('another order already assigned', status=400)
        order = get_order_from_delay_queue()
        employee.working_on = order
        employee.save()
        return HttpResponse(serializers.serialize('json', [order]), content_type='application/json')
    except (json.decoder.JSONDecodeError, KeyError, Employee.DoesNotExist, queue.Empty, Order.DoesNotExist):
        return HttpResponse('bad request', status=400)


@csrf_exempt
@require_GET
def get_vendors_delay_report(request):
    vendors = Vendor.objects \
        .annotate(num_delays=Count("order__delay_report"))\
        .order_by("-num_delays")
    data = serializers.serialize('json', vendors)
    return HttpResponse(data, content_type='application/json')
    # return JsonResponse(list(vendors.values()), safe=False)
