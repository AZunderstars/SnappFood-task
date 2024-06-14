from django_redis import get_redis_connection
from django.utils import timezone
from .models import *
import requests
import queue

new_arrive_time_service_url = "https://run.mocky.io/v3/122c2796-5df4-461c-ab75-87c1192b17f7"

default_minute_latency_to_add = 15


def get_new_arrive_time():
    try:
        response = requests.get(new_arrive_time_service_url)
        return response.json().get("new_arrive_time")

    except (requests.exceptions.RequestException, requests.exceptions.JSONDecodeError):
        return timezone.localtime(timezone.now() + timezone.timedelta(minutes=default_minute_latency_to_add))


def push_to_delay_queue(value):
    con = get_redis_connection("default")
    con.lpush('delay_queue', value)


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
