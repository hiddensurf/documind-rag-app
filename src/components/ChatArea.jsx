import React, { useRef, useEffect } from 'react';
import ChatMessage from './ChatMessage';
import { Loader2 } from 'lucide-react';

const ChatArea = ({ messages, isLoading, onViewMindMap }) => {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="max-w-3xl mx-auto px-4 py-8 space-y-6">
        {messages.map(msg => (
          <ChatMessage
            key={msg.id}
            message={msg}
            onViewMindMap={onViewMindMap}
          />
        ))}
        
        {isLoading && (
          <div className="flex items-start gap-4">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center flex-shrink-0">
              <Loader2 className="w-5 h-5 text-white animate-spin" />
            </div>
            <div className="flex-1 bg-light-sidebar dark:bg-dark-sidebar rounded-2xl p-4 border border-light-border dark:border-dark-border">
              <div className="flex items-center gap-2 text-light-textSecondary dark:text-dark-textSecondary">
                <span>Thinking</span>
                <span className="animate-pulse">...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default ChatArea;
