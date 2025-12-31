import { useState, useCallback } from 'react';
import { uploadDocument, deleteDocument as deleteDocumentAPI } from '../services/api';

export const useDocuments = () => {
  const [documents, setDocuments] = useState([]);
  const [uploadProgress, setUploadProgress] = useState(null);

  const handleUpload = useCallback(async (file) => {
    try {
      console.log('Starting upload for:', file.name);
      setUploadProgress({ name: file.name, status: 'uploading' });
      
      // Upload to backend
      const result = await uploadDocument(file);
      console.log('Upload successful:', result);
      
      setUploadProgress({ name: file.name, status: 'processing' });
      
      const newDoc = {
        id: result.id,
        name: result.name,
        uploadedAt: result.upload_date,
        size: `${(result.size / 1024).toFixed(2)} KB`
      };
      
      setDocuments(prev => [...prev, newDoc]);
      setUploadProgress({ name: file.name, status: 'ready' });
      
      await new Promise(resolve => setTimeout(resolve, 500));
      setUploadProgress(null);
      
      return newDoc;
    } catch (error) {
      console.error('Upload error:', error);
      console.error('Error details:', error.response?.data);
      setUploadProgress({ 
        name: file.name, 
        status: 'error',
        error: error.response?.data?.detail || error.message 
      });
      
      // Show error for 3 seconds
      await new Promise(resolve => setTimeout(resolve, 3000));
      setUploadProgress(null);
      throw error;
    }
  }, []);
  // Add state for DWG converter modal
const [showDWGConverter, setShowDWGConverter] = useState(false);
const [failedDWGFile, setFailedDWGFile] = useState(null);
  

  const deleteDocument = useCallback(async (docId) => {
    try {
      await deleteDocumentAPI(docId);
      setDocuments(prev => prev.filter(doc => doc.id !== docId));
    } catch (error) {
      console.error('Delete error:', error);
      throw error;
    }
  }, []);

  return {
    documents,
    uploadProgress,
    handleUpload,
    deleteDocument,
    setDocuments
  };
};
