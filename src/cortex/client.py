from autobahn.twisted.websocket import connectWS
from cortex.clientFactory import CortexClientFactory

"""
 Class for setting up the factory and init additional info for connection
"""
class CortexClient:
    def __init__(self, receiver, url="wss://localhost:6868"):
        factory = CortexClientFactory(url, receiver)
        connectWS(factory)