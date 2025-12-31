import { useState, useEffect } from 'react';
import { useConversations } from '../context/ConversationContext';
import { useChat } from '../hooks/useChat';
import WelcomeScreen from './WelcomeScreen';
import ChatArea from './ChatArea';
import ChatInput from './ChatInput';
import DocumentBadge from './DocumentBadge';

export default function MainContent({ documents, currentConversation, onViewMindMap }) {
  const { updateConversationDocuments } = useConversations();
  const [activeDocuments, setActiveDocuments] = useState([]);

  const conversationId = currentConversation?.id;
  const documentIds = currentConversation?.documentIds || [];

  const { messages, setMessages, isLoading, sendMessage, sendAdvancedAnalysis, sendHybridAnalysis } = useChat(
    conversationId,
    documentIds
  );

  // Load messages when conversation changes
  useEffect(() => {
    if (currentConversation?.messages) {
      setMessages(currentConversation.messages);
    } else {
      setMessages([]);
    }
  }, [currentConversation, setMessages]);

  // Update active documents when conversation or documents change
  useEffect(() => {
    if (documentIds && documentIds.length > 0 && documents && documents.length > 0) {
      const active = documents.filter(doc => documentIds.includes(doc.id));
      setActiveDocuments(active);
    } else {
      setActiveDocuments([]);
    }
  }, [documentIds, documents]);

  // Check if any active documents are CAD files - IMPROVED DETECTION
  const hasCADDocuments = activeDocuments.some(doc => {
    const fileName = (doc.name || doc.filename || '').toLowerCase();
    const isCadExtension = fileName.endsWith('.dxf') || 
                          fileName.endsWith('.dwg') || 
                          fileName.endsWith('.dwf');
    const isCadFlag = doc.isCad || doc.is_cad;
    
    console.log('CAD Check:', {
      fileName,
      isCadExtension,
      isCadFlag,
      result: isCadExtension || isCadFlag
    });
    
    return isCadExtension || isCadFlag;
  });

  console.log('MainContent State:', {
    hasCADDocuments,
    activeDocuments: activeDocuments.length,
    documentNames: activeDocuments.map(d => d.name || d.filename)
  });

  if (!currentConversation) {
    return <WelcomeScreen />;
  }

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden">
      {activeDocuments.length > 0 && (
        <DocumentBadge documents={activeDocuments} />
      )}
      
      <ChatArea 
        messages={messages}
        isLoading={isLoading}
        onViewMindMap={onViewMindMap}
      />
      
      <ChatInput 
        onSendMessage={sendMessage}
        onAdvancedAnalysis={sendAdvancedAnalysis}
        onHybridAnalysis={sendHybridAnalysis}
        disabled={isLoading}
        hasCADDocuments={hasCADDocuments}
      />
    </div>
  );
}
