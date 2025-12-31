import React, { useState } from 'react';
import DocumentUpload from './DocumentUpload';
import DocumentList from './DocumentList';
import ConversationHistory from './ConversationHistory';
import ThemeToggle from './ThemeToggle';
import { FileText, Sparkles, MessageSquare } from 'lucide-react';
import { useDocuments } from '../hooks/useDocuments';
import { useConversations } from '../context/ConversationContext';
import { updateConversationDocuments } from '../services/api';

const Sidebar = ({ documents, setDocuments, onNewChat, onDocumentsUpdate, onViewCAD }) => {
  const { uploadProgress, handleUpload, deleteDocument } = useDocuments();
  const { currentConversation, loadConversations } = useConversations();
  const [activeTab, setActiveTab] = useState('chats');

  const onFilesSelected = async (files) => {
    for (const file of files) {
      try {
        const doc = await handleUpload(file);
        if (doc) {
          setDocuments(prev => [...prev, doc]);
          
          // Add document to current conversation
          if (currentConversation) {
            const newDocIds = [...(currentConversation.document_ids || []), doc.id];
            await updateConversationDocuments(currentConversation.id, newDocIds);
            await loadConversations();
          }
        }
      } catch (error) {
        console.error('Upload error:', error);
        
        // Check if it's a DWG conversion error
        const errorMessage = error.response?.data?.detail || error.message || '';
        if (file.name.toLowerCase().endsWith('.dwg') && 
            (errorMessage.includes('DWG') || errorMessage.includes('conversion'))) {
          // Show DWG converter modal
          if (onDWGConversionNeeded) {
            onDWGConversionNeeded(file.name);
          }
        } else {
          // Show generic error
          alert(`Failed to upload ${file.name}: ${errorMessage}`);
        }
      }
    }
    if (onDocumentsUpdate) {
      await onDocumentsUpdate();
    }
  };

  const onDeleteDocument = async (docId) => {
    await deleteDocument(docId);
    setDocuments(prev => prev.filter(doc => doc.id !== docId));
    if (onDocumentsUpdate) {
      await onDocumentsUpdate();
    }
  };

  return (
    <div className="w-64 bg-light-sidebar dark:bg-dark-sidebar border-r border-light-border dark:border-dark-border flex flex-col transition-colors duration-200">
      {/* Header */}
      <div className="p-4 border-b border-light-border dark:border-dark-border">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <h1 className="text-lg font-semibold">DocuMind</h1>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-light-border dark:border-dark-border">
        <button
          onClick={() => setActiveTab('chats')}
          className={`flex-1 px-4 py-3 text-sm font-medium transition-colors flex items-center justify-center gap-2 ${
            activeTab === 'chats'
              ? 'text-purple-500 border-b-2 border-purple-500'
              : 'text-light-textSecondary dark:text-dark-textSecondary hover:text-light-text dark:hover:text-dark-text'
          }`}
        >
          <MessageSquare className="w-4 h-4" />
          Chats
        </button>
        <button
          onClick={() => setActiveTab('documents')}
          className={`flex-1 px-4 py-3 text-sm font-medium transition-colors flex items-center justify-center gap-2 ${
            activeTab === 'documents'
              ? 'text-purple-500 border-b-2 border-purple-500'
              : 'text-light-textSecondary dark:text-dark-textSecondary hover:text-light-text dark:hover:text-dark-text'
          }`}
        >
          <FileText className="w-4 h-4" />
          Docs
        </button>
      </div>

      {/* Content */}
      {activeTab === 'chats' ? (
        <ConversationHistory onNewChat={onNewChat} />
      ) : (
        <>
          <DocumentUpload 
            onFilesSelected={onFilesSelected}
            uploadProgress={uploadProgress}
          />
          <DocumentList 
            documents={documents}
            onDeleteDocument={onDeleteDocument}
            onViewCAD={onViewCAD}
          />
        </>
      )}

      {/* Footer */}
      <div className="mt-auto p-4 border-t border-light-border dark:border-dark-border">
        {activeTab === 'documents' && (
          <div className="text-xs text-light-textSecondary dark:text-dark-textSecondary mb-3">
            Supported: PDF, DOCX, TXT, MD, DWG, DXF
          </div>
        )}
        <ThemeToggle />
      </div>
    </div>
  );
};

export default Sidebar;