import React from 'react';
import { FileText, X } from 'lucide-react';

const DocumentBadge = ({ documents, onRemove, readonly = false }) => {
  if (!documents || documents.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2 px-4 py-3 border-b border-light-border dark:border-dark-border bg-light-sidebar dark:bg-dark-sidebar">
      <div className="text-xs text-light-textSecondary dark:text-dark-textSecondary flex items-center gap-2">
        <FileText className="w-4 h-4" />
        <span>Using {documents.length} document{documents.length > 1 ? 's' : ''}:</span>
      </div>
      {documents.map((doc) => (
        <div
          key={doc.id}
          className="flex items-center gap-1.5 px-2.5 py-1 bg-purple-500/10 border border-purple-500/20 rounded-lg text-xs group"
        >
          <span className="truncate max-w-[200px]" title={doc.name}>
            {doc.name}
          </span>
          {!readonly && onRemove && (
            <button
              onClick={() => onRemove(doc.id)}
              className="opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-500/20 rounded p-0.5"
            >
              <X className="w-3 h-3 text-red-500" />
            </button>
          )}
        </div>
      ))}
    </div>
  );
};

export default DocumentBadge;
