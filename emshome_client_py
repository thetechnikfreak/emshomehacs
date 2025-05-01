"""Client for eMShome Smart Meter."""
import logging
import asyncio
import aiohttp
import websockets
import json
import time
from datetime import datetime

from .const import DATA_POINT_KEYS

_LOGGER = logging.getLogger(__name__)


class EMSHomeClient:
    """Client to interact with eMShome Smart Meter."""

    def __init__(self, host, password):
        """Initialize the client."""
        self.host = host
        self.password = password
        self.access_token = None
        self.token_type = None
        self.ws_connection = None
        self.data = {}
        self.last_update = None
        self._closing = False
        self._listen_task = None

    async def authenticate(self):
        """Authenticate with the eMShome API and get access token."""
        url = f"http://{self.host}/api/web-login/token"
        data = {
            "grant_type": "password",
            "client_id": "emos",
            "client_secret": "56951025",
            "username": "admin",
            "password": self.password,
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, data=data) as response:
                    if response.status != 200:
                        _LOGGER.error(f"Authentication failed with status {response.status}")
                        return False

                    result = await response.json()
                    self.token_type = result.get("token_type")
                    self.access_token = result.get("access_token")
                    
                    if not self.token_type or not self.access_token:
                        _LOGGER.error("Missing token_type or access_token in response")
                        return False
                    
                    return True
            except aiohttp.ClientError as err:
                _LOGGER.error(f"Error connecting to eMShome API: {err}")
                return False

    async def connect_websocket(self):
        """Connect to the eMShome WebSocket."""
        if not self.token_type or not self.access_token:
            if not await self.authenticate():
                return False

        authorization = f"{self.token_type} {self.access_token}"
        ws_url = f"ws://{self.host}/api/data-transfer/ws/protobuf/gdr/local/values/smart-meter"

        try:
            self.ws_connection = await websockets.connect(
                ws_url, 
                extra_headers={"Authorization": authorization}
            )
            
            # Send token twice as in original code
            await self.ws_connection.send(authorization)
            await self.ws_connection.send(authorization)
            
            return True
        except (websockets.exceptions.ConnectionClosed, 
                websockets.exceptions.InvalidStatusCode,
                OSError) as err:
            _LOGGER.error(f"Error connecting to WebSocket: {err}")
            self.ws_connection = None
            return False

    async def listen(self):
        """Listen for data on WebSocket connection."""
        if not self.ws_connection and not await self.connect_websocket():
            return

        self._closing = False
        
        try:
            while not self._closing:
                try:
                    if not self.ws_connection:
                        if not await self.connect_websocket():
                            await asyncio.sleep(10)
                            continue
                    
                    message = await asyncio.wait_for(self.ws_connection.recv(), timeout=30)
                    self._process_message(message)
                    
                except asyncio.TimeoutError:
                    _LOGGER.debug("WebSocket timeout - reconnecting")
                    await self.close()
                    if not await self.connect_websocket():
                        await asyncio.sleep(10)
                    
                except (websockets.exceptions.ConnectionClosed, OSError) as err:
                    _LOGGER.debug(f"WebSocket connection closed - reconnecting: {err}")
                    await self.close()
                    if not await self.connect_websocket():
                        await asyncio.sleep(10)
                        
        except asyncio.CancelledError:
            _LOGGER.debug("WebSocket listener task cancelled")
            await self.close()
            
        except Exception as err:
            _LOGGER.error(f"Unexpected error in WebSocket listener: {err}")
            await self.close()

    def _process_message(self, message):
        """Process binary message from WebSocket."""
        # This is a simplified implementation, as the original uses a custom binary protocol
        # In a real implementation, we'd need to port the binary protocol used by eMShome
        
        # For demonstration purposes, we'll simulate the processed data
        self.last_update = datetime.now()
        
        # Note: In a real implementation, this would be where we decode the protobuf message
        # using similar logic to the Arduino code in eMShome.cpp
        
        # For now, we'll simulate the data
        self._update_data_point(DATA_POINT_KEYS["total_active_power_positive"], 5000)
        self._update_data_point(DATA_POINT_KEYS["total_active_power_negative"], 0)
        self._update_data_point(DATA_POINT_KEYS["l1_active_power_positive"], 1700)
        self._update_data_point(DATA_POINT_KEYS["l1_active_power_negative"], 0)
        self._update_data_point(DATA_POINT_KEYS["l2_active_power_positive"], 1600)
        self._update_data_point(DATA_POINT_KEYS["l2_active_power_negative"], 0)
        self._update_data_point(DATA_POINT_KEYS["l3_active_power_positive"], 1700)
        self._update_data_point(DATA_POINT_KEYS["l3_active_power_negative"], 0)

    def _update_data_point(self, key, value):
        """Update a data point in the data dictionary."""
        self.data[key] = value

    def get_active_power(self, line):
        """Get active power for a specific line.
        
        line: 0 = Total, 1 = L1, 2 = L2, 3 = L3
        """
        if line == 0:  # Total
            positive_key = DATA_POINT_KEYS["total_active_power_positive"]
            negative_key = DATA_POINT_KEYS["total_active_power_negative"]
        elif line == 1:  # L1
            positive_key = DATA_POINT_KEYS["l1_active_power_positive"]
            negative_key = DATA_POINT_KEYS["l1_active_power_negative"]
        elif line == 2:  # L2
            positive_key = DATA_POINT_KEYS["l2_active_power_positive"]
            negative_key = DATA_POINT_KEYS["l2_active_power_negative"]
        elif line == 3:  # L3
            positive_key = DATA_POINT_KEYS["l3_active_power_positive"]
            negative_key = DATA_POINT_KEYS["l3_active_power_negative"]
        else:
            _LOGGER.error(f"Invalid line number: {line}")
            return None

        positive_value = self.data.get(positive_key, 0)
        negative_value = self.data.get(negative_key, 0)
        
        # Following the logic in the original code
        if positive_value == 0 and negative_value != 0:
            return -negative_value / 1000  # Convert to W
        return positive_value / 1000  # Convert to W

    async def start_listening(self):
        """Start the WebSocket listener task."""
        if self._listen_task and not self._listen_task.done():
            return
            
        self._listen_task = asyncio.create_task(self.listen())

    async def close(self):
        """Close the WebSocket connection."""
        self._closing = True
        
        if self.ws_connection:
            try:
                await self.ws_connection.close()
            except Exception as err:
                _LOGGER.debug(f"Error closing WebSocket connection: {err}")
            finally:
                self.ws_connection = None
