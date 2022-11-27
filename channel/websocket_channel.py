# from sanic import Sanic
# from sanic.websocket import WebSocketProtocol
# from sanic import Blueprint, response

# from typing import Any, Awaitable, Callable, Dict, Iterable, List, Optional, Text

# from rasa.core.channels.channel import InputChannel, OutputChannel, UserMessage, CollectingOutputChannel

# import json

# class WebsocketInputChannel(InputChannel):

#     def name(self) -> Text:
#         return "websocket_input_channel"

#     def blueprint(
#         self, on_new_message: Callable[[UserMessage], Awaitable[None]]
#     ) -> Blueprint:

#         sanic_blueprint = Blueprint("websocket_blueprint")

#         @sanic_blueprint.websocket('/channel')
#         async def feed(request, ws):

#             output_channel = WebSocketOutputChannel(ws)

#             while True:
#                 raw_request = await ws.recv()
#                 request = json.loads(raw_request)
                
#                 sender_id = request["id"]
#                 text = request["text"]

#                 input_channel = self.name()
#                 metadata = self.get_metadata(request)

#                 await on_new_message(
#                     UserMessage(
#                         text,
#                         output_channel,
#                         sender_id,
#                         input_channel=input_channel,
#                         metadata=metadata,
#                     )
#                 )
            

#         return sanic_blueprint


# class WebSocketOutputChannel(OutputChannel):

#     def __init__(self, ws) -> None:
#         self.ws = ws

#     def name(self) -> Text:
#         return "websocket_output_channel"

#     async def send_response(self, recipient_id, message):

#         # only support text responses right now over websocket

#         response = {
#             "id": recipient_id,
#             "text": message.get("text")
#         }

#         await self.ws.send(json.dumps(response))




import logging
import json
from typing import Any, Awaitable, Callable, Dict, Iterable, List, Optional, Text

from rasa.core.channels.channel import InputChannel, OutputChannel, UserMessage, CollectingOutputChannel
import rasa.shared.utils.io
from sanic import Blueprint, response
from sanic.request import Request
# WebSocket
import asyncio
import websockets
# mongodb
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)


class WebSocketClient():

    def __init__(self, on_new_message: Callable[[UserMessage], Awaitable[Any]]):
        self.on_new_message = on_new_message

    async def connect(self):
        '''
            Connecting to webSocket server
            websockets.client.connect returns a WebSocketClientProtocol, which is used to send and receive messages
        '''
        try:
            self.connection = await websockets.client.connect('ws://192.168.1.72:4000/chat')
            if self.connection.open:
                # Ask to subscribe to messages
                await self.sendMessage(json.dumps({"event": "rasa_sub"}))
                return self.connection
        except ConnectionRefusedError:
            await asyncio.sleep(5)
            await self.connect()

    async def sendMessage(self, message):
        '''
            Sending message to webSocket server
        '''
        await self.connection.send(message)

    async def receiveMessage(self):
        '''
            Receiving all server messages and handling them
        '''
        while True:
            try:
                message = await self.connection.recv()
                message = json.loads(str(message))

                if message['event'] == 'user_message':
                    id = message['data']['client_id']
                    text = message['data']['message']

                    output = WebSocketOutput(self.connection)
                    user_message = UserMessage(
                        text, output, id, input_channel="websockets"
                    )
                    await self.on_new_message(user_message)
            except websockets.exceptions.ConnectionClosed:
                pass
                # await self.connect()
                # break

    async def heartbeat(self):
        '''
        Sending heartbeat to server every 5 seconds
        Ping - pong messages to verify connection is alive
        '''
        while True:
            try:
                await self.sendMessage(json.dumps({"event": "ping"}))
                await asyncio.sleep(5)
            except websockets.exceptions.ConnectionClosed:
                print('Websocket closed. Opening again...')
                await self.connect()
                # break


class WebSocketOutput(OutputChannel):
    @classmethod
    def name(cls) -> Text:
        return "websocket"

    def __init__(self, connection) -> None:
        self.connection = connection

    async def _send_message(self, id: Text, response: Any) -> None:
        """Sends a message to the recipient using the bot event."""
        await self.connection.send(json.dumps({"event": "bot_message", "id": id, "data": response}))

    async def send_text_message(
        self, recipient_id: Text, text: Text, **kwargs: Any
    ) -> None:
        """Send a message through this channel."""

        for message_part in text.strip().split("\n\n"):
            await self._send_message(recipient_id, {"text": message_part})

    async def send_image_url(
        self, recipient_id: Text, image: Text, **kwargs: Any
    ) -> None:
        """Sends an image to the output"""

        message = {"image": image}
        await self._send_message(recipient_id, message)

    async def send_text_with_buttons(
        self,
        recipient_id: Text,
        text: Text,
        buttons: List[Dict[Text, Any]],
        **kwargs: Any,
    ) -> None:
        """Sends buttons to the output."""

        # split text and create a message for each text fragment
        # the `or` makes sure there is at least one message we can attach the quick
        # replies to
        message_parts = text.strip().split("\n\n") or [text]
        messages = [{"text": message, "quick_replies": []}
                    for message in message_parts]

        # attach all buttons to the last text fragment
        for button in buttons:
            messages[-1]["quick_replies"].append(
                {
                    "content_type": "text",
                    "title": button["title"],
                    "payload": button["payload"],
                }
            )

        for message in messages:
            await self._send_message(recipient_id, message)

    async def send_custom_json(
        self, recipient_id: Text, json_message: Dict[Text, Any], **kwargs: Any
    ) -> None:
        """Sends custom json to the output"""

        await self._send_message(recipient_id, json_message)

    async def send_elements(
        self, recipient_id: Text, elements: Iterable[Dict[Text, Any]], **kwargs: Any
    ) -> None:
        """Sends elements to the output."""

        for element in elements:
            message = {
                "attachment": {
                    "type": "template",
                    "payload": {"template_type": "generic", "elements": element},
                }
            }

            await self._send_message(recipient_id, message)

    async def send_attachment(
        self, recipient_id: Text, attachment: Dict[Text, Any], **kwargs: Any
    ) -> None:
        """Sends an attachment to the user."""
        await self._send_message(recipient_id, {"attachment": attachment})


class WebSocketInput(InputChannel):
    """A websocket input channel."""

    @classmethod
    def name(cls) -> Text:
        return "websockets"

    def __init__(
        self,
    ):
        pass

    def blueprint(
        self, on_new_message: Callable[[UserMessage], Awaitable[Any]]
    ) -> Blueprint:
        ws_server_webhook = Blueprint("websocket_webhook")

        @ws_server_webhook.listener('after_server_start')
        async def setup_db(app, loop):
            app.ws = WebSocketClient(on_new_message)
            # Start connection and get client connection protocol
            await asyncio.gather(app.ws.connect())
            # Start listener and heartbeat
            heart_task = asyncio.create_task(app.ws.heartbeat())
            message_task = asyncio.create_task(
                app.ws.receiveMessage())

            await heart_task
            await message_task

        @ws_server_webhook.websocket('/')
        async def health(_: Request, ws) -> None:
            while True:
                logger.debug("HEALTH RUNNING")
                await ws.send("Health is good from rasa")
                return "HEALTH GOOD FROM RASA"

        @ws_server_webhook.websocket('/websocket')
        async def handle_message(request, ws):
            print('hi')

        return ws_server_webhook