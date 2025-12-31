import React, { useRef } from 'react';
import { Upload, Loader2, AlertCircle, Check } from 'lucide-react';

const DocumentUpload = ({ onFilesSelected, uploadProgress }) => {
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
      onFilesSelected(files);
    }
    e.target.value = '';
  };

  return (
    <div className="p-4 border-b border-light-border dark:border-dark-border">
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept=".pdf,.docx,.txt,.md,.dwg,.dxf,.stl"
        onChange={handleFileChange}
        className="hidden"
      />
      <button
        onClick={() => fileInputRef.current?.click()}
        className="w-full py-6 border-2 border-dashed border-light-border dark:border-dark-border rounded-xl hover:border-purple-500 hover:bg-light-hover dark:hover:bg-dark-hover transition-all flex flex-col items-center gap-2 group"
      >
        <div className="w-12 h-12 rounded-full bg-light-hover dark:bg-dark-hover group-hover:bg-purple-500/10 flex items-center justify-center transition-colors">
          <Upload className="w-5 h-5 text-light-textSecondary dark:text-dark-textSecondary group-hover:text-purple-500" />
        </div>
        <span className="text-sm text-light-textSecondary dark:text-dark-textSecondary">
          Upload documents
        </span>
      </button>

      {uploadProgress && (
        <div className={`mt-3 p-3 rounded-lg ${
          uploadProgress.status === 'error' 
            ? 'bg-red-500/10 border border-red-500/20' 
            : uploadProgress.status === 'ready'
            ? 'bg-green-500/10 border border-green-500/20'
            : 'bg-purple-500/10 border border-purple-500/20'
        }`}>
          <div className="flex items-center gap-2 text-sm">
            {uploadProgress.status === 'error' ? (
              <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0" />
            ) : uploadProgress.status === 'ready' ? (
              <Check className="w-4 h-4 text-green-500 flex-shrink-0" />
            ) : (
              <Loader2 className="w-4 h-4 animate-spin text-purple-500 flex-shrink-0" />
            )}
            <span className="flex-1 truncate text-light-text dark:text-dark-text">
              {uploadProgress.name}
            </span>
          </div>
          <div className={`mt-1 text-xs ${
            uploadProgress.status === 'error' ? 'text-red-500' : 
            uploadProgress.status === 'ready' ? 'text-green-500' : 
            'text-purple-500'
          }`}>
            {uploadProgress.status === 'error' 
              ? `Error: ${uploadProgress.error}` 
              : uploadProgress.status === 'ready'
              ? 'Ready'
              : `${uploadProgress.status}...`
            }
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentUpload;
