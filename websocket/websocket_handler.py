"""
WebSocket Handler - Real-time chat and streaming responses

Manages WebSocket connections, message routing, and streaming LLM responses.
"""

import asyncio
import json
import logging
from typing import Dict, Set, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """WebSocket message types"""
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    QUERY = "query"
    RESPONSE = "response"
    STREAMING = "streaming"
    ERROR = "error"
    STATUS = "status"


@dataclass
class WebSocketMessage:
    """WebSocket message structure"""
    type: str
    content: str = ""
    user_id: str = "anonymous"
    conversation_id: str = "default"
    chunk: str = ""
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()

    def dict(self) -> dict:
        return asdict(self)

    def json(self) -> str:
        return json.dumps(self.dict())


class WebSocketHandler:
    """
    Manages WebSocket connections for real-time chat.
    
    Features:
    - Connection pooling
    - Message routing
    - Streaming responses
    - Connection persistence
    - Error handling
    """

    def __init__(self, orchestrator=None):
        """
        Initialize WebSocket handler.
        
        Args:
            orchestrator: Optional TARS orchestrator for query processing
        """
        self.connections: Dict[str, Any] = {}
        self.user_conversations: Dict[str, Set[str]] = {}
        self.orchestrator = orchestrator
        self.message_queue: Dict[str, asyncio.Queue] = {}

    async def handle_connection(self, websocket, client_id: str):
        """
        Handle WebSocket connection lifecycle.
        
        Args:
            websocket: WebSocket connection object
            client_id: Unique client identifier
        """
        try:
            self.connections[client_id] = websocket
            self.message_queue[client_id] = asyncio.Queue()
            
            logger.info(f"Client connected: {client_id}")
            
            # Send welcome message
            await websocket.send(WebSocketMessage(
                type=MessageType.STATUS,
                content="Connected to TARS"
            ).json())

            # Process messages
            async for message in websocket:
                await self._process_message(client_id, message)

        except Exception as e:
            logger.error(f"WebSocket error for {client_id}: {e}")
        finally:
            await self._handle_disconnect(client_id)

    async def _process_message(self, client_id: str, message: str):
        """
        Process incoming WebSocket message.
        
        Args:
            client_id: Client identifier
            message: Raw message string
        """
        try:
            data = json.loads(message)
            msg_type = data.get('type', '')
            
            if msg_type == MessageType.CONNECT:
                await self._handle_connect(client_id, data)
            elif msg_type == MessageType.QUERY:
                await self._handle_query(client_id, data)
            else:
                logger.warning(f"Unknown message type: {msg_type}")
                
        except json.JSONDecodeError:
            await self._send_error(client_id, "Invalid JSON format")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await self._send_error(client_id, str(e))

    async def _handle_connect(self, client_id: str, data: dict):
        """
        Handle client connection initialization.
        
        Args:
            client_id: Client identifier
            data: Connection data
        """
        user_id = data.get('user_id', 'anonymous')
        
        if user_id not in self.user_conversations:
            self.user_conversations[user_id] = set()
        
        self.user_conversations[user_id].add(client_id)
        
        logger.info(f"User {user_id} connected with client {client_id}")

    async def _handle_query(self, client_id: str, data: dict):
        """
        Handle query message and stream response.
        
        Args:
            client_id: Client identifier
            data: Query data
        """
        try:
            query = data.get('content', '')
            user_id = data.get('user_id', 'anonymous')
            conversation_id = data.get('conversation_id', 'default')

            if not query:
                await self._send_error(client_id, "Empty query")
                return

            logger.info(f"Query from {user_id}: {query[:100]}")

            # If orchestrator available, use it
            if self.orchestrator:
                response = await self._process_with_orchestrator(
                    query, user_id, conversation_id
                )
            else:
                response = await self._process_simple(query)

            # Send response
            websocket = self.connections.get(client_id)
            if websocket:
                await websocket.send(WebSocketMessage(
                    type=MessageType.RESPONSE,
                    content=response,
                    user_id=user_id,
                    conversation_id=conversation_id
                ).json())

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            await self._send_error(client_id, str(e))

    async def _process_with_orchestrator(self, query: str, user_id: str, 
                                        conversation_id: str) -> str:
        """
        Process query using TARS orchestrator.
        
        Args:
            query: User query
            user_id: User identifier
            conversation_id: Conversation identifier
            
        Returns:
            Response string
        """
        try:
            # Call orchestrator (would be actual implementation)
            response = self.orchestrator.process_query(
                query=query,
                user_id=user_id,
                conversation_id=conversation_id
            )
            return str(response)
        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            return f"Error: {str(e)}"

    async def _process_simple(self, query: str) -> str:
        """
        Process query with simple echo (fallback).
        
        Args:
            query: User query
            
        Returns:
            Response string
        """
        # Simple fallback response
        return f"TARS Echo: {query}"

    async def _send_error(self, client_id: str, error_message: str):
        """
        Send error message to client.
        
        Args:
            client_id: Client identifier
            error_message: Error message
        """
        websocket = self.connections.get(client_id)
        if websocket:
            try:
                await websocket.send(WebSocketMessage(
                    type=MessageType.ERROR,
                    content=error_message
                ).json())
            except Exception as e:
                logger.error(f"Error sending error message: {e}")

    async def _handle_disconnect(self, client_id: str):
        """
        Handle client disconnection.
        
        Args:
            client_id: Client identifier
        """
        if client_id in self.connections:
            del self.connections[client_id]
        
        if client_id in self.message_queue:
            del self.message_queue[client_id]

        # Remove from user conversations
        for user_id, clients in list(self.user_conversations.items()):
            if client_id in clients:
                clients.discard(client_id)
                if not clients:
                    del self.user_conversations[user_id]

        logger.info(f"Client disconnected: {client_id}")

    async def broadcast(self, message: WebSocketMessage, 
                       user_id: str = None):
        """
        Broadcast message to all connected clients (optionally filtered by user).
        
        Args:
            message: Message to broadcast
            user_id: Optional user ID to filter clients
        """
        if user_id:
            clients = self.user_conversations.get(user_id, set())
        else:
            clients = self.connections.keys()

        for client_id in clients:
            websocket = self.connections.get(client_id)
            if websocket:
                try:
                    await websocket.send(message.json())
                except Exception as e:
                    logger.error(f"Error broadcasting to {client_id}: {e}")

    async def stream_response(self, client_id: str, response_chunks: list):
        """
        Stream response chunks to client.
        
        Args:
            client_id: Client identifier
            response_chunks: List of response chunks
        """
        websocket = self.connections.get(client_id)
        if not websocket:
            return

        try:
            for chunk in response_chunks:
                await websocket.send(WebSocketMessage(
                    type=MessageType.STREAMING,
                    chunk=chunk
                ).json())
                await asyncio.sleep(0.01)  # Small delay for streaming effect
        except Exception as e:
            logger.error(f"Error streaming response: {e}")

    def get_connection_count(self) -> int:
        """Get current number of connections."""
        return len(self.connections)

    def get_user_count(self) -> int:
        """Get current number of connected users."""
        return len(self.user_conversations)

    def get_connection_status(self) -> dict:
        """Get connection status information."""
        return {
            "connections": self.get_connection_count(),
            "users": self.get_user_count(),
            "timestamp": datetime.utcnow().isoformat()
        }
