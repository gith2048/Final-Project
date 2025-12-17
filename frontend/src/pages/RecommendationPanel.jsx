import React, { useState } from 'react';

export default function RecommendationPanel({ data }) {
  const [activeTab, setActiveTab] = useState('models'); // Changed default from 'overview' to 'models'
  
  if (!data || data.error) return null;

  // Normalize different response formats to a consistent object
  const normalize = () => {
    const out = { 
      lstm: null, 
      random_forest: null, 
      isolation_forest: null, 
      thresholds: data.thresholds || {}, 
      overall_summary: data.overall_summary || "",
      recommendations: data.recommendations || null
    };

    if (data.lstm) out.lstm = data.lstm;
    else if (data.forecast) out.lstm = { issue: "LSTM Forecast", forecast: data.forecast };

    if (data.random_forest && typeof data.random_forest === "object") out.random_forest = data.random_forest;
    else if (typeof data.random_forest === "number") {
      const rf = data.random_forest;
      const label = rf === 2 ? "Critical" : rf === 1 ? "Warning" : "Normal";
      out.random_forest = { issue: label, pred: rf };
    }

    if (data.isolation_forest && typeof data.isolation_forest === "object") out.isolation_forest = data.isolation_forest;
    else if (typeof data.isolation_forest === "number") {
      const iso = data.isolation_forest;
      out.isolation_forest = { issue: iso === -1 ? "Anomaly" : "Normal", pred: iso, score: data.iso_score };
    }
    return out;
  };

  const obj = normalize();

  const getStatusConfig = (issue = "") => {
    const t = (issue || "").toLowerCase();
    if (t.includes("critical") || t.includes("anomaly") || t.includes("🚨")) {
      return {
        color: "red",
        bgColor: "bg-red-50",
        borderColor: "border-red-200",
        textColor: "text-red-800",
        iconColor: "text-red-500",
        icon: "🚨"
      };
    }
    if (t.includes("high") || t.includes("warning") || t.includes("⚠")) {
      return {
        color: "yellow",
        bgColor: "bg-yellow-50",
        borderColor: "border-yellow-200",
        textColor: "text-yellow-800",
        iconColor: "text-yellow-500",
        icon: "⚠️"
      };
    }
    return {
      color: "green",
      bgColor: "bg-green-50",
      borderColor: "border-green-200",
      textColor: "text-green-800",
      iconColor: "text-green-500",
      icon: "✅"
    };
  };

  const getModelIcon = (modelName) => {
    switch (modelName) {
      case 'LSTM': return '🧠';
      case 'Random Forest': return '🌲';
      case 'Isolation Forest': return '🔍';
      default: return '📊';
    }
  };

  const getPriorityBadge = (priority) => {
    const configs = {
      critical: { bg: 'bg-red-100', text: 'text-red-800', border: 'border-red-200' },
      high: { bg: 'bg-orange-100', text: 'text-orange-800', border: 'border-orange-200' },
      medium: { bg: 'bg-yellow-100', text: 'text-yellow-800', border: 'border-yellow-200' },
      low: { bg: 'bg-green-100', text: 'text-green-800', border: 'border-green-200' }
    };
    const config = configs[priority] || configs.medium;
    
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${config.bg} ${config.text} ${config.border}`}>
        {priority?.toUpperCase()}
      </span>
    );
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden modern-card animate-fade-in-up">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 px-8 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">AI Analysis Results</h2>
              <p className="text-blue-100">Machine learning insights and recommendations</p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-white/80 text-sm">Analysis Complete</div>
            <div className="text-white font-semibold">{new Date().toLocaleTimeString()}</div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8 px-8">
          {[
            // { id: 'overview', label: 'Overview', icon: '📊' }, // COMMENTED OUT
            { id: 'models', label: 'AI Models', icon: '🤖' },
            { id: 'recommendations', label: 'Recommendations', icon: '💡' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="p-8">
        {/* OVERVIEW SECTION - COMMENTED OUT */}
        {/* {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-6 border border-gray-200">
              <div className="flex items-start space-x-4">
                <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center flex-shrink-0">
                  <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">System Health Summary</h3>
                  <div className="prose prose-sm text-gray-700">
                    <p className="whitespace-pre-line leading-relaxed">{obj.overall_summary}</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[obj.lstm, obj.random_forest, obj.isolation_forest].filter(Boolean).map((model, index) => {
                const modelNames = ['LSTM Neural Network', 'Random Forest', 'Isolation Forest'];
                const config = getStatusConfig(model.issue);
                
                return (
                  <div key={index} className={`${config.bgColor} ${config.borderColor} border rounded-xl p-4`}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-600">{modelNames[index]}</span>
                      <span className="text-lg">{getModelIcon(modelNames[index])}</span>
                    </div>
                    <div className={`text-lg font-semibold ${config.textColor}`}>
                      {model.issue}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )} */}

        {activeTab === 'models' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {[
              ['LSTM Neural Network', obj.lstm, '🧠'],
              ['Random Forest', obj.random_forest, '🌲'],
              ['Isolation Forest', obj.isolation_forest, '🔍']
            ].map(([title, block, icon]) => {
              if (!block) return null;
              const config = getStatusConfig(block.issue);
              
              return (
                <div key={title} className="bg-white border border-gray-200 rounded-xl shadow-sm hover:shadow-md transition-shadow">
                  {/* Model Header */}
                  <div className={`${config.bgColor} ${config.borderColor} border-b px-6 py-4`}>
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl">{icon}</span>
                      <div>
                        <h3 className="font-semibold text-gray-900">{title}</h3>
                        <div className="flex items-center space-x-2 mt-1">
                          <span className={`text-sm ${config.textColor} font-medium`}>
                            {block.issue}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Model Content */}
                  <div className="p-6 space-y-4">
                    {block.cause && (
                      <div>
                        <h4 className="text-sm font-medium text-gray-900 mb-2">Root Cause</h4>
                        <p className="text-sm text-gray-600 bg-gray-50 rounded-lg p-3">{block.cause}</p>
                      </div>
                    )}

                    {block.solution && (
                      <div>
                        <h4 className="text-sm font-medium text-gray-900 mb-2">Recommended Action</h4>
                        <p className="text-sm text-gray-600 bg-blue-50 rounded-lg p-3">{block.solution}</p>
                      </div>
                    )}

                    {block.forecast && (
                      <div>
                        <h4 className="text-sm font-medium text-gray-900 mb-3">Forecast (Next Cycle)</h4>
                        <div className="grid grid-cols-1 gap-2">
                          {[
                            { label: 'Temperature', value: block.forecast.temperature, unit: '°C', color: 'text-red-600' },
                            { label: 'Vibration', value: block.forecast.vibration, unit: 'mm/s', color: 'text-blue-600' },
                            { label: 'Speed', value: block.forecast.speed, unit: 'RPM', color: 'text-green-600' }
                          ].map((item) => (
                            <div key={item.label} className="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg">
                              <span className="text-sm text-gray-600">{item.label}</span>
                              <span className={`text-sm font-semibold ${item.color}`}>
                                {Number(item.value).toFixed(2)} {item.unit}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {block.score !== undefined && (
                      <div>
                        <h4 className="text-sm font-medium text-gray-900 mb-2">Confidence Score</h4>
                        <div className="flex items-center space-x-3">
                          <div className="flex-1 bg-gray-200 rounded-full h-2">
                            <div 
                              className={`h-2 rounded-full ${config.color === 'red' ? 'bg-red-500' : config.color === 'yellow' ? 'bg-yellow-500' : 'bg-green-500'}`}
                              style={{ width: `${Math.abs(block.score) * 100}%` }}
                            ></div>
                          </div>
                          <span className="text-sm font-medium text-gray-900">
                            {Number(block.score).toFixed(3)}
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {activeTab === 'recommendations' && obj.recommendations && (
          <div className="space-y-6">
            {/* Priority Banner */}
            <div className={`rounded-xl p-6 border-l-4 ${
              obj.recommendations.priority === 'critical' ? 'bg-red-50 border-red-400' :
              obj.recommendations.priority === 'high' ? 'bg-orange-50 border-orange-400' :
              obj.recommendations.priority === 'medium' ? 'bg-yellow-50 border-yellow-400' :
              'bg-green-50 border-green-400'
            }`}>
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Action Required</h3>
                  <p className="text-gray-600 mt-1">{obj.recommendations.summary}</p>
                </div>
                {getPriorityBadge(obj.recommendations.priority)}
              </div>
            </div>

            {/* Action Items */}
            {obj.recommendations.actions && obj.recommendations.actions.length > 0 && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900">Immediate Actions</h3>
                {obj.recommendations.actions.map((action, index) => (
                  <div key={index} className="bg-white border border-gray-200 rounded-xl shadow-sm">
                    <div className="p-6">
                      <div className="flex items-start space-x-4">
                        <span className="text-2xl flex-shrink-0">{action.icon}</span>
                        <div className="flex-1">
                          <h4 className="text-lg font-semibold text-gray-900 mb-2">{action.title}</h4>
                          
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                            <div>
                              <h5 className="text-sm font-medium text-gray-700 mb-2">Problem</h5>
                              <p className="text-sm text-gray-600 bg-red-50 rounded-lg p-3">{action.problem}</p>
                            </div>
                            <div>
                              <h5 className="text-sm font-medium text-gray-700 mb-2">Impact</h5>
                              <p className="text-sm text-gray-600 bg-orange-50 rounded-lg p-3">{action.impact}</p>
                            </div>
                          </div>

                          {action.immediate_actions && action.immediate_actions.length > 0 && (
                            <div className="mb-4">
                              <h5 className="text-sm font-medium text-gray-700 mb-2">⚡ Immediate Steps</h5>
                              <ul className="space-y-1">
                                {action.immediate_actions.map((step, stepIndex) => (
                                  <li key={stepIndex} className="text-sm text-gray-600 flex items-start space-x-2">
                                    <span className="text-blue-500 mt-1">•</span>
                                    <span>{step}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {action.resolution_steps && action.resolution_steps.length > 0 && (
                            <div className="mb-4">
                              <h5 className="text-sm font-medium text-gray-700 mb-2">🔧 Resolution Steps</h5>
                              <ol className="space-y-1">
                                {action.resolution_steps.map((step, stepIndex) => (
                                  <li key={stepIndex} className="text-sm text-gray-600 flex items-start space-x-2">
                                    <span className="text-green-500 font-medium mt-1">{stepIndex + 1}.</span>
                                    <span>{step}</span>
                                  </li>
                                ))}
                              </ol>
                            </div>
                          )}

                          {action.prevention && action.prevention.length > 0 && (
                            <div>
                              <h5 className="text-sm font-medium text-gray-700 mb-2">🛡️ Prevention</h5>
                              <ul className="space-y-1">
                                {action.prevention.map((prev, prevIndex) => (
                                  <li key={prevIndex} className="text-sm text-gray-600 flex items-start space-x-2">
                                    <span className="text-purple-500 mt-1">•</span>
                                    <span>{prev}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Preventive Actions */}
            {obj.recommendations.preventive && obj.recommendations.preventive.length > 0 && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900">Preventive Maintenance</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {obj.recommendations.preventive.map((prev, index) => (
                    <div key={index} className="bg-green-50 border border-green-200 rounded-xl p-4">
                      <div className="flex items-start space-x-3">
                        <span className="text-xl flex-shrink-0">{prev.icon}</span>
                        <div>
                          <h4 className="font-semibold text-green-800 mb-2">{prev.title}</h4>
                          <ul className="space-y-1">
                            {prev.actions.map((action, actionIndex) => (
                              <li key={actionIndex} className="text-sm text-green-700 flex items-start space-x-2">
                                <span className="text-green-500 mt-1">•</span>
                                <span>{action}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
