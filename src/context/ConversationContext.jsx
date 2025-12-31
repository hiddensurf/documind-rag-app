import React, { createContext, useContext, useState, useEffect } from 'react';
import { 
  createConversation, 
  getConversations, 
  deleteConversation as deleteConversationAPI,
  updateConversationTitle 
} from '../services/api';

const ConversationContext = createContext();

export const useConversations = () => {
  const context = useContext(ConversationContext);
  if (!context) {
    throw new Error('useConversations must be used within ConversationProvider');
  }
  return context;
};

export const ConversationProvider = ({ children }) => {
  const [conversations, setConversations] = useState([]);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Load conversations on mount
  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      setIsLoading(true);
      const data = await getConversations();
      setConversations(data);
    } catch (error) {
      console.error('Error loading conversations:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const createNewConversation = async (documentIds = []) => {
    try {
      const newConv = await createConversation(documentIds);
      setConversations(prev => [newConv, ...prev]);
      setCurrentConversation(newConv);
      return newConv;
    } catch (error) {
      console.error('Error creating conversation:', error);
      throw error;
    }
  };

  const selectConversation = (conversation) => {
    setCurrentConversation(conversation);
  };

  const updateTitle = async (convId, title) => {
    try {
      const updated = await updateConversationTitle(convId, title);
      setConversations(prev =>
        prev.map(conv => conv.id === convId ? updated : conv)
      );
      if (currentConversation?.id === convId) {
        setCurrentConversation(updated);
      }
    } catch (error) {
      console.error('Error updating title:', error);
      throw error;
    }
  };

  const deleteConversation = async (convId) => {
    try {
      await deleteConversationAPI(convId);
      setConversations(prev => prev.filter(conv => conv.id !== convId));
      if (currentConversation?.id === convId) {
        setCurrentConversation(null);
      }
    } catch (error) {
      console.error('Error deleting conversation:', error);
      throw error;
    }
  };

  return (
    <ConversationContext.Provider
      value={{
        conversations,
        currentConversation,
        isLoading,
        createNewConversation,
        selectConversation,
        updateTitle,
        deleteConversation,
        loadConversations,
      }}
    >
      {children}
    </ConversationContext.Provider>
  );
};
