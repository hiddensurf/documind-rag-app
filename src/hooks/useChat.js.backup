import { useState, useCallback } from 'react';
import { sendMessage as apiSendMessage, runAdvancedAnalysis } from '../services/api';

export function useChat(conversationId, documentIds = []) {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = useCallback(async (query) => {
    if (!conversationId) return;

    const userMessage = {
      role: 'user',
      content: query,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await apiSendMessage(conversationId, query, documentIds);
      
      const assistantMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: response.timestamp,
        hasMindmap: response.hasMindmap,
        mermaidCode: response.mermaidCode,
        sources: response.sources || []
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, there was an error processing your message. Please try again.',
        timestamp: new Date().toISOString(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [conversationId, documentIds]);

  const sendAdvancedAnalysis = useCallback(async (query) => {
    if (!conversationId) return;

    const userMessage = {
      role: 'user',
      content: `🤖 Advanced CAD Analysis: ${query}`,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await runAdvancedAnalysis(conversationId, query, documentIds);
      
      const assistantMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: response.timestamp,
        sources: response.sources || []
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error running advanced analysis:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, there was an error running the advanced analysis. Please try again.',
        timestamp: new Date().toISOString(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [conversationId, documentIds]);

  return {
    messages,
    setMessages,
    isLoading,
    sendMessage,
    sendAdvancedAnalysis
  };
}
