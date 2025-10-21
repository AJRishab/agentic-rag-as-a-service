import React, { useState, useEffect } from 'react';
import { Upload, Database, Network, Brain, Search, GitBranch, CheckCircle, AlertCircle, Loader, Eye, Zap, RefreshCw } from 'lucide-react';

const GraphRAGPlatform = () => {
  const [activeTab, setActiveTab] = useState('upload');
  const [documents, setDocuments] = useState([]);
  const [graphData, setGraphData] = useState(null);
  const [query, setQuery] = useState('');
  const [queryResult, setQueryResult] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [agentActivity, setAgentActivity] = useState([]);
  const [apiStatus, setApiStatus] = useState('checking');
  const [error, setError] = useState(null);

  // API Base URL - change this to your backend URL
  const API_BASE_URL = 'http://localhost:8000';

  // Check API health on mount
  useEffect(() => {
    checkApiHealth();
    loadDocuments();
    loadGraphStats();
  }, []);

  const checkApiHealth = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      if (response.ok) {
        setApiStatus('connected');
        setError(null);
      } else {
        setApiStatus('error');
        setError('API is not responding');
      }
    } catch (err) {
      setApiStatus('error');
      setError('Cannot connect to backend. Make sure the server is running on port 8000.');
    }
  };

  const loadDocuments = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/documents`);
      if (response.ok) {
        const data = await response.json();
        setDocuments(data);
      }
    } catch (err) {
      console.error('Failed to load documents:', err);
    }
  };

  const loadGraphStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/graph/stats`);
      if (response.ok) {
        const stats = await response.json();
        setGraphData({
          stats: stats,
          nodes: [],
          edges: []
        });
      }
    } catch (err) {
      console.error('Failed to load graph stats:', err);
    }
  };

  const handleDocumentUpload = async (file) => {
    setProcessing(true);
    setAgentActivity([]);
    setError(null);
    
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_BASE_URL}/api/documents/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const data = await response.json();
      
      // Display processing stages
      data.stages.forEach((stage, idx) => {
        setTimeout(() => {
          setAgentActivity(prev => [...prev, { 
            agent: stage.agent, 
            action: stage.action, 
            status: 'complete' 
          }]);
        }, idx * 400);
      });

      // Update documents and graph data
      setTimeout(() => {
        setProcessing(false);
        loadDocuments();
        loadGraphStats();
        
        // Show success message
        const newDoc = {
          name: file.name,
          processed: true,
          entities: data.graph_stats.entities,
          relationships: data.graph_stats.relationships
        };
        setDocuments(prev => [...prev, newDoc]);
      }, data.stages.length * 400);

    } catch (err) {
      setProcessing(false);
      setError(`Upload failed: ${err.message}`);
      setAgentActivity([]);
    }
  };

  const handleQuery = async () => {
    if (!query.trim()) return;
    
    setProcessing(true);
    setQueryResult(null);
    setAgentActivity([]);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          max_results: 10,
          use_vector: true,
          use_graph: true,
          use_filter: true
        }),
      });

      if (!response.ok) {
        throw new Error('Query failed');
      }

      const data = await response.json();
      
      // Display reasoning chain
      data.reasoning_chain.forEach((stage, idx) => {
        setTimeout(() => {
          setAgentActivity(prev => [...prev, { 
            agent: stage.agent, 
            action: stage.action, 
            status: 'complete' 
          }]);
        }, idx * 300);
      });

      // Show final result
      setTimeout(() => {
        setProcessing(false);
        setQueryResult({
          answer: data.answer,
          sources: data.sources,
          confidence: data.confidence
        });
      }, data.reasoning_chain.length * 300);

    } catch (err) {
      setProcessing(false);
      setError(`Query failed: ${err.message}`);
      setAgentActivity([]);
    }
  };

  const refreshData = () => {
    loadDocuments();
    loadGraphStats();
    checkApiHealth();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Network className="w-10 h-10 text-purple-400" />
              <div>
                <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                  Graph RAG Platform
                </h1>
                <p className="text-slate-300 text-sm">Intelligent Knowledge Retrieval with Agentic Reasoning</p>
              </div>
            </div>
            
            {/* API Status Indicator */}
            <div className="flex items-center gap-3">
              <button
                onClick={refreshData}
                className="p-2 hover:bg-slate-700/50 rounded-lg transition-all"
                title="Refresh data"
              >
                <RefreshCw className="w-5 h-5 text-slate-400" />
              </button>
              <div className="flex items-center gap-2 px-3 py-2 bg-slate-800/50 rounded-lg">
                <div className={`w-2 h-2 rounded-full ${
                  apiStatus === 'connected' ? 'bg-green-400 animate-pulse' :
                  apiStatus === 'error' ? 'bg-red-400' :
                  'bg-yellow-400 animate-pulse'
                }`} />
                <span className="text-xs text-slate-300">
                  {apiStatus === 'connected' ? 'Connected' :
                   apiStatus === 'error' ? 'Disconnected' :
                   'Checking...'}
                </span>
              </div>
            </div>
          </div>

          {/* Error Banner */}
          {error && (
            <div className="mt-4 p-4 bg-red-900/30 border border-red-500/50 rounded-lg flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-red-300">Error</p>
                <p className="text-xs text-red-200">{error}</p>
              </div>
            </div>
          )}
        </div>

        {/* Navigation Tabs */}
        <div className="flex gap-2 mb-6 bg-slate-800/50 p-2 rounded-lg backdrop-blur">
          {[
            { id: 'upload', label: 'Document Upload', icon: Upload },
            { id: 'graph', label: 'Knowledge Graph', icon: Database },
            { id: 'query', label: 'Agentic Query', icon: Brain }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all ${
                activeTab === tab.id
                  ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/50'
                  : 'text-slate-300 hover:bg-slate-700/50'
              }`}
            >
              <tab.icon className="w-5 h-5" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content Area */}
        <div className="bg-slate-800/30 backdrop-blur rounded-xl p-6 border border-slate-700/50 shadow-2xl">
          {activeTab === 'upload' && (
            <div>
              <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                <Upload className="w-6 h-6 text-purple-400" />
                Document Ingestion Pipeline
              </h2>
              
              <div className="mb-6 p-4 bg-slate-900/50 rounded-lg border-2 border-dashed border-purple-500/30 hover:border-purple-500/60 transition-all cursor-pointer">
                <input
                  type="file"
                  id="fileUpload"
                  className="hidden"
                  accept=".pdf,.docx,.txt"
                  onChange={(e) => {
                    if (e.target.files[0]) {
                      handleDocumentUpload(e.target.files[0]);
                    }
                  }}
                  disabled={apiStatus !== 'connected'}
                />
                <label htmlFor="fileUpload" className={`cursor-pointer block text-center py-8 ${
                  apiStatus !== 'connected' ? 'opacity-50 cursor-not-allowed' : ''
                }`}>
                  <Upload className="w-12 h-12 mx-auto mb-3 text-purple-400" />
                  <p className="text-lg font-medium mb-1">
                    {apiStatus === 'connected' ? 'Upload Documents' : 'Backend Not Connected'}
                  </p>
                  <p className="text-sm text-slate-400">
                    {apiStatus === 'connected' 
                      ? 'PDF, DOCX, TXT files supported' 
                      : 'Start the backend server to upload documents'}
                  </p>
                </label>
              </div>

              {/* Processing Pipeline */}
              {agentActivity.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                    <Zap className="w-5 h-5 text-yellow-400" />
                    Processing Pipeline
                  </h3>
                  <div className="space-y-2">
                    {agentActivity.map((activity, idx) => (
                      <div key={idx} className="flex items-center gap-3 p-3 bg-slate-900/50 rounded-lg">
                        <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />
                        <div className="flex-1">
                          <p className="font-medium text-sm">{activity.agent}</p>
                          <p className="text-xs text-slate-400">{activity.action}</p>
                        </div>
                      </div>
                    ))}
                    {processing && (
                      <div className="flex items-center gap-3 p-3 bg-purple-900/20 rounded-lg border border-purple-500/30">
                        <Loader className="w-5 h-5 text-purple-400 animate-spin" />
                        <p className="text-sm text-purple-300">Processing...</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Processed Documents */}
              {documents.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-3">Processed Documents ({documents.length})</h3>
                  <div className="space-y-2">
                    {documents.map((doc, idx) => (
                      <div key={idx} className="p-4 bg-slate-900/50 rounded-lg border border-slate-700/50">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="font-medium">{doc.filename || doc.name}</p>
                            <p className="text-sm text-slate-400">
                              {doc.graph_stats?.entities || doc.entities || 0} entities • {doc.graph_stats?.relationships || doc.relationships || 0} relationships
                            </p>
                          </div>
                          <CheckCircle className="w-6 h-6 text-green-400" />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {documents.length === 0 && !processing && (
                <div className="text-center py-12 text-slate-400">
                  <Upload className="w-16 h-16 mx-auto mb-3 opacity-50" />
                  <p>No documents uploaded yet</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'graph' && (
            <div>
              <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                <Database className="w-6 h-6 text-purple-400" />
                Knowledge Graph Visualization
              </h2>

              {graphData && graphData.stats ? (
                <div>
                  {/* Graph Stats */}
                  <div className="grid grid-cols-3 gap-4 mb-6">
                    <div className="p-4 bg-gradient-to-br from-blue-900/30 to-blue-800/30 rounded-lg border border-blue-500/30">
                      <p className="text-sm text-blue-300 mb-1">Total Entities</p>
                      <p className="text-3xl font-bold text-blue-400">{graphData.stats.entities || 0}</p>
                    </div>
                    <div className="p-4 bg-gradient-to-br from-purple-900/30 to-purple-800/30 rounded-lg border border-purple-500/30">
                      <p className="text-sm text-purple-300 mb-1">Relationships</p>
                      <p className="text-3xl font-bold text-purple-400">{graphData.stats.relationships || 0}</p>
                    </div>
                    <div className="p-4 bg-gradient-to-br from-pink-900/30 to-pink-800/30 rounded-lg border border-pink-500/30">
                      <p className="text-sm text-pink-300 mb-1">Attributes</p>
                      <p className="text-3xl font-bold text-pink-400">{graphData.stats.attributes || 0}</p>
                    </div>
                  </div>

                  {/* Entity Types */}
                  {graphData.stats.entity_types && Object.keys(graphData.stats.entity_types).length > 0 && (
                    <div className="mb-6">
                      <h3 className="text-lg font-semibold mb-3">Entity Types</h3>
                      <div className="grid grid-cols-2 gap-3">
                        {Object.entries(graphData.stats.entity_types).map(([type, count]) => (
                          <div key={type} className="p-3 bg-slate-900/50 rounded-lg border border-slate-700/50">
                            <div className="flex items-center justify-between">
                              <span className="font-medium">{type}</span>
                              <span className="text-sm text-slate-400">{count} nodes</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Visual Graph Representation */}
                  <div className="p-8 bg-slate-900/50 rounded-lg border border-slate-700/50">
                    <svg viewBox="0 0 600 400" className="w-full h-64">
                      <circle cx="300" cy="200" r="40" fill="#8b5cf6" opacity="0.8" />
                      <text x="300" y="205" textAnchor="middle" fill="white" fontSize="12">Entity</text>
                      
                      <circle cx="150" cy="200" r="35" fill="#ec4899" opacity="0.8" />
                      <text x="150" y="205" textAnchor="middle" fill="white" fontSize="12">Node</text>
                      
                      <circle cx="450" cy="200" r="35" fill="#06b6d4" opacity="0.8" />
                      <text x="450" y="205" textAnchor="middle" fill="white" fontSize="12">Data</text>
                      
                      <circle cx="300" cy="80" r="30" fill="#f59e0b" opacity="0.8" />
                      <text x="300" y="85" textAnchor="middle" fill="white" fontSize="11">Info</text>
                      
                      <line x1="260" y1="200" x2="185" y2="200" stroke="#8b5cf6" strokeWidth="2" />
                      <line x1="340" y1="200" x2="415" y2="200" stroke="#8b5cf6" strokeWidth="2" />
                      <line x1="300" y1="160" x2="300" y2="110" stroke="#8b5cf6" strokeWidth="2" />
                    </svg>
                    <p className="text-center text-sm text-slate-400 mt-4">
                      Simplified graph visualization • {graphData.stats.entities || 0} total nodes
                    </p>
                  </div>
                </div>
              ) : (
                <div className="text-center py-12 text-slate-400">
                  <Database className="w-16 h-16 mx-auto mb-3 opacity-50" />
                  <p>Upload documents to generate knowledge graph</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'query' && (
            <div>
              <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                <Brain className="w-6 h-6 text-purple-400" />
                Agentic Retrieval System
              </h2>

              {/* Query Input */}
              <div className="mb-6">
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder={apiStatus === 'connected' 
                      ? "Ask a question about your knowledge base..." 
                      : "Backend not connected..."}
                    className="flex-1 px-4 py-3 bg-slate-900/50 border border-slate-700/50 rounded-lg focus:border-purple-500 focus:outline-none text-white placeholder-slate-500"
                    onKeyPress={(e) => e.key === 'Enter' && handleQuery()}
                    disabled={apiStatus !== 'connected'}
                  />
                  <button
                    onClick={handleQuery}
                    disabled={processing || !query.trim() || apiStatus !== 'connected'}
                    className="px-6 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-slate-700 disabled:cursor-not-allowed rounded-lg font-medium transition-all flex items-center gap-2 shadow-lg shadow-purple-500/30"
                  >
                    <Search className="w-5 h-5" />
                    Query
                  </button>
                </div>
              </div>

              {/* Agent Activity */}
              {agentActivity.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                    <GitBranch className="w-5 h-5 text-purple-400" />
                    Agent Reasoning Chain
                  </h3>
                  <div className="space-y-2">
                    {agentActivity.map((activity, idx) => (
                      <div key={idx} className="flex items-start gap-3 p-3 bg-slate-900/50 rounded-lg">
                        <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                        <div className="flex-1">
                          <p className="font-medium text-sm text-purple-300">{activity.agent}</p>
                          <p className="text-sm text-slate-400">{activity.action}</p>
                        </div>
                      </div>
                    ))}
                    {processing && (
                      <div className="flex items-center gap-3 p-3 bg-purple-900/20 rounded-lg border border-purple-500/30">
                        <Loader className="w-5 h-5 text-purple-400 animate-spin" />
                        <p className="text-sm text-purple-300">Agents processing...</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Query Result */}
              {queryResult && (
                <div className="bg-gradient-to-br from-slate-900/80 to-slate-800/80 rounded-lg p-6 border border-purple-500/30 shadow-xl">
                  <div className="flex items-start gap-3 mb-4">
                    <CheckCircle className="w-6 h-6 text-green-400 flex-shrink-0 mt-1" />
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold mb-2">Answer</h3>
                      <p className="text-slate-200 leading-relaxed">{queryResult.answer}</p>
                    </div>
                  </div>

                  <div className="mt-4 pt-4 border-t border-slate-700/50">
                    <h4 className="text-sm font-semibold text-slate-400 mb-3">Evidence Sources ({queryResult.sources.length})</h4>
                    <div className="space-y-2">
                      {queryResult.sources.map((source, idx) => (
                        <div key={idx} className="p-3 bg-slate-900/50 rounded-lg text-sm">
                          <div className="flex items-center gap-2 mb-1">
                            <span className={`px-2 py-1 rounded text-xs font-medium ${
                              source.type === 'graph' ? 'bg-purple-900/50 text-purple-300' :
                              source.type === 'vector' ? 'bg-blue-900/50 text-blue-300' :
                              'bg-pink-900/50 text-pink-300'
                            }`}>
                              {source.type}
                            </span>
                            {source.confidence && (
                              <span className="text-slate-400">
                                {(source.confidence * 100).toFixed(0)}% confidence
                              </span>
                            )}
                          </div>
                          <p className="text-slate-300 text-xs">
                            {source.content}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="mt-4 flex items-center justify-between text-sm">
                    <span className="text-slate-400">Confidence Score</span>
                    <div className="flex items-center gap-2">
                      <div className="w-32 h-2 bg-slate-700 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-gradient-to-r from-green-500 to-green-400"
                          style={{ width: `${queryResult.confidence * 100}%` }}
                        />
                      </div>
                      <span className="font-medium text-green-400">
                        {(queryResult.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {!queryResult && !processing && (
                <div className="text-center py-12 text-slate-400">
                  <Search className="w-16 h-16 mx-auto mb-3 opacity-50" />
                  <p>
                    {apiStatus === 'connected' 
                      ? 'Enter a query to see agentic retrieval in action'
                      : 'Connect to backend to start querying'}
                  </p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Architecture Info */}
        <div className="mt-6 p-4 bg-slate-800/20 rounded-lg border border-slate-700/30">
          <h3 className="text-sm font-semibold text-slate-300 mb-2">System Architecture</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
            <div className="text-slate-400">
              <span className="text-purple-400 font-medium">Graph DB:</span> Neo4j / In-Memory
            </div>
            <div className="text-slate-400">
              <span className="text-purple-400 font-medium">Vector Store:</span> Built-in
            </div>
            <div className="text-slate-400">
              <span className="text-purple-400 font-medium">LLM:</span> Ollama / OpenAI
            </div>
            <div className="text-slate-400">
              <span className="text-purple-400 font-medium">Backend:</span> {apiStatus === 'connected' ? '✓ Running' : '✗ Offline'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GraphRAGPlatform;
