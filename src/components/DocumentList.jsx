import React from 'react';
import { FileText, Trash2, Box } from 'lucide-react';

const DocumentList = ({ documents, onDeleteDocument, onViewCAD }) => {
  // Remove duplicates based on ID
  const uniqueDocuments = documents.reduce((acc, doc) => {
    if (!acc.find(d => d.id === doc.id)) {
      acc.push(doc);
    }
    return acc;
  }, []);

  const [deleting, setDeleting] = React.useState(null);

  const handleDelete = async (docId) => {
    if (!confirm('Are you sure you want to delete this document? It will be removed from the vector database and all conversations.')) {
      return;
    }
    
    setDeleting(docId);
    try {
      await onDeleteDocument(docId);
    } catch (error) {
      console.error('Delete failed:', error);
      alert('Failed to delete document: ' + error.message);
    } finally {
      setDeleting(null);
    }
  };

  const isCADFile = (filename) => {
    const lower = filename.toLowerCase();
    return lower.endsWith('.dwg') || lower.endsWith('.dxf');
  };

  const handleDocumentClick = (doc) => {
    if (isCADFile(doc.name) && onViewCAD) {
      onViewCAD(doc);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto p-4">
      {uniqueDocuments.length === 0 ? (
        <div className="text-center text-light-textSecondary dark:text-dark-textSecondary text-sm mt-8">
          No documents uploaded
        </div>
      ) : (
        <div className="space-y-2">
          {uniqueDocuments.map(doc => (
            <div
              key={doc.id}
              onClick={() => handleDocumentClick(doc)}
              className={`p-3 bg-light-hover dark:bg-dark-hover hover:bg-light-border dark:hover:bg-dark-border rounded-xl transition-all group relative ${
                isCADFile(doc.name) ? 'cursor-pointer' : ''
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  {/* Icon */}
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${
                    isCADFile(doc.name)
                      ? 'bg-gradient-to-br from-blue-500 to-cyan-500'
                      : 'bg-gradient-to-br from-purple-500 to-pink-500'
                  }`}>
                    {isCADFile(doc.name) ? (
                      <Box className="w-5 h-5 text-white" />
                    ) : (
                      <FileText className="w-5 h-5 text-white" />
                    )}
                  </div>
                  
                  {/* Document Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm font-medium truncate" title={doc.name}>
                        {doc.name}
                      </span>
                      {isCADFile(doc.name) && (
                        <span className="text-xs px-2 py-0.5 bg-blue-500/10 text-blue-500 rounded-full">
                          CAD
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-light-textSecondary dark:text-dark-textSecondary">
                      {(doc.size / 1024).toFixed(1)} KB
                      {isCADFile(doc.name) && ' • Click to view'}
                    </div>
                  </div>
                </div>
                
                {/* Delete Button */}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDelete(doc.id);
                  }}
                  disabled={deleting === doc.id}
                  className="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 hover:bg-red-500/10 rounded-lg disabled:opacity-50"
                >
                  {deleting === doc.id ? (
                    <div className="w-4 h-4 border-2 border-red-500 border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <Trash2 className="w-4 h-4 text-red-500" />
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default DocumentList;