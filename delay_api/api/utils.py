from django_redis import get_redis_connection
from django.utils import timezone
from .models import *
from .constants import *
import requests
import queue


def get_new_arrive_time():
    try:
        response = requests.get(NEW_ARRIVE_TIME_SERVICE_URL)
        return response.json().get(TIME_FIELD_IN_WEB_SERVICE)

    except (requests.exceptions.RequestException, requests.exceptions.JSONDecodeError):
        return timezone.localtime(timezone.now() + timezone.timedelta(minutes=DEFAULT_MINUTE_LATENCY_TO_ADD))


def push_to_delay_queue(value):
    con = get_redis_connection()
    con.lpush(DELAY_QUEUE, value)


def has_trip_on_the_way(order):
    return hasattr(order, "trip") and order.trip.status != "DELIVERED"


def pop_from_delay_queue():
    con = get_redis_connection()
    return con.rpop(DELAY_QUEUE)


def is_delay_queue_empty():
    con = get_redis_connection()
    return con.llen(DELAY_QUEUE) == 0


def get_order_from_delay_queue():
    if is_delay_queue_empty():
        raise queue.Empty
    order_id = pop_from_delay_queue()
    order = Order.objects.get(id=order_id)
    return order


def does_order_have_delay_report(order):
    return DelayReport.objects.filter(order__id=order.id, action="DELAY_QUEUED").exists()
