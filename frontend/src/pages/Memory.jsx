import React, { useState, useEffect } from 'react';
import { Search, Folder, FileText, Trash2 } from 'lucide-react';
import '../styles/Memory.css';

export default function Memory() {
  const [activeTab, setActiveTab] = useState('conversations'); // conversations | projects
  const [conversations, setConversations] = useState([]);
  const [projects, setProjects] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Fetch conversations
  useEffect(() => {
    const fetchConversations = async () => {
      setIsLoading(true);
      try {
        const response = await fetch('http://localhost:8000/memory/conversations', {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        });
        if (response.ok) {
          const data = await response.json();
          setConversations(data.conversations || []);
        }
      } catch (error) {
        console.error('Error fetching conversations:', error);
      }
      setIsLoading(false);
    };

    if (activeTab === 'conversations') {
      fetchConversations();
    }
  }, [activeTab]);

  // Fetch projects
  useEffect(() => {
    const fetchProjects = async () => {
      setIsLoading(true);
      try {
        const response = await fetch('http://localhost:8000/memory/projects', {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        });
        if (response.ok) {
          const data = await response.json();
          setProjects(data.projects || []);
        }
      } catch (error) {
        console.error('Error fetching projects:', error);
      }
      setIsLoading(false);
    };

    if (activeTab === 'projects') {
      fetchProjects();
    }
  }, [activeTab]);

  // Search conversations
  const filteredConversations = conversations.filter(conv =>
    conv.title?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Search projects
  const filteredProjects = projects.filter(proj =>
    proj.name?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleDeleteConversation = async (conversationId) => {
    if (!window.confirm('Delete this conversation?')) return;
    try {
      await fetch(`http://localhost:8000/memory/conversations/${conversationId}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' }
      });
      setConversations(conversations.filter(c => c.id !== conversationId));
    } catch (error) {
      console.error('Error deleting conversation:', error);
    }
  };

  return (
    <div className="memory-container max-w-6xl mx-auto">
      
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg p-6 mb-6 shadow-lg">
        <h1 className="text-3xl font-bold text-white mb-2">🧠 Memory Explorer</h1>
        <p className="text-purple-100">View and manage your conversations and projects</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b border-slate-700">
        <button
          onClick={() => setActiveTab('conversations')}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === 'conversations'
              ? 'text-blue-400 border-b-2 border-blue-400'
              : 'text-slate-400 hover:text-slate-300'
          }`}
        >
          💬 Conversations
        </button>
        <button
          onClick={() => setActiveTab('projects')}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === 'projects'
              ? 'text-blue-400 border-b-2 border-blue-400'
              : 'text-slate-400 hover:text-slate-300'
          }`}
        >
          📁 Projects
        </button>
      </div>

      {/* Search Bar */}
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-3 text-slate-400" size={20} />
          <input
            type="text"
            placeholder={activeTab === 'conversations' ? 'Search conversations...' : 'Search projects...'}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-10 pr-4 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
        </div>
      </div>

      {/* Content */}
      {isLoading ? (
        <div className="text-center py-12">
          <div className="animate-spin inline-block w-8 h-8 border-4 border-slate-700 border-t-blue-400 rounded-full"></div>
          <p className="text-slate-400 mt-4">Loading...</p>
        </div>
      ) : activeTab === 'conversations' ? (
        <div className="space-y-3">
          {filteredConversations.length === 0 ? (
            <div className="text-center py-12 bg-slate-800/50 rounded-lg border border-slate-700">
              <p className="text-slate-400">No conversations found</p>
            </div>
          ) : (
            filteredConversations.map(conv => (
              <div
                key={conv.id}
                className="bg-slate-800 border border-slate-700 rounded-lg p-4 hover:border-slate-600 transition flex justify-between items-start"
              >
                <div className="flex-1">
                  <h3 className="text-white font-medium">{conv.title || 'Untitled'}</h3>
                  <p className="text-slate-400 text-sm mt-1">
                    {conv.message_count || 0} messages • {new Date(conv.created_at).toLocaleDateString()}
                  </p>
                </div>
                <button
                  onClick={() => handleDeleteConversation(conv.id)}
                  className="text-red-400 hover:text-red-300 p-2 hover:bg-red-500/10 rounded-lg transition"
                  title="Delete conversation"
                >
                  <Trash2 size={20} />
                </button>
              </div>
            ))
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredProjects.length === 0 ? (
            <div className="col-span-full text-center py-12 bg-slate-800/50 rounded-lg border border-slate-700">
              <p className="text-slate-400">No projects found</p>
            </div>
          ) : (
            filteredProjects.map(proj => (
              <div
                key={proj.id}
                className="bg-slate-800 border border-slate-700 rounded-lg p-4 hover:border-slate-600 transition"
              >
                <div className="flex items-start gap-3 mb-2">
                  <Folder className="text-blue-400 mt-1" size={20} />
                  <div className="flex-1">
                    <h3 className="text-white font-medium">{proj.name}</h3>
                    <p className="text-slate-400 text-sm">{proj.description || 'No description'}</p>
                  </div>
                </div>
                <div className="text-slate-500 text-xs mt-3">
                  📄 {proj.document_count || 0} documents • {new Date(proj.created_at).toLocaleDateString()}
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
