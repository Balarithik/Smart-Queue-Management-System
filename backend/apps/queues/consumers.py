import json
from channels.generic.websocket import AsyncWebsocketConsumer


class QueueConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.service_id = self.scope["url_route"]["kwargs"]["service_id"]
        self.group_name = f"service_{self.service_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def queue_message(self, event):
        await self.send(
            text_data=json.dumps(
                {"type": event["event_type"], "timestamp": event["timestamp"], "payload": event["payload"]}
            )
        )
