from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.db.models import Count
from .serializers import *
from .models import *
from .utils import *
import json
import queue


@csrf_exempt
@require_POST
def delay_report_announce(request):
    try:
        body = json.loads(request.body)
        order = Order.objects.get(id=body["id"])
        if not order.is_now_late_for_delivery():
            return HttpResponse('not late', status=400)
        if has_trip_on_the_way(order):
            DelayReport.objects.create(order=order, action="RESCHEDULED")
            new_arrive_time = get_new_arrive_time()
            return JsonResponse({"new_arrive_time": new_arrive_time})
        else:
            if DelayReport.objects.filter(order__id=order.id, action="DELAY_QUEUED").exists():
                return HttpResponse('order is in queue', status=400)
            DelayReport.objects.create(order=order, action="DELAY_QUEUED")
            push_to_delay_queue(order.id)
            return HttpResponse("queued to be examined by an employee")

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
        return JsonResponse(OrderSerializer(order).data, safe=False)
    except (json.decoder.JSONDecodeError, KeyError, Employee.DoesNotExist, queue.Empty, Order.DoesNotExist):
        return HttpResponse('bad request', status=400)


@csrf_exempt
@require_GET
def get_vendors_delay_report(request):
    vendors = Vendor.objects \
        .annotate(num_delays=Count("order__delay_report"))\
        .order_by("-num_delays")
    return JsonResponse(VendorSerializer(vendors, many=True).data, safe=False)
