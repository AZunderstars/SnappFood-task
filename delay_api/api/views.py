from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django_redis import get_redis_connection
from django.db.models import Count
from .models import *
import json
import requests

url = "https://run.mocky.io/v3/122c2796-5df4-461c-ab75-87c1192b17f7"


@csrf_exempt
@require_POST
def delay_report_announce(request):
    body = json.loads(request.body)
    if "id" not in body:
        return HttpResponse('bad parameters')
    if not Order.objects.filter(id=body["id"]).exists():
        return HttpResponse('no order')
    order = Order.objects.get(id=body["id"])
    if order.is_now_late_for_delivery:
        return HttpResponse('not late')
    if hasattr(order, "trip") and order.trip.status != "DELIVERED":
        try:
            response = requests.get(url, params=request.GET)
            if response.status_code == 200:
                return HttpResponse('Yay, it worked')
            else:
                return HttpResponse('oh no')
        except requests.exceptions.RequestException as e:
            return HttpResponse('exception')
        finally:
            DelayReport.objects.create(order=order, action="RESCHEDULED")
    else:
        con = get_redis_connection("default")
        con.lpush('delay_queue', 1)
        DelayReport.objects.create(order=order, action="DELAY_QUEUED")
        return HttpResponse('queued')


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
