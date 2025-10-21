import React, { useState, useEffect } from 'react';
import { Upload, Database, Network, Brain, Search, GitBranch, CheckCircle, AlertCircle, Loader, Trash2, RefreshCw } from 'lucide-react';

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
  const [deleting, setDeleting] = useState({});

  const API_BASE_URL = 'http://localhost:8000';

  // Check API health on mount
  useEffect(() => {
    checkApiHealth();
    loadDocuments();
    loadGraphData();
  }, []);

  const checkApiHealth = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/`);
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

  const loadGraphData = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/graph/visualize`);
      if (response.ok) {
        const vizData = await response.json();
        setGraphData(vizData);
      }
    } catch (err) {
      console.error('Failed to load graph data:', err);
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
        loadGraphData();
      }, data.stages.length * 400);

    } catch (err) {
      setProcessing(false);
      setError(`Upload failed: ${err.message}`);
      setAgentActivity([]);
    }
  };

  const handleDocumentDelete = async (documentId) => {
    if (!window.confirm('Are you sure you want to delete this document and all its associated data?')) {
      return;
    }
    
    setDeleting(prev => ({ ...prev, [documentId]: true }));
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/documents/${documentId}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Document not found');
        }
        throw new Error('Delete failed');
      }
      
      const result = await response.json();
      
      // Show success message
      setAgentActivity([{
        agent: 'Document Manager',
        action: `Deleted document: ${result.deleted_entities} entities, ${result.deleted_relationships} relationships removed`,
        status: 'complete'
      }]);
      
      // Refresh data
      setTimeout(() => {
        loadDocuments();
        loadGraphData();
        setAgentActivity([]);
      }, 2000);
      
    } catch (err) {
      setError(`Delete failed: ${err.message}`);
    } finally {
      setDeleting(prev => ({ ...prev, [documentId]: false }));
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
    loadGraphData();
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
                          <div className="flex-1">
                            <p className="font-medium">{doc.filename || doc.name}</p>
                            <p className="text-sm text-slate-400">
                              {doc.graph_stats?.entities || doc.entities || 0} entities • {doc.graph_stats?.relationships || doc.relationships || 0} relationships
                            </p>
                          </div>
                          <div className="flex items-center gap-2">
                            <CheckCircle className="w-6 h-6 text-green-400" />
                            {doc.id && (
                              <button
                                onClick={() => handleDocumentDelete(doc.id)}
                                disabled={deleting[doc.id]}
                                className="p-2 hover:bg-red-900/30 rounded-lg transition-all group disabled:opacity-50 disabled:cursor-not-allowed"
                                title="Delete document"
                              >
                                {deleting[doc.id] ? (
                                  <Loader className="w-4 h-4 text-red-400 animate-spin" />
                                ) : (
                                  <Trash2 className="w-4 h-4 text-slate-400 group-hover:text-red-400" />
                                )}
                              </button>
                            )}
                          </div>
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

                  {/* Dynamic Graph Visualization */}
                  <div className="p-6 bg-slate-900/50 rounded-lg border border-slate-700/50 mb-6">
                    <h4 className="text-sm font-semibold text-slate-300 mb-4">Interactive Graph Visualization</h4>
                    <div className="w-full overflow-x-auto">
                      <svg viewBox="0 0 800 600" className="w-full h-96 bg-slate-950/30 rounded">
                        {/* Background grid */}
                        <defs>
                          <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                            <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#374151" strokeWidth="0.5" opacity="0.3"/>
                          </pattern>
                        </defs>
                        <rect width="100%" height="100%" fill="url(#grid)" />
                        
                        {/* Render edges */}
                        {graphData.edges && graphData.edges.map((edge, idx) => {
                          const sourceIndex = graphData.nodes.findIndex(n => n.id === edge.from);
                          const targetIndex = graphData.nodes.findIndex(n => n.id === edge.to);
                          
                          if (sourceIndex === -1 || targetIndex === -1) return null;
                          
                          const centerX = 400;
                          const centerY = 300;
                          const radius = Math.min(250, 150 + graphData.nodes.length * 8);
                          
                          const sourceAngle = (sourceIndex / graphData.nodes.length) * 2 * Math.PI;
                          const targetAngle = (targetIndex / graphData.nodes.length) * 2 * Math.PI;
                          
                          const sourceX = centerX + Math.cos(sourceAngle) * radius;
                          const sourceY = centerY + Math.sin(sourceAngle) * radius;
                          const targetX = centerX + Math.cos(targetAngle) * radius;
                          const targetY = centerY + Math.sin(targetAngle) * radius;
                          
                          return (
                            <line 
                              key={`edge-${idx}`}
                              x1={sourceX} y1={sourceY} 
                              x2={targetX} y2={targetY}
                              stroke="#6366f1" 
                              strokeWidth="1.5" 
                              opacity="0.6"
                              markerEnd="url(#arrowhead)"
                            />
                          );
                        })}
                        
                        {/* Arrow marker */}
                        <defs>
                          <marker id="arrowhead" markerWidth="10" markerHeight="7" 
                                  refX="9" refY="3.5" orient="auto">
                            <polygon points="0 0, 10 3.5, 0 7" fill="#6366f1" opacity="0.6" />
                          </marker>
                        </defs>
                        
                        {/* Render nodes */}
                        {graphData.nodes && graphData.nodes.map((node, idx) => {
                          const centerX = 400;
                          const centerY = 300;
                          const radius = Math.min(250, 150 + graphData.nodes.length * 8);
                          const angle = (idx / graphData.nodes.length) * 2 * Math.PI;
                          
                          const x = centerX + Math.cos(angle) * radius;
                          const y = centerY + Math.sin(angle) * radius;
                          
                          const colors = {
                            'Document': '#8b5cf6',
                            'Person': '#3b82f6',
                            'Organization': '#10b981',
                            'Location': '#f59e0b',
                            'Project': '#ec4899',
                            'Department': '#6366f1',
                            'Position': '#ef4444',
                            'Date': '#f97316',
                            'Entity': '#64748b'
                          };
                          const color = colors[node.type] || '#64748b';
                          const nodeRadius = node.type === 'Document' ? 25 : 18;
                          
                          return (
                            <g key={node.id}>
                              <circle 
                                cx={x} cy={y} r={nodeRadius}
                                fill={color} 
                                opacity="0.8"
                                stroke="white" 
                                strokeWidth="2"
                              />
                              <text 
                                x={x} y={y + nodeRadius + 15} 
                                textAnchor="middle" 
                                fill="#e2e8f0" 
                                fontSize="9"
                              >
                                {node.label.length > 12 ? node.label.substring(0, 12) + '...' : node.label}
                              </text>
                              <text 
                                x={x} y={y + nodeRadius + 28} 
                                textAnchor="middle" 
                                fill="#94a3b8" 
                                fontSize="7"
                              >
                                {node.type}
                              </text>
                            </g>
                          );
                        })}
                      </svg>
                    </div>
                  </div>

                  {/* Summary Cards */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-4 bg-slate-900/50 rounded-lg border border-slate-700/50">
                      <h4 className="text-sm font-semibold text-slate-300 mb-3">Key Entities</h4>
                      <div className="space-y-1">
                        {graphData.nodes && graphData.nodes.filter(n => n.type !== 'Document').slice(0, 5).map(node => (
                          <div key={node.id} className="text-xs text-slate-400 truncate">
                            {node.label}
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="p-4 bg-slate-900/50 rounded-lg border border-slate-700/50">
                      <h4 className="text-sm font-semibold text-slate-300 mb-3">Connections</h4>
                      <div className="space-y-1">
                        {graphData.edges && graphData.edges.slice(0, 5).map((edge, idx) => (
                          <div key={idx} className="text-xs text-slate-500 truncate">
                            {graphData.nodes.find(n => n.id === edge.from)?.label || edge.from} → {graphData.nodes.find(n => n.id === edge.to)?.label || edge.to}
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="p-4 bg-slate-900/50 rounded-lg border border-slate-700/50">
                      <h4 className="text-sm font-semibold text-slate-300 mb-3">Graph Info</h4>
                      <div className="space-y-1 text-xs text-slate-400">
                        <div>Nodes: {graphData.nodes?.length || 0}</div>
                        <div>Edges: {graphData.edges?.length || 0}</div>
                        <div>Density: {graphData.nodes?.length ? ((graphData.edges?.length || 0) / graphData.nodes.length).toFixed(2) : 0}</div>
                      </div>
                    </div>
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
                      ? "💬 Ask me anything about your documents... (e.g., 'What company is this about?')" 
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

              {/* Query Result - Conversational */}
              {queryResult && (
                <div className="bg-gradient-to-br from-slate-900/80 to-slate-800/80 rounded-lg p-6 border border-purple-500/30 shadow-xl">
                  <div className="flex items-start gap-3 mb-4">
                    <div className="w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center text-sm">
                      🤖
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold mb-2 text-purple-300">AI Assistant</h3>
                      <div className="bg-slate-800/50 rounded-lg p-4 mb-4">
                        <p className="text-slate-200 leading-relaxed">{queryResult.answer}</p>
                      </div>
                    </div>
                  </div>

                  <div className="mt-4 pt-4 border-t border-slate-700/50">
                    <h4 className="text-sm font-semibold text-slate-400 mb-3">Evidence Sources ({queryResult.sources?.length || 0})</h4>
                    <div className="space-y-2">
                      {queryResult.sources?.map((source, idx) => (
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
                          style={{ width: `${(queryResult.confidence || 0) * 100}%` }}
                        />
                      </div>
                      <span className="font-medium text-green-400">
                        {((queryResult.confidence || 0) * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {!queryResult && !processing && (
                <div className="text-center py-12 text-slate-400">
                  <div className="w-16 h-16 mx-auto mb-4 bg-slate-800/50 rounded-full flex items-center justify-center">
                    💬
                  </div>
                  <h3 className="text-lg font-medium mb-2 text-slate-300">Start a Conversation</h3>
                  <p className="text-sm mb-4">
                    {apiStatus === 'connected' 
                      ? 'Ask me anything about your uploaded documents'
                      : 'Connect to backend to start chatting'}
                  </p>
                  {apiStatus === 'connected' && (
                    <div className="text-xs text-slate-500 space-y-1">
                      <p>Try asking:</p>
                      <div className="space-y-1">
                        <p>• "What company is this document about?"</p>
                        <p>• "What kind of financial information is included?"</p>
                        <p>• "What time period does this cover?"</p>
                      </div>
                    </div>
                  )}
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
              <span className="text-purple-400 font-medium">LLM:</span> TinyLlama
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