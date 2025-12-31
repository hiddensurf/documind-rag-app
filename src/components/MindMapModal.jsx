import React, { useRef, useEffect, useState } from 'react';
import { Brain, X, Download, Copy, Check, AlertCircle } from 'lucide-react';
import mermaid from 'mermaid';

const MindMapModal = ({ mermaidCode, onClose }) => {
  const containerRef = useRef(null);
  const [isRendering, setIsRendering] = useState(true);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);
  const [svgContent, setSvgContent] = useState('');

  useEffect(() => {
    let mounted = true;

    const renderDiagram = async () => {
      if (!mermaidCode) {
        console.error('MindMapModal - No mermaid code provided');
        if (mounted) {
          setError('No diagram code provided');
          setIsRendering(false);
        }
        return;
      }

      try {
        console.log('MindMapModal - Starting render');
        console.log('MindMapModal - Code:', mermaidCode);
        
        setIsRendering(true);
        setError(null);
        
        // Clean the code
        let cleanCode = mermaidCode.trim();
        cleanCode = cleanCode.replace(/```mermaid\n?/g, '').replace(/```\n?/g, '').trim();
        
        // Ensure it starts with a graph type
        if (!cleanCode.startsWith('graph') && !cleanCode.startsWith('flowchart')) {
          cleanCode = 'graph TD\n' + cleanCode;
        }
        
        console.log('MindMapModal - Clean code:', cleanCode);
        
        // Generate unique ID
        const id = `mermaid-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        
        // Render using mermaid.render
        console.log('MindMapModal - Calling mermaid.render with ID:', id);
        const { svg } = await mermaid.render(id, cleanCode);
        
        console.log('MindMapModal - Render successful!');
        
        if (!mounted) return;
        
        setSvgContent(svg);
        setIsRendering(false);
        
      } catch (err) {
        console.error('MindMapModal - Render error:', err);
        if (mounted) {
          setError(err.message || 'Failed to render diagram');
          setIsRendering(false);
        }
      }
    };

    // Small delay to ensure component is mounted
    const timer = setTimeout(renderDiagram, 100);

    return () => {
      mounted = false;
      clearTimeout(timer);
    };
  }, [mermaidCode]);

  const handleDownload = () => {
    if (!containerRef.current) return;
    
    const svg = containerRef.current.querySelector('svg');
    if (svg) {
      try {
        const svgData = new XMLSerializer().serializeToString(svg);
        const blob = new Blob([svgData], { type: 'image/svg+xml' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'mindmap.svg';
        link.click();
        URL.revokeObjectURL(url);
      } catch (err) {
        console.error('Download failed:', err);
        alert('Failed to download diagram');
      }
    }
  };

  const handleCopyCode = () => {
    navigator.clipboard.writeText(mermaidCode)
      .then(() => {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      })
      .catch(err => {
        console.error('Copy failed:', err);
        alert('Failed to copy code');
      });
  };

  const handleRetry = () => {
    setError(null);
    setIsRendering(true);
    setSvgContent('');
    
    setTimeout(async () => {
      try {
        let cleanCode = mermaidCode.trim();
        cleanCode = cleanCode.replace(/```mermaid\n?/g, '').replace(/```\n?/g, '').trim();
        
        if (!cleanCode.startsWith('graph') && !cleanCode.startsWith('flowchart')) {
          cleanCode = 'graph TD\n' + cleanCode;
        }
        
        const id = `mermaid-retry-${Date.now()}`;
        const { svg } = await mermaid.render(id, cleanCode);
        
        setSvgContent(svg);
        setIsRendering(false);
      } catch (err) {
        setError(err.message);
        setIsRendering(false);
      }
    }, 100);
  };

  return (
    <div 
      className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-in fade-in duration-200"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="bg-light-bg dark:bg-dark-bg rounded-2xl w-full max-w-6xl max-h-[90vh] flex flex-col shadow-2xl border border-light-border dark:border-dark-border">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-light-border dark:border-dark-border">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold">Mind Map Visualization</h3>
              <p className="text-sm text-light-textSecondary dark:text-dark-textSecondary">
                {isRendering ? 'Rendering diagram...' : error ? 'Render failed' : 'Interactive diagram'}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleCopyCode}
              className="flex items-center gap-2 px-3 py-2 hover:bg-light-hover dark:hover:bg-dark-hover rounded-xl transition-colors text-sm"
              title="Copy Mermaid code"
            >
              {copied ? (
                <>
                  <Check className="w-4 h-4 text-green-500" />
                  <span className="text-green-500">Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4" />
                  <span>Copy Code</span>
                </>
              )}
            </button>
            {!error && !isRendering && svgContent && (
              <button
                onClick={handleDownload}
                className="p-2 hover:bg-light-hover dark:hover:bg-dark-hover rounded-xl transition-colors"
                title="Download as SVG"
              >
                <Download className="w-5 h-5" />
              </button>
            )}
            <button
              onClick={onClose}
              className="p-2 hover:bg-light-hover dark:hover:bg-dark-hover rounded-xl transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>
        
        {/* Content */}
        <div className="flex-1 overflow-auto p-8 bg-light-sidebar dark:bg-dark-sidebar">
          {isRendering ? (
            <div className="flex items-center justify-center min-h-[400px]">
              <div className="text-center">
                <div className="w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                <p className="text-light-textSecondary dark:text-dark-textSecondary">
                  Rendering mind map...
                </p>
                <p className="text-xs text-light-textSecondary dark:text-dark-textSecondary mt-2">
                  This may take a few seconds
                </p>
              </div>
            </div>
          ) : error ? (
            <div className="flex items-center justify-center min-h-[400px]">
              <div className="text-center max-w-lg">
                <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">Failed to Render Diagram</h3>
                <p className="text-sm text-light-textSecondary dark:text-dark-textSecondary mb-4">
                  {error}
                </p>
                <button
                  onClick={handleRetry}
                  className="px-4 py-2 bg-purple-500 hover:bg-purple-600 text-white rounded-xl text-sm font-medium transition-colors"
                >
                  Try Again
                </button>
              </div>
            </div>
          ) : (
            <div 
              ref={containerRef}
              className="flex items-center justify-center min-h-[400px] mermaid-container"
              dangerouslySetInnerHTML={{ __html: svgContent }}
            />
          )}
        </div>

        {/* Raw Code Preview */}
        <div className="border-t border-light-border dark:border-dark-border p-4 bg-light-bg dark:bg-dark-bg">
          <details>
            <summary className="cursor-pointer text-sm font-medium hover:text-purple-500 flex items-center gap-2">
              <Copy className="w-4 h-4" />
              View Raw Mermaid Code
            </summary>
            <pre className="text-xs bg-dark-bg dark:bg-black p-4 rounded-lg overflow-auto max-h-40 border border-light-border dark:border-dark-border mt-2 font-mono text-gray-300">
              {mermaidCode}
            </pre>
          </details>
        </div>
      </div>
    </div>
  );
};

export default MindMapModal;