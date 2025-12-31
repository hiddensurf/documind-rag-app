import React, { useState, useRef, useEffect } from 'react';
import { X, ZoomIn, ZoomOut, Maximize2, RotateCw, Download, Layers } from 'lucide-react';

const CADViewer = ({ documentId, documentName, onClose }) => {
  const [svgContent, setSvgContent] = useState('');
  const [manifest, setManifest] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const [startPan, setStartPan] = useState({ x: 0, y: 0 });
  const [showLayers, setShowLayers] = useState(false);
  
  const containerRef = useRef(null);
  const svgRef = useRef(null);

  useEffect(() => {
    loadCADData();
  }, [documentId]);

  const loadCADData = async () => {
    try {
      setLoading(true);
      
      // Load SVG render
      const svgResponse = await fetch(`http://localhost:8000/api/documents/${documentId}/cad-render`);
      if (svgResponse.ok) {
        const svgText = await svgResponse.text();
        setSvgContent(svgText);
      } else {
        throw new Error('Failed to load CAD render');
      }
      
      // Load manifest
      const manifestResponse = await fetch(`http://localhost:8000/api/documents/${documentId}/cad-manifest`);
      if (manifestResponse.ok) {
        const manifestData = await manifestResponse.json();
        setManifest(manifestData);
      }
      
      setLoading(false);
    } catch (err) {
      console.error('Error loading CAD data:', err);
      setError(err.message);
      setLoading(false);
    }
  };

  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev + 0.2, 5));
  };

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev - 0.2, 0.5));
  };

  const handleResetView = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  const handleMouseDown = (e) => {
    if (e.button === 0) { // Left click
      setIsPanning(true);
      setStartPan({ x: e.clientX - pan.x, y: e.clientY - pan.y });
    }
  };

  const handleMouseMove = (e) => {
    if (isPanning) {
      setPan({
        x: e.clientX - startPan.x,
        y: e.clientY - startPan.y
      });
    }
  };

  const handleMouseUp = () => {
    setIsPanning(false);
  };

  const handleWheel = (e) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? -0.1 : 0.1;
    setZoom(prev => Math.max(0.5, Math.min(5, prev + delta)));
  };

  const handleDownloadSVG = () => {
    const blob = new Blob([svgContent], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${documentName}.svg`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-light-bg dark:bg-dark-bg rounded-2xl w-full max-w-7xl max-h-[95vh] flex flex-col shadow-2xl border border-light-border dark:border-dark-border">
        
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-light-border dark:border-dark-border">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-semibold">{documentName}</h3>
              <p className="text-sm text-light-textSecondary dark:text-dark-textSecondary">
                {manifest ? `${manifest.statistics.total_entities} entities • ${manifest.units}` : 'Loading...'}
              </p>
            </div>
          </div>
          
          {/* Controls */}
          <div className="flex items-center gap-2">
            <button
              onClick={handleZoomOut}
              className="p-2 hover:bg-light-hover dark:hover:bg-dark-hover rounded-xl transition-colors"
              title="Zoom Out"
            >
              <ZoomOut className="w-5 h-5" />
            </button>
            <span className="text-sm font-mono min-w-[60px] text-center">
              {(zoom * 100).toFixed(0)}%
            </span>
            <button
              onClick={handleZoomIn}
              className="p-2 hover:bg-light-hover dark:hover:bg-dark-hover rounded-xl transition-colors"
              title="Zoom In"
            >
              <ZoomIn className="w-5 h-5" />
            </button>
            <button
              onClick={handleResetView}
              className="p-2 hover:bg-light-hover dark:hover:bg-dark-hover rounded-xl transition-colors"
              title="Reset View"
            >
              <Maximize2 className="w-5 h-5" />
            </button>
            {manifest && (
              <button
                onClick={() => setShowLayers(!showLayers)}
                className="p-2 hover:bg-light-hover dark:hover:bg-dark-hover rounded-xl transition-colors"
                title="Layers"
              >
                <Layers className="w-5 h-5" />
              </button>
            )}
            <button
              onClick={handleDownloadSVG}
              className="p-2 hover:bg-light-hover dark:hover:bg-dark-hover rounded-xl transition-colors"
              title="Download SVG"
            >
              <Download className="w-5 h-5" />
            </button>
            <button
              onClick={onClose}
              className="p-2 hover:bg-light-hover dark:hover:bg-dark-hover rounded-xl transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden flex">
          {/* CAD Viewer */}
          <div 
            ref={containerRef}
            className="flex-1 overflow-hidden bg-gray-100 dark:bg-gray-900 relative cursor-move"
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
            onWheel={handleWheel}
          >
            {loading ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                  <p className="text-light-textSecondary dark:text-dark-textSecondary">
                    Loading CAD drawing...
                  </p>
                </div>
              </div>
            ) : error ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-center max-w-md">
                  <div className="text-red-500 mb-4">
                    <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-semibold mb-2">Failed to Load CAD File</h3>
                  <p className="text-sm text-light-textSecondary dark:text-dark-textSecondary">
                    {error}
                  </p>
                </div>
              </div>
            ) : (
              <div 
                ref={svgRef}
                className="w-full h-full flex items-center justify-center"
                style={{
                  transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
                  transformOrigin: 'center',
                  transition: isPanning ? 'none' : 'transform 0.1s ease-out'
                }}
                dangerouslySetInnerHTML={{ __html: svgContent }}
              />
            )}
          </div>

          {/* Layers Panel */}
          {showLayers && manifest && (
            <div className="w-80 border-l border-light-border dark:border-dark-border bg-light-sidebar dark:bg-dark-sidebar overflow-y-auto">
              <div className="p-4">
                <h4 className="font-semibold mb-4">Layers & Statistics</h4>
                
                {/* Statistics */}
                <div className="mb-6">
                  <h5 className="text-sm font-medium mb-2 text-light-textSecondary dark:text-dark-textSecondary">
                    Drawing Info
                  </h5>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>Units:</span>
                      <span className="font-mono">{manifest.units}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Total Entities:</span>
                      <span className="font-mono">{manifest.statistics.total_entities}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Text Entities:</span>
                      <span className="font-mono">
                        {manifest.statistics.text_entities + (manifest.statistics.mtext_entities || 0)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Dimensions:</span>
                      <span className="font-mono">{manifest.statistics.dimension_entities}</span>
                    </div>
                  </div>
                </div>

                {/* Layers */}
                <div>
                  <h5 className="text-sm font-medium mb-2 text-light-textSecondary dark:text-dark-textSecondary">
                    Layers ({manifest.layers.length})
                  </h5>
                  <div className="space-y-1">
                    {manifest.layers.map((layer, idx) => (
                      <div
                        key={idx}
                        className="px-3 py-2 bg-light-bg dark:bg-dark-bg rounded-lg text-sm font-mono"
                      >
                        {layer}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer Hint */}
        <div className="px-4 py-2 border-t border-light-border dark:border-dark-border bg-light-sidebar dark:bg-dark-sidebar">
          <p className="text-xs text-light-textSecondary dark:text-dark-textSecondary text-center">
            💡 Drag to pan • Scroll to zoom • Click layers icon for details
          </p>
        </div>
      </div>
    </div>
  );
};

export default CADViewer;
