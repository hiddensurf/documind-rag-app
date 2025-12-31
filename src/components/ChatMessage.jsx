import React from 'react';
import { Brain, User, Sparkles } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const ChatMessage = ({ message, onViewMindMap }) => {
  const isUser = message.role === 'user';
  
  // FIXED: Handle both snake_case (from backend) and camelCase (from frontend)
  const hasMindMap = message.has_mindmap || message.hasMindMap || false;
  const mermaidCode = message.mermaid_code || message.mermaidCode || null;
  const sources = message.sources || [];

  // Debug logging
  console.log('ChatMessage render:', {
    hasMindMap,
    mermaidCodeExists: !!mermaidCode,
    mermaidCodeLength: mermaidCode?.length,
    messageKeys: Object.keys(message)
  });

  return (
    <div className="flex items-start gap-4">
      {/* Avatar */}
      <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
        isUser 
          ? 'bg-light-border dark:bg-dark-border' 
          : 'bg-gradient-to-br from-purple-500 to-pink-500'
      }`}>
        {isUser ? (
          <User className="w-5 h-5 text-light-text dark:text-dark-text" />
        ) : (
          <Sparkles className="w-5 h-5 text-white" />
        )}
      </div>

      {/* Message Content */}
      <div className="flex-1 space-y-2">
        <div className={`rounded-2xl p-4 ${
          isUser
            ? 'bg-transparent'
            : message.isError
            ? 'bg-red-500/10 border border-red-500/20'
            : 'bg-light-sidebar dark:bg-dark-sidebar border border-light-border dark:border-dark-border'
        }`}>
          {isUser ? (
            <p className="whitespace-pre-wrap m-0 leading-relaxed">
              {message.content}
            </p>
          ) : (
            <div className="prose prose-sm dark:prose-invert max-w-none prose-p:my-2 prose-headings:my-3">
              <ReactMarkdown
                components={{
                  p: ({node, ...props}) => <p className="my-2 leading-relaxed" {...props} />,
                  ul: ({node, ...props}) => <ul className="my-2 ml-4 space-y-1" {...props} />,
                  ol: ({node, ...props}) => <ol className="my-2 ml-4 space-y-1" {...props} />,
                  li: ({node, ...props}) => <li className="leading-relaxed" {...props} />,
                  strong: ({node, ...props}) => <strong className="font-semibold text-purple-500" {...props} />,
                  code: ({node, inline, ...props}) => 
                    inline ? (
                      <code className="px-1.5 py-0.5 bg-light-border dark:bg-dark-border rounded text-sm" {...props} />
                    ) : (
                      <code className="block p-3 bg-light-border dark:bg-dark-border rounded-lg text-sm overflow-x-auto" {...props} />
                    ),
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          )}
        </div>

        {/* Mind Map Button - FIXED */}
        {hasMindMap && mermaidCode && !isUser && (
          <button
            onClick={() => {
              console.log('Mind Map button clicked, mermaidCode:', mermaidCode);
              onViewMindMap(mermaidCode);
            }}
            className="inline-flex items-center gap-2 px-4 py-2 bg-purple-500 hover:bg-purple-600 text-white rounded-xl text-sm font-medium transition-colors shadow-lg hover:shadow-xl transform hover:scale-105 transition-all"
          >
            <Brain className="w-4 h-4" />
            View Mind Map
          </button>
        )}

        {/* Sources */}
        {sources.length > 0 && !isUser && (
          <div className="flex flex-wrap gap-2">
            <span className="text-xs text-light-textSecondary dark:text-dark-textSecondary">
              Sources:
            </span>
            {sources.map((source, idx) => (
              <span
                key={idx}
                className="text-xs px-2 py-1 bg-purple-500/10 border border-purple-500/20 rounded-lg"
              >
                {source}
              </span>
            ))}
          </div>
        )}

        {/* Timestamp */}
        <div className="text-xs text-light-textSecondary dark:text-dark-textSecondary">
          {message.timestamp}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;