from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpRequest, HttpResponse
from django_redis import get_redis_connection
from .models import *
import json
import requests

url = "https://run.mocky.io/v3/122c2796-5df4-461c-ab75-87c1192b17f7"


@csrf_exempt
@require_POST
def delay_report_announce(request: HttpRequest):
    body = json.loads(request.body)
    if "id" not in body or len(body.keys()) != 1:
        return HttpResponse('bad parameters')
    if (not Order.objects.filter(id=body["id"]).exists()):
        return HttpResponse('no order')
    order = Order.objects.get(id=body["id"])
    if (hasattr(order, "trip") and order.trip.status != "DELIVERED"):
        try:
            response = requests.get(url, params=request.GET)
            if (response.status_code == 200):
                return HttpResponse('Yay, it worked')
            else:
                return HttpResponse('oh no')
        except requests.exceptions.RequestException as e:
            return HttpResponse('exception')
    else:
        con = get_redis_connection("default")
        con.lpush('delay_queue', 1)
        return HttpResponse('queued')
