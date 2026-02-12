import React, { useState, useEffect, useRef } from 'react';
import ChatBox from '../components/ChatBox';
import { Send, Loader } from 'lucide-react';
import '../styles/Chat.css';

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);
  const ws = useRef(null);
  const messagesEndRef = useRef(null);

  // WebSocket Connection
  useEffect(() => {
    const connectWebSocket = () => {
      try {
        ws.current = new WebSocket('ws://localhost:8000/ws/chat');

        ws.current.onopen = () => {
          console.log('WebSocket connected');
          setWsConnected(true);
          // Send initial connection message
          ws.current.send(JSON.stringify({
            type: 'connect',
            user_id: 'default_user'
          }));
        };

        ws.current.onmessage = (event) => {
          const data = JSON.parse(event.data);
          
          if (data.type === 'response') {
            // LLM response received
            setMessages(prev => [
              ...prev,
              {
                id: Date.now(),
                role: 'assistant',
                content: data.content,
                timestamp: new Date().toISOString()
              }
            ]);
          } else if (data.type === 'streaming') {
            // Streaming chunk
            setMessages(prev => {
              const newMessages = [...prev];
              if (newMessages.length > 0) {
                const lastMsg = newMessages[newMessages.length - 1];
                if (lastMsg.role === 'assistant') {
                  lastMsg.content += data.chunk;
                }
              }
              return newMessages;
            });
          }
          setIsLoading(false);
        };

        ws.current.onerror = (error) => {
          console.error('WebSocket error:', error);
          setWsConnected(false);
        };

        ws.current.onclose = () => {
          console.log('WebSocket disconnected');
          setWsConnected(false);
          // Try to reconnect after 3 seconds
          setTimeout(connectWebSocket, 3000);
        };
      } catch (error) {
        console.error('WebSocket connection failed:', error);
        setWsConnected(false);
      }
    };

    connectWebSocket();

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, []);

  // Scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!input.trim() || !wsConnected) return;

    // Add user message
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // Send via WebSocket
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        type: 'query',
        content: input,
        user_id: 'default_user',
        conversation_id: 'default'
      }));
    }
  };

  return (
    <div className="chat-container max-w-4xl mx-auto h-[calc(100vh-200px)] flex flex-col">
      
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-t-lg p-4 shadow-lg">
        <h1 className="text-2xl font-bold text-white">💬 Chat with TARS</h1>
        <p className="text-blue-100 text-sm mt-1">
          {wsConnected ? '🟢 Connected' : '🔴 Connecting...'}
        </p>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto bg-slate-800/50 border border-slate-700 p-6 space-y-4">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <p className="text-slate-400 text-lg mb-2">No messages yet</p>
              <p className="text-slate-500 text-sm">Start a conversation by typing a message below</p>
            </div>
          </div>
        ) : (
          messages.map(msg => (
            <ChatBox key={msg.id} message={msg} />
          ))
        )}
        
        {isLoading && (
          <div className="flex items-center gap-2 text-slate-400">
            <Loader size={20} className="animate-spin" />
            <span>TARS is thinking...</span>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <form
        onSubmit={handleSendMessage}
        className="bg-slate-900 border border-t border-slate-700 rounded-b-lg p-4 shadow-lg"
      >
        <div className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={!wsConnected || isLoading}
            placeholder={wsConnected ? "Type your message..." : "Connecting..."}
            className="flex-1 bg-slate-800 text-white rounded-lg px-4 py-2 border border-slate-700 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!wsConnected || isLoading || !input.trim()}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 text-white rounded-lg px-6 py-2 flex items-center gap-2 transition"
          >
            <Send size={20} />
            <span className="hidden sm:inline">Send</span>
          </button>
        </div>
        
        {!wsConnected && (
          <p className="text-red-400 text-sm mt-2">
            ⚠️ WebSocket connection lost. Attempting to reconnect...
          </p>
        )}
      </form>
    </div>
  );
}
