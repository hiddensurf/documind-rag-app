import { useState, useRef, useEffect } from 'react';
import { Send, Sparkles } from 'lucide-react';

export default function ChatInput({ onSendMessage, onAdvancedAnalysis, disabled, hasCADDocuments }) {
  const [message, setMessage] = useState('');
  const [isAdvancedMode, setIsAdvancedMode] = useState(false);
  const textareaRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [message]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      if (isAdvancedMode && hasCADDocuments) {
        onAdvancedAnalysis(message.trim());
      } else {
        onSendMessage(message.trim());
      }
      setMessage('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4">
      <div className="max-w-4xl mx-auto">
        {hasCADDocuments && (
          <div className="mb-2 flex items-center gap-2">
            <button
              type="button"
              onClick={() => setIsAdvancedMode(!isAdvancedMode)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                isAdvancedMode
                  ? 'bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-200 border-2 border-purple-500 shadow-lg'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 border-2 border-transparent hover:border-purple-300 hover:shadow'
              }`}
            >
              <Sparkles className={`w-4 h-4 ${isAdvancedMode ? 'animate-pulse' : ''}`} />
              <span>Advanced CAD Analysis</span>
            </button>
            {isAdvancedMode && (
              <div className="text-xs text-purple-600 dark:text-purple-400 flex items-center gap-1">
                <Sparkles className="w-3 h-3 animate-pulse" />
                <span>5-stage vision analysis enabled</span>
              </div>
            )}
          </div>
        )}
        
        <div className="flex gap-2">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={isAdvancedMode ? "What would you like to analyze about this CAD drawing?" : "Ask a question about your documents..."}
            disabled={disabled}
            rows={1}
            className={`flex-1 resize-none rounded-lg border px-4 py-3 focus:outline-none focus:ring-2 transition-all ${
              isAdvancedMode
                ? 'border-purple-300 focus:ring-purple-500 bg-purple-50 dark:bg-purple-900/20 dark:border-purple-600'
                : 'border-gray-300 dark:border-gray-600 focus:ring-blue-500 bg-white dark:bg-gray-700'
            } text-gray-900 dark:text-gray-100 disabled:opacity-50 disabled:cursor-not-allowed`}
            style={{ maxHeight: '200px', minHeight: '48px' }}
          />
          <button
            type="submit"
            disabled={disabled || !message.trim()}
            className={`px-4 py-3 rounded-lg font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-lg hover:shadow-xl ${
              isAdvancedMode
                ? 'bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white'
                : 'bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white'
            }`}
          >
            {isAdvancedMode ? (
              <>
                <Sparkles className="w-5 h-5" />
                <span className="hidden sm:inline">Analyze</span>
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                <span className="hidden sm:inline">Send</span>
              </>
            )}
          </button>
        </div>
      </div>
    </form>
  );
}
