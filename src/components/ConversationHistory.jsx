import React, { useState } from 'react';
import { MessageSquare, Trash2, Edit2, Check, X, Plus } from 'lucide-react';
import { useConversations } from '../context/ConversationContext';

const ConversationHistory = ({ onNewChat }) => {
  const { 
    conversations, 
    currentConversation, 
    selectConversation, 
    deleteConversation,
    updateTitle 
  } = useConversations();
  
  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState('');

  const handleStartEdit = (conv) => {
    setEditingId(conv.id);
    setEditTitle(conv.title);
  };

  const handleSaveEdit = async (convId) => {
    if (editTitle.trim()) {
      await updateTitle(convId, editTitle);
    }
    setEditingId(null);
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditTitle('');
  };

  const handleDelete = async (e, convId) => {
    e.stopPropagation();
    if (confirm('Delete this conversation?')) {
      await deleteConversation(convId);
    }
  };

  const formatDate = (isoString) => {
    const date = new Date(isoString);
    const now = new Date();
    const diff = now - date;
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days} days ago`;
    return date.toLocaleDateString();
  };

  // Group conversations by date
  const groupedConversations = conversations.reduce((groups, conv) => {
    const date = formatDate(conv.updated_at);
    if (!groups[date]) {
      groups[date] = [];
    }
    groups[date].push(conv);
    return groups;
  }, {});

  return (
    <div className="flex-1 overflow-y-auto p-2">
      {/* New Chat Button */}
      <button
        onClick={onNewChat}
        className="w-full mb-4 px-3 py-2.5 bg-light-hover dark:bg-dark-hover hover:bg-light-border dark:hover:bg-dark-border rounded-xl transition-all flex items-center gap-2 text-sm font-medium group"
      >
        <Plus className="w-4 h-4 group-hover:rotate-90 transition-transform" />
        New Chat
      </button>

      {/* Conversation List */}
      {conversations.length === 0 ? (
        <div className="text-center text-light-textSecondary dark:text-dark-textSecondary text-sm py-8">
          No conversations yet
        </div>
      ) : (
        <div className="space-y-4">
          {Object.entries(groupedConversations).map(([date, convs]) => (
            <div key={date}>
              <div className="text-xs font-semibold text-light-textSecondary dark:text-dark-textSecondary mb-2 px-2">
                {date}
              </div>
              <div className="space-y-1">
                {convs.map((conv) => (
                  <div
                    key={conv.id}
                    onClick={() => !editingId && selectConversation(conv)}
                    className={`group relative px-3 py-2.5 rounded-xl cursor-pointer transition-all ${
                      currentConversation?.id === conv.id
                        ? 'bg-light-border dark:bg-dark-border'
                        : 'hover:bg-light-hover dark:hover:bg-dark-hover'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <MessageSquare className="w-4 h-4 flex-shrink-0 text-light-textSecondary dark:text-dark-textSecondary" />
                      
                      {editingId === conv.id ? (
                        <div className="flex-1 flex items-center gap-1">
                          <input
                            type="text"
                            value={editTitle}
                            onChange={(e) => setEditTitle(e.target.value)}
                            onKeyPress={(e) => {
                              if (e.key === 'Enter') handleSaveEdit(conv.id);
                              if (e.key === 'Escape') handleCancelEdit();
                            }}
                            className="flex-1 bg-light-bg dark:bg-dark-bg border border-light-border dark:border-dark-border rounded px-2 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-purple-500"
                            autoFocus
                          />
                          <button
                            onClick={() => handleSaveEdit(conv.id)}
                            className="p-1 hover:bg-green-500/10 rounded"
                          >
                            <Check className="w-4 h-4 text-green-500" />
                          </button>
                          <button
                            onClick={handleCancelEdit}
                            className="p-1 hover:bg-red-500/10 rounded"
                          >
                            <X className="w-4 h-4 text-red-500" />
                          </button>
                        </div>
                      ) : (
                        <>
                          <span className="flex-1 text-sm truncate">
                            {conv.title}
                          </span>
                          <div className="opacity-0 group-hover:opacity-100 flex items-center gap-1">
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleStartEdit(conv);
                              }}
                              className="p-1 hover:bg-light-border dark:hover:bg-dark-border rounded"
                            >
                              <Edit2 className="w-3.5 h-3.5" />
                            </button>
                            <button
                              onClick={(e) => handleDelete(e, conv.id)}
                              className="p-1 hover:bg-red-500/10 rounded"
                            >
                              <Trash2 className="w-3.5 h-3.5 text-red-500" />
                            </button>
                          </div>
                        </>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ConversationHistory;
