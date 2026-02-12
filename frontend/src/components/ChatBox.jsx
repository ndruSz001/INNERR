import React from 'react';
import { Copy, Check } from 'lucide-react';
import { useState } from 'react';

export default function ChatBox({ message }) {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === 'user';

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg ${
          isUser
            ? 'bg-blue-600 text-white rounded-br-none'
            : 'bg-slate-700 text-slate-100 rounded-bl-none'
        }`}
      >
        <p className="text-sm break-words">{message.content}</p>
        
        <div className="flex items-center justify-between mt-2 gap-2">
          <span className="text-xs opacity-70">
            {new Date(message.timestamp).toLocaleTimeString()}
          </span>
          
          {!isUser && (
            <button
              onClick={handleCopy}
              className="opacity-70 hover:opacity-100 transition"
              title="Copy message"
            >
              {copied ? (
                <Check size={14} className="text-green-400" />
              ) : (
                <Copy size={14} />
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
