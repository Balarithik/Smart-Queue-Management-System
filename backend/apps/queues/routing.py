from django.urls import re_path
from .consumers import QueueConsumer

websocket_urlpatterns = [
    re_path(r"ws/queues/(?P<service_id>\d+)/$", QueueConsumer.as_asgi()),
]
