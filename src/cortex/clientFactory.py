import os
from autobahn.twisted.websocket import WebSocketClientFactory
from cortex.clientProtocol import CortexClientProtocol

"""
 Class for twisted client factory (Twisted-based WebSocket client factories) to combine additional parameters
 of the client with the receiver
"""
class CortexClientFactory(WebSocketClientFactory):
    protocol = CortexClientProtocol

    # credentials to be used, assume from env 
    def __init__(self, url, receiver):
        WebSocketClientFactory.__init__(self, url)
        credentials = {
            "license": "",
            "client_id": os.environ.get("CLIENT_ID", "default_client_id"),
            "client_secret": os.environ.get("CLIENT_SECRET", "default_client_secret"),
            "debit": 100
        }
        self.receiver = receiver
        self.credentials = credentials