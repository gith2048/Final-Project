import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { getMachineCondition } from '../utils/thresholds';

const EarlyDetection = ({ currentData, selectedMachine, isVisible = true }) => {
  const [predictions, setPredictions] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  // Auto-refresh predictions every 15 seconds when visible
  useEffect(() => {
    if (!isVisible || !currentData || !selectedMachine) return;

    const fetchPredictions = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // Use the predict endpoint for fast predictions with existing models
        const response = await axios.post('http://localhost:5000/predict', {
          temperature: currentData.temperature || 0,
          vibration: currentData.vibration || 0,
          speed: currentData.speed || 0,
          sequence: [
            // Create a simple sequence for LSTM (last 10 data points)
            [currentData.temperature || 0, currentData.vibration || 0, currentData.speed || 0],
            [currentData.temperature || 0, currentData.vibration || 0, currentData.speed || 0],
            [currentData.temperature || 0, currentData.vibration || 0, currentData.speed || 0],
            [currentData.temperature || 0, currentData.vibration || 0, currentData.speed || 0],
            [currentData.temperature || 0, currentData.vibration || 0, currentData.speed || 0],
            [currentData.temperature || 0, currentData.vibration || 0, currentData.speed || 0],
            [currentData.temperature || 0, currentData.vibration || 0, currentData.speed || 0],
            [currentData.temperature || 0, currentData.vibration || 0, currentData.speed || 0],
            [currentData.temperature || 0, currentData.vibration || 0, currentData.speed || 0],
            [currentData.temperature || 0, currentData.vibration || 0, currentData.speed || 0]
          ]
        });

        if (response.data && response.data.lstm) {
          // Transform the response to match expected structure
          const transformedPredictions = {
            lstm_forecast: response.data.lstm.forecast,
            future_timeline: null // Not available in simple predict endpoint
          };
          setPredictions(transformedPredictions);
          setLastUpdate(new Date());
        }
      } catch (err) {
        console.error('Early detection error:', err);
        setError('Failed to fetch predictions');
      } finally {
        setLoading(false);
      }
    };

    // Initial fetch
    fetchPredictions();

    // Set up auto-refresh (every 15 seconds for fast predictions)
    const interval = setInterval(fetchPredictions, 15000); // 15 seconds

    return () => clearInterval(interval);
  }, [currentData, selectedMachine, isVisible]);

  // Use centralized threshold function
  // (getMachineCondition is imported from utils/thresholds.js)

  if (!isVisible) return null;

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 modern-card animate-fade-in-up">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div>
            <h3 className="text-lg font-bold text-gray-900">Early Detection System</h3>
            <p className="text-sm text-gray-600">AI-powered forecast using trained models</p>
          </div>
        </div>
        
        {/* Refresh indicator */}
        <div className="flex items-center space-x-2">
          {loading && (
            <svg className="animate-spin w-4 h-4 text-purple-500" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          )}
          {lastUpdate && (
            <span className="text-xs text-gray-500">
              Updated: {lastUpdate.toLocaleTimeString()}
            </span>
          )}
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
          <div className="flex items-center space-x-2">
            <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-red-700 text-sm">{error}</span>
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && !predictions && (
        <div className="flex items-center justify-center py-8">
          <div className="text-center">
            <svg className="animate-spin w-8 h-8 text-purple-500 mx-auto mb-2" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <p className="text-gray-600 text-sm">Analyzing machine patterns...</p>
          </div>
        </div>
      )}

      {/* Predictions Display */}
      {predictions && predictions.lstm_forecast && (
        <div className="space-y-4">
          {/* Current vs Predicted Comparison */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Current Condition */}
            <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
              <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center space-x-2">
                <span>🔄</span>
                <span>Current Condition</span>
              </h4>
              <div className="space-y-2">
                {[
                  { label: 'Temperature', value: currentData?.temperature || 0, unit: '°C', color: 'text-red-600' },
                  { label: 'Vibration', value: currentData?.vibration || 0, unit: 'mm/s', color: 'text-blue-600' },
                  { label: 'Speed', value: currentData?.speed || 0, unit: 'RPM', color: 'text-green-600' }
                ].map((item) => (
                  <div key={item.label} className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">{item.label}</span>
                    <span className={`text-sm font-semibold ${item.color}`}>
                      {Number(item.value).toFixed(2)} {item.unit}
                    </span>
                  </div>
                ))}
              </div>
              
              {/* Current Status */}
              {(() => {
                const condition = getMachineCondition(
                  currentData?.temperature || 0,
                  currentData?.vibration || 0,
                  currentData?.speed || 0
                );
                return (
                  <div className={`mt-3 p-2 rounded-lg ${condition.bgColor} ${condition.borderColor} border`}>
                    <div className="flex items-center space-x-2">
                      <span>{condition.icon}</span>
                      <span className={`text-sm font-semibold ${condition.color}`}>
                        {condition.status}
                      </span>
                    </div>
                  </div>
                );
              })()}
            </div>

            {/* Predicted Condition (10 minutes ahead) */}
            <div className="bg-purple-50 rounded-xl p-4 border border-purple-200">
              <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center space-x-2">
                <span>🔮</span>
                <span>Predicted (10 min)</span>
              </h4>
              <div className="space-y-2">
                {[
                  { label: 'Temperature', value: predictions.lstm_forecast.temperature, unit: '°C', color: 'text-red-600' },
                  { label: 'Vibration', value: predictions.lstm_forecast.vibration, unit: 'mm/s', color: 'text-blue-600' },
                  { label: 'Speed', value: predictions.lstm_forecast.speed, unit: 'RPM', color: 'text-green-600' }
                ].map((item) => (
                  <div key={item.label} className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">{item.label}</span>
                    <span className={`text-sm font-semibold ${item.color}`}>
                      {Number(item.value).toFixed(2)} {item.unit}
                    </span>
                  </div>
                ))}
              </div>
              
              {/* Predicted Status */}
              {(() => {
                const condition = getMachineCondition(
                  predictions.lstm_forecast.temperature,
                  predictions.lstm_forecast.vibration,
                  predictions.lstm_forecast.speed
                );
                return (
                  <div className={`mt-3 p-2 rounded-lg ${condition.bgColor} ${condition.borderColor} border`}>
                    <div className="flex items-center space-x-2">
                      <span>{condition.icon}</span>
                      <span className={`text-sm font-semibold ${condition.color}`}>
                        {condition.status}
                      </span>
                    </div>
                    <p className="text-xs text-gray-600 mt-1">{condition.description}</p>
                  </div>
                );
              })()}
            </div>
          </div>

          {/* Future Timeline (if available) */}
          {predictions.future_timeline && predictions.future_timeline.length > 0 && (
            <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl p-4 border border-indigo-200">
              <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center space-x-2">
                <span>📈</span>
                <span>30-Minute Trend Forecast</span>
              </h4>
              
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2">
                {predictions.future_timeline.slice(0, 6).map((prediction, index) => {
                  const minutes = (index + 1) * 5;
                  const condition = getMachineCondition(
                    prediction.temperature,
                    prediction.vibration,
                    prediction.speed
                  );
                  
                  return (
                    <div key={index} className="text-center">
                      <div className="text-xs text-gray-500 mb-1">+{minutes}min</div>
                      <div className={`w-8 h-8 mx-auto rounded-full flex items-center justify-center text-xs ${condition.bgColor} ${condition.borderColor} border`}>
                        {condition.icon}
                      </div>
                      <div className={`text-xs font-medium mt-1 ${condition.color}`}>
                        {condition.status}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Alert Messages */}
          {(() => {
            const currentCondition = getMachineCondition(
              currentData?.temperature || 0,
              currentData?.vibration || 0,
              currentData?.speed || 0
            );
            const predictedCondition = getMachineCondition(
              predictions.lstm_forecast.temperature,
              predictions.lstm_forecast.vibration,
              predictions.lstm_forecast.speed
            );

            // Check if condition is worsening
            const conditionLevels = { 'Healthy': 0, 'Satisfactory': 1, 'High Risk': 2, 'Critical': 3 };
            const currentLevel = conditionLevels[currentCondition.status] || 0;
            const predictedLevel = conditionLevels[predictedCondition.status] || 0;

            if (predictedLevel > currentLevel) {
              return (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="flex items-start space-x-3">
                    <svg className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16c-.77.833.192 2.5 1.732 2.5z" />
                    </svg>
                    <div>
                      <h5 className="text-sm font-semibold text-red-800">⚠️ Condition Deterioration Detected</h5>
                      <p className="text-sm text-red-700 mt-1">
                        Machine condition is predicted to change from <strong>{currentCondition.status}</strong> to <strong>{predictedCondition.status}</strong> in the next 10 minutes.
                      </p>
                      <p className="text-xs text-red-600 mt-2">
                        Recommended: Monitor closely and prepare for maintenance intervention.
                      </p>
                    </div>
                  </div>
                </div>
              );
            } else if (predictedLevel < currentLevel) {
              return (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-start space-x-3">
                    <svg className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div>
                      <h5 className="text-sm font-semibold text-green-800">✅ Condition Improvement Expected</h5>
                      <p className="text-sm text-green-700 mt-1">
                        Machine condition is predicted to improve from <strong>{currentCondition.status}</strong> to <strong>{predictedCondition.status}</strong> in the next 10 minutes.
                      </p>
                    </div>
                  </div>
                </div>
              );
            } else if (predictedCondition.status === 'Critical') {
              return (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="flex items-start space-x-3">
                    <svg className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div>
                      <h5 className="text-sm font-semibold text-red-800">🚨 Critical Condition Maintained</h5>
                      <p className="text-sm text-red-700 mt-1">
                        Machine will remain in <strong>Critical</strong> condition. Immediate intervention required.
                      </p>
                    </div>
                  </div>
                </div>
              );
            }

            return null;
          })()}
        </div>
      )}

      {/* No data state */}
      {!loading && !predictions && !error && (
        <div className="text-center py-8">
          <svg className="w-12 h-12 text-gray-400 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <p className="text-gray-600 text-sm">Select a machine to view early detection forecasts</p>
        </div>
      )}
    </div>
  );
};

export default EarlyDetection;