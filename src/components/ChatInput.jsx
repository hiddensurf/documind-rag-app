import { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, Bot, ChevronDown } from 'lucide-react';

// Available AI models - UPDATED WITH GOOGLE STUDIO GEMINI
const AI_MODELS = {
  hybrid: [
    { id: 'meta-llama/llama-3.3-70b-instruct:free', name: 'Llama 3.3 70B', free: true, recommended: true, description: 'Best free text model' },
    { id: 'google/gemma-3-27b-it:free', name: 'Gemma 3 27B', free: true, description: 'Fast and efficient' },
    { id: 'openai/gpt-oss-20b:free', name: 'GPT OSS 20B', free: true, description: 'GPT-style model' },
    { id: 'deepseek/deepseek-r1', name: 'DeepSeek R1', free: false, description: 'Best reasoning (paid)' },
    { id: 'qwen/qwen3-235b-a22b', name: 'Qwen 3 235B', free: false, description: 'Large model (paid)' },
  ],
  vision: [
    { id: 'gemini-2.5-flash', name: 'Gemini 2.5 Flash', free: true, recommended: true, description: 'Best quality (auto-fallback to Lite)' },
    { id: 'gemini-2.5-flash-lite', name: 'Gemini 2.5 Flash Lite', free: true, description: 'Lighter, better for quota limits' },
    { id: 'nvidia/nemotron-nano-12b-v2-vl:free', name: 'NVIDIA Nemotron VL', free: true, description: 'Technical diagrams' },
    { id: 'qwen/qwen-2.5-vl-7b-instruct:free', name: 'Qwen 2.5 VL', free: true, description: 'Qwen vision model' },
  ]
};

export default function ChatInput({ 
  onSendMessage, 
  onAdvancedAnalysis, 
  onHybridAnalysis,
  disabled, 
  hasCADDocuments 
}) {
  const [message, setMessage] = useState('');
  const [analysisMode, setAnalysisMode] = useState('normal');
  const [showModeMenu, setShowModeMenu] = useState(false);
  const [showModelPicker, setShowModelPicker] = useState(false);
  const [selectedModel, setSelectedModel] = useState(null);
  const textareaRef = useRef(null);
  const modeMenuRef = useRef(null);
  const modelPickerRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [message]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (modeMenuRef.current && !modeMenuRef.current.contains(event.target)) {
        setShowModeMenu(false);
      }
      if (modelPickerRef.current && !modelPickerRef.current.contains(event.target)) {
        setShowModelPicker(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      if (analysisMode === 'vision' && hasCADDocuments) {
        onAdvancedAnalysis(message.trim(), selectedModel);
      } else if (analysisMode === 'hybrid' && hasCADDocuments) {
        onHybridAnalysis(message.trim(), selectedModel);
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

  const getModeConfig = () => {
    switch (analysisMode) {
      case 'vision':
        return {
          label: 'Vision Analysis',
          icon: Sparkles,
          gradient: 'from-purple-600 to-purple-700',
          hoverGradient: 'hover:from-purple-700 hover:to-purple-800',
          bgLight: 'bg-purple-50 dark:bg-purple-900/20',
          border: 'border-purple-300 dark:border-purple-600',
          ring: 'focus:ring-purple-500',
          buttonBg: 'bg-purple-100 dark:bg-purple-900',
          buttonText: 'text-purple-700 dark:text-purple-200',
          buttonBorder: 'border-purple-500',
          description: '5-stage vision',
          models: AI_MODELS.vision
        };
      case 'hybrid':
        return {
          label: 'Hybrid AI',
          icon: Bot,
          gradient: 'from-blue-600 to-blue-700',
          hoverGradient: 'hover:from-blue-700 hover:to-blue-800',
          bgLight: 'bg-blue-50 dark:bg-blue-900/20',
          border: 'border-blue-300 dark:border-blue-600',
          ring: 'focus:ring-blue-500',
          buttonBg: 'bg-blue-100 dark:bg-blue-900',
          buttonText: 'text-blue-700 dark:text-blue-200',
          buttonBorder: 'border-blue-500',
          description: 'CV + AI',
          models: AI_MODELS.hybrid
        };
      default:
        return {
          label: 'Normal Chat',
          icon: Send,
          gradient: 'from-blue-600 to-blue-700',
          hoverGradient: 'hover:from-blue-700 hover:to-blue-800',
          bgLight: 'bg-white dark:bg-gray-700',
          border: 'border-gray-300 dark:border-gray-600',
          ring: 'focus:ring-blue-500',
          buttonBg: 'bg-gray-100 dark:bg-gray-700',
          buttonText: 'text-gray-700 dark:text-gray-300',
          buttonBorder: 'border-transparent',
          description: 'RAG chat',
          models: []
        };
    }
  };

  const config = getModeConfig();
  const Icon = config.icon;

  const getModelDisplayName = () => {
    if (!selectedModel) return 'Auto';
    const model = [...AI_MODELS.hybrid, ...AI_MODELS.vision].find(m => m.id === selectedModel);
    return model ? model.name.split(' ')[0] + (model.name.includes('Studio') ? ' Studio' : '') : 'Auto';
  };

  const showModeSelector = true;

  return (
    <form onSubmit={handleSubmit} className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4">
      <div className="max-w-4xl mx-auto">
        {showModeSelector && (
          <div className="mb-3 flex items-center gap-2 flex-wrap">
            <div className="relative" ref={modeMenuRef}>
              <button
                type="button"
                onClick={() => setShowModeMenu(!showModeMenu)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all shadow-md hover:shadow-lg ${
                  analysisMode !== 'normal'
                    ? `${config.buttonBg} ${config.buttonText} border-2 ${config.buttonBorder}`
                    : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 border-2 border-gray-300 dark:border-gray-600 hover:border-blue-400'
                }`}
              >
                <Icon className={`w-4 h-4 ${analysisMode !== 'normal' ? 'animate-pulse' : ''}`} />
                <span className="font-semibold">{config.label}</span>
                <ChevronDown className={`w-4 h-4 transition-transform ${showModeMenu ? 'rotate-180' : ''}`} />
              </button>

              {showModeMenu && (
                <div className="absolute bottom-full left-0 mb-2 w-72 bg-white dark:bg-gray-800 rounded-xl shadow-2xl border-2 border-gray-200 dark:border-gray-700 z-[9999] overflow-hidden">
                  <div className="p-1">
                    <button
                      type="button"
                      onClick={() => { setAnalysisMode('normal'); setShowModeMenu(false); }}
                      className={`w-full flex items-start gap-3 p-3 rounded-lg transition-all ${
                        analysisMode === 'normal' 
                          ? 'bg-blue-50 dark:bg-blue-900/30 border-2 border-blue-500' 
                          : 'hover:bg-gray-100 dark:hover:bg-gray-700'
                      }`}
                    >
                      <Send className="w-6 h-6 mt-0.5 text-blue-600 dark:text-blue-400 flex-shrink-0" />
                      <div className="flex-1 text-left">
                        <div className="font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
                          Normal Chat
                          {analysisMode === 'normal' && <span className="text-xs bg-blue-500 text-white px-2 py-0.5 rounded-full">Active</span>}
                        </div>
                        <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Regular RAG query</div>
                      </div>
                    </button>
                    
                    <button
                      type="button"
                      onClick={() => { setAnalysisMode('vision'); setShowModeMenu(false); }}
                      className={`w-full flex items-start gap-3 p-3 rounded-lg transition-all ${
                        analysisMode === 'vision' 
                          ? 'bg-purple-50 dark:bg-purple-900/30 border-2 border-purple-500' 
                          : 'hover:bg-purple-50 dark:hover:bg-purple-900/20'
                      }`}
                    >
                      <Sparkles className="w-6 h-6 mt-0.5 text-purple-600 dark:text-purple-400 flex-shrink-0" />
                      <div className="flex-1 text-left">
                        <div className="font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
                          Vision Analysis
                          {analysisMode === 'vision' && <span className="text-xs bg-purple-500 text-white px-2 py-0.5 rounded-full">Active</span>}
                        </div>
                        <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">5-stage vision AI</div>
                      </div>
                    </button>
                    
                    <button
                      type="button"
                      onClick={() => { setAnalysisMode('hybrid'); setShowModeMenu(false); }}
                      className={`w-full flex items-start gap-3 p-3 rounded-lg transition-all ${
                        analysisMode === 'hybrid' 
                          ? 'bg-blue-50 dark:bg-blue-900/30 border-2 border-blue-500' 
                          : 'hover:bg-blue-50 dark:hover:bg-blue-900/20'
                      }`}
                    >
                      <Bot className="w-6 h-6 mt-0.5 text-blue-600 dark:text-blue-400 flex-shrink-0" />
                      <div className="flex-1 text-left">
                        <div className="font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
                          Hybrid AI
                          {analysisMode === 'hybrid' && <span className="text-xs bg-blue-500 text-white px-2 py-0.5 rounded-full">Active</span>}
                        </div>
                        <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">CV + AI models</div>
                      </div>
                    </button>
                  </div>
                </div>
              )}
            </div>

            {analysisMode !== 'normal' && config.models.length > 0 && (
              <div className="relative" ref={modelPickerRef}>
                <button
                  type="button"
                  onClick={() => setShowModelPicker(!showModelPicker)}
                  className="flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:bg-gray-200 dark:hover:bg-gray-600 shadow-sm"
                >
                  <span>Model: {getModelDisplayName()}</span>
                  <ChevronDown className={`w-3 h-3 transition-transform ${showModelPicker ? 'rotate-180' : ''}`} />
                </button>

                {showModelPicker && (
                  <div className="absolute bottom-full left-0 mb-2 w-80 bg-white dark:bg-gray-800 rounded-xl shadow-2xl border-2 border-gray-200 dark:border-gray-700 z-[9999] max-h-96 overflow-y-auto">
                    <div className="p-2">
                      <button
                        type="button"
                        onClick={() => { setSelectedModel(null); setShowModelPicker(false); }}
                        className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-all"
                      >
                        <div className="flex-1 text-left">
                          <div className="font-semibold text-gray-900 dark:text-gray-100">
                            🎯 Auto-select
                            <span className="ml-2 text-xs bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 px-2 py-1 rounded-full font-normal">Recommended</span>
                          </div>
                          <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Best available model</div>
                        </div>
                      </button>

                      <div className="my-2 border-t border-gray-200 dark:border-gray-600"></div>

                      {config.models.map((model) => (
                        <button
                          key={model.id}
                          type="button"
                          onClick={() => { setSelectedModel(model.id); setShowModelPicker(false); }}
                          className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-all text-left"
                        >
                          <div className="flex-1">
                            <div className="font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2 flex-wrap">
                              {model.name}
                              {model.free && <span className="text-xs bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 px-2 py-1 rounded-full font-normal">FREE</span>}
                              {!model.free && <span className="text-xs bg-yellow-100 dark:bg-yellow-900 text-yellow-700 dark:text-yellow-300 px-2 py-1 rounded-full font-normal">PAID</span>}
                              {model.recommended && <span className="text-xs">⭐</span>}
                            </div>
                            <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{model.description}</div>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {analysisMode !== 'normal' && (
              <div className={`flex items-center gap-1.5 px-3py-1.5 rounded-lg text-xs font-medium ${config.buttonBg} ${config.buttonText}`}>
<Icon className="w-3 h-3" />
<span>{config.description}</span>
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
        placeholder={
          analysisMode === 'vision' 
            ? "What would you like to analyze?" 
            : analysisMode === 'hybrid'
            ? "Ask about CAD structure..."
            : "Ask a question..."
        }
        disabled={disabled}
        rows={1}
        className={`flex-1 resize-none rounded-lg border-2 px-4 py-3 focus:outline-none focus:ring-2 transition-all ${
          config.border
        } ${config.ring} ${config.bgLight} text-gray-900 dark:text-gray-100 disabled:opacity-50 disabled:cursor-not-allowed`}
        style={{ maxHeight: '200px', minHeight: '52px' }}
      />
      <button
        type="submit"
        disabled={disabled || !message.trim()}
        className={`px-5 py-3 rounded-lg font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-lg hover:shadow-xl bg-gradient-to-r ${config.gradient} ${config.hoverGradient} text-white min-w-[100px] justify-center`}
      >
        <Icon className="w-5 h-5" />
        <span className="hidden sm:inline">
          {analysisMode === 'normal' ? 'Send' : 'Analyze'}
        </span>
      </button>
    </div>
  </div>
</form>
);
}
