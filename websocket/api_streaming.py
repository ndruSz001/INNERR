"""
API Streaming - FastAPI WebSocket integration and streaming responses

Provides streaming endpoints for LLM responses and real-time data.
"""

import asyncio
import logging
from typing import AsyncGenerator, Optional
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)


class StreamingResponse:
    """
    Streaming response handler for FastAPI.
    
    Features:
    - Server-Sent Events (SSE)
    - Chunked streaming
    - Error handling
    - Stream cancellation
    """

    def __init__(self, generator: AsyncGenerator):
        """
        Initialize streaming response.
        
        Args:
            generator: Async generator yielding response chunks
        """
        self.generator = generator
        self.is_active = True

    async def stream(self) -> AsyncGenerator[str, None]:
        """
        Stream response chunks.
        
        Yields:
            Formatted response chunks
        """
        try:
            async for chunk in self.generator:
                if not self.is_active:
                    logger.info("Stream cancelled")
                    break
                
                # Format as Server-Sent Event
                if chunk:
                    yield f"data: {chunk}\n\n"
                    await asyncio.sleep(0.01)  # Small delay for streaming
                    
        except GeneratorExit:
            logger.info("Generator closed")
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"data: Error: {str(e)}\n\n"

    def cancel(self):
        """Cancel the stream."""
        self.is_active = False


class WebSocketStreaming:
    """
    WebSocket streaming utilities.
    
    Features:
    - Message buffering
    - Back-pressure handling
    - Connection management
    """

    @staticmethod
    async def stream_to_websocket(
        websocket: WebSocket,
        generator: AsyncGenerator[str, None],
        chunk_size: int = 50
    ):
        """
        Stream data to WebSocket client.
        
        Args:
            websocket: WebSocket connection
            generator: Async generator yielding chunks
            chunk_size: Number of characters per message
        """
        buffer = ""
        try:
            async for chunk in generator:
                buffer += chunk
                
                # Send when buffer reaches chunk_size
                if len(buffer) >= chunk_size:
                    await websocket.send_json({
                        "type": "streaming",
                        "chunk": buffer
                    })
                    buffer = ""
            
            # Send remaining buffer
            if buffer:
                await websocket.send_json({
                    "type": "streaming",
                    "chunk": buffer
                })
                
            # Send completion
            await websocket.send_json({
                "type": "response_complete"
            })
            
        except WebSocketDisconnect:
            logger.info("WebSocket disconnected during streaming")
        except Exception as e:
            logger.error(f"WebSocket streaming error: {e}")
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })

    @staticmethod
    async def generate_lm_response(
        query: str,
        model_callable,
        stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """
        Generate LLM response with optional streaming.
        
        Args:
            query: User query
            model_callable: Callable that processes query
            stream: Whether to stream response
            
        Yields:
            Response chunks
        """
        if stream:
            # Streaming response simulation
            words = ["TARS", "is", "processing", "your", "query..."]
            for word in words:
                yield word + " "
                await asyncio.sleep(0.1)
        else:
            # Non-streaming response
            response = await asyncio.to_thread(
                model_callable,
                query
            )
            yield str(response)

    @staticmethod
    async def generate_embedding_stream(
        texts: list,
        embedder_callable,
        batch_size: int = 10
    ) -> AsyncGenerator[dict, None]:
        """
        Generate embeddings in streaming fashion.
        
        Args:
            texts: List of texts to embed
            embedder_callable: Embedding model callable
            batch_size: Batch size for processing
            
        Yields:
            Embedding dictionaries
        """
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            embeddings = await asyncio.to_thread(
                embedder_callable,
                batch
            )
            
            for text, embedding in zip(batch, embeddings):
                yield {
                    "text": text,
                    "embedding": embedding.tolist() if hasattr(embedding, 'tolist') else embedding
                }
            
            await asyncio.sleep(0.01)  # Prevent blocking

    @staticmethod
    async def handle_streaming_error(
        websocket: WebSocket,
        error: Exception
    ):
        """
        Handle streaming error gracefully.
        
        Args:
            websocket: WebSocket connection
            error: Exception that occurred
        """
        error_message = {
            "type": "error",
            "code": type(error).__name__,
            "message": str(error)
        }
        
        try:
            await websocket.send_json(error_message)
        except Exception as e:
            logger.error(f"Error sending error message: {e}")


class BufferedStreamResponse:
    """
    Buffered streaming response for efficient chunking.
    """

    def __init__(self, generator: AsyncGenerator, buffer_size: int = 1024):
        """
        Initialize buffered stream.
        
        Args:
            generator: Async generator
            buffer_size: Buffer size in bytes
        """
        self.generator = generator
        self.buffer_size = buffer_size
        self.buffer = ""

    async def read_chunk(self) -> Optional[str]:
        """
        Read next chunk from buffer.
        
        Returns:
            Next chunk or None if exhausted
        """
        while len(self.buffer) < self.buffer_size:
            try:
                self.buffer += await asyncio.wait_for(
                    self.generator.__anext__(),
                    timeout=1.0
                )
            except (StopAsyncIteration, asyncio.TimeoutError):
                break

        if self.buffer:
            chunk = self.buffer[:self.buffer_size]
            self.buffer = self.buffer[self.buffer_size:]
            return chunk
        
        return None if not self.buffer else self.buffer

    async def stream(self) -> AsyncGenerator[str, None]:
        """
        Stream buffered chunks.
        
        Yields:
            Response chunks
        """
        while True:
            chunk = await self.read_chunk()
            if chunk:
                yield chunk
            else:
                break
