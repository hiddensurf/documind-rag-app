import React, { useState } from 'react';
import { AlertCircle, ExternalLink, X, FileText } from 'lucide-react';

const DWGConverter = ({ fileName, onClose, onRetry }) => {
  const [selectedMethod, setSelectedMethod] = useState('online');

  const conversionMethods = [
    {
      id: 'online',
      name: 'Online Converter (Recommended)',
      description: 'Convert DWG to DXF using free online tools',
      tools: [
        {
          name: 'Zamzar',
          url: 'https://www.zamzar.com/convert/dwg-to-dxf/',
          free: true,
          fast: true
        },
        {
          name: 'AnyConv',
          url: 'https://anyconv.com/dwg-to-dxf-converter/',
          free: true,
          fast: true
        },
        {
          name: 'CloudConvert',
          url: 'https://cloudconvert.com/dwg-to-dxf',
          free: true,
          fast: true
        }
      ]
    },
    {
      id: 'software',
      name: 'Desktop Software',
      description: 'Use CAD software to export',
      tools: [
        {
          name: 'AutoCAD',
          steps: 'File → Save As → DXF',
          free: false
        },
        {
          name: 'FreeCAD',
          steps: 'File → Export → DXF',
          free: true,
          download: 'https://www.freecad.org/downloads.php'
        },
        {
          name: 'LibreCAD',
          steps: 'File → Export → DXF',
          free: true,
          download: 'https://librecad.org/download.html'
        }
      ]
    }
  ];

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-light-bg dark:bg-dark-bg rounded-2xl w-full max-w-2xl shadow-2xl border border-light-border dark:border-dark-border">
        
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-light-border dark:border-dark-border">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-yellow-500/20 rounded-xl flex items-center justify-center">
              <AlertCircle className="w-5 h-5 text-yellow-500" />
            </div>
            <div>
              <h3 className="text-lg font-semibold">DWG Conversion Required</h3>
              <p className="text-sm text-light-textSecondary dark:text-dark-textSecondary">
                {fileName}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-light-hover dark:hover:bg-dark-hover rounded-xl transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          <div className="mb-6 p-4 bg-blue-500/10 border border-blue-500/20 rounded-xl">
            <p className="text-sm">
              <strong>DWG files</strong> are proprietary AutoCAD format. For web processing, 
              we need <strong>DXF format</strong> (open standard). Choose a conversion method below:
            </p>
          </div>

          {/* Method Tabs */}
          <div className="flex gap-2 mb-6">
            {conversionMethods.map(method => (
              <button
                key={method.id}
                onClick={() => setSelectedMethod(method.id)}
                className={`flex-1 px-4 py-3 rounded-xl font-medium text-sm transition-all ${
                  selectedMethod === method.id
                    ? 'bg-purple-500 text-white shadow-lg'
                    : 'bg-light-hover dark:bg-dark-hover hover:bg-light-border dark:hover:bg-dark-border'
                }`}
              >
                {method.name}
              </button>
            ))}
          </div>

          {/* Selected Method Content */}
          <div className="space-y-4">
            {conversionMethods.find(m => m.id === selectedMethod)?.tools.map((tool, idx) => (
              <div
                key={idx}
                className="p-4 bg-light-sidebar dark:bg-dark-sidebar rounded-xl border border-light-border dark:border-dark-border"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h4 className="font-semibold">{tool.name}</h4>
                      {tool.free && (
                        <span className="text-xs px-2 py-0.5 bg-green-500/10 text-green-500 rounded-full">
                          Free
                        </span>
                      )}
                      {tool.fast && (
                        <span className="text-xs px-2 py-0.5 bg-blue-500/10 text-blue-500 rounded-full">
                          Fast
                        </span>
                      )}
                    </div>
                    {tool.steps && (
                      <p className="text-sm text-light-textSecondary dark:text-dark-textSecondary">
                        {tool.steps}
                      </p>
                    )}
                  </div>
                  {tool.url && (
                    <a
                      href={tool.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 px-4 py-2 bg-purple-500 hover:bg-purple-600 text-white rounded-xl text-sm font-medium transition-colors"
                    >
                      Open
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  )}
                  {tool.download && (
                    <a
                      href={tool.download}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-xl text-sm font-medium transition-colors"
                    >
                      Download
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Instructions */}
          <div className="mt-6 p-4 bg-light-hover dark:bg-dark-hover rounded-xl">
            <h4 className="font-medium mb-2 flex items-center gap-2">
              <FileText className="w-4 h-4" />
              Quick Steps:
            </h4>
            <ol className="text-sm space-y-1 list-decimal list-inside text-light-textSecondary dark:text-dark-textSecondary">
              <li>Convert your DWG file to DXF using one of the methods above</li>
              <li>Download the converted DXF file</li>
              <li>Upload the DXF file to DocuMind</li>
              <li>Enjoy interactive CAD viewing and querying!</li>
            </ol>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-light-border dark:border-dark-border">
          <p className="text-sm text-light-textSecondary dark:text-dark-textSecondary">
            After conversion, you can upload the DXF file here
          </p>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-purple-500 hover:bg-purple-600 text-white rounded-xl text-sm font-medium transition-colors"
          >
            Got it!
          </button>
        </div>
      </div>
    </div>
  );
};

export default DWGConverter;