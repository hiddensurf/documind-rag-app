import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import MainContent from './components/MainContent';
import MindMapModal from './components/MindMapModal';
import CADViewer from './components/CADViewer';
import { useConversations } from './context/ConversationContext';
import { getDocuments } from './services/api';
import { initializeMermaid } from './utils/mermaid';
import DWGConverter from './components/DWGConverter';

initializeMermaid();

const App = () => {
  const [documents, setDocuments] = useState([]);
  const [showMindMap, setShowMindMap] = useState(false);
  const [currentMermaid, setCurrentMermaid] = useState('');
  const [showCADViewer, setShowCADViewer] = useState(false);
  const [currentCADDoc, setCurrentCADDoc] = useState(null);
  const [showDWGConverter, setShowDWGConverter] = useState(false);
  const [failedDWGFile, setFailedDWGFile] = useState(null);
  
  const { currentConversation, createNewConversation } = useConversations();

  // Load documents on mount
  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const docs = await getDocuments();
      setDocuments(docs);
    } catch (error) {
      console.error('Error loading documents:', error);
    }
  };

  const handleNewChat = async () => {
    console.log('App - Creating new chat with documents:', documents);
    const documentIds = documents.map(d => d.id);
    console.log('App - Document IDs:', documentIds);
    await createNewConversation(documentIds);
  };

  const handleViewMindMap = (mermaidCode) => {
    console.log('App - Opening mind map with code:', mermaidCode);
    if (mermaidCode) {
      setCurrentMermaid(mermaidCode);
      setShowMindMap(true);
    } else {
      console.error('App - No mermaid code provided!');
    }
  };

  const handleCloseMindMap = () => {
    console.log('App - Closing mind map');
    setShowMindMap(false);
    setTimeout(() => setCurrentMermaid(''), 300);
  };

  const handleViewCAD = (document) => {
    console.log('App - Opening CAD viewer for:', document.name);
    setCurrentCADDoc(document);
    setShowCADViewer(true);
  };

  const handleCloseCADViewer = () => {
    console.log('App - Closing CAD viewer');
    setShowCADViewer(false);
    setTimeout(() => setCurrentCADDoc(null), 300);
  };

  const handleDWGConversionNeeded = (fileName) => {
    console.log('DWG conversion needed for:', fileName);
    setFailedDWGFile(fileName);
    setShowDWGConverter(true);
  };

  const handleCloseDWGConverter = () => {
    setShowDWGConverter(false);
    setTimeout(() => setFailedDWGFile(null), 300);
  };

  return (
    <div className="flex h-screen bg-light-bg dark:bg-dark-bg text-light-text dark:text-dark-text transition-colors duration-200">
      <Sidebar 
        documents={documents}
        setDocuments={setDocuments}
        onNewChat={handleNewChat}
        onDocumentsUpdate={loadDocuments}
        onViewCAD={handleViewCAD}
        onDWGConversionNeeded={handleDWGConversionNeeded}
      />
      
      <MainContent
        documents={documents}
        currentConversation={currentConversation}
        onViewMindMap={handleViewMindMap}
      />

      {showMindMap && currentMermaid && (
        <MindMapModal
          mermaidCode={currentMermaid}
          onClose={handleCloseMindMap}
        />
      )}

      {showCADViewer && currentCADDoc && (
        <CADViewer
          documentId={currentCADDoc.id}
          documentName={currentCADDoc.name}
          onClose={handleCloseCADViewer}
        />
      )}
      
      {showDWGConverter && failedDWGFile && (
        <DWGConverter
          fileName={failedDWGFile}
          onClose={handleCloseDWGConverter}
        />
      )}
    </div>
  );
};

export default App;
