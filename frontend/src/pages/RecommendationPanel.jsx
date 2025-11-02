export default function RecommendationPanel({ data }) {
  if (!data || data.error) return null;

  const modelLabels = {
    lstm: "LSTM Forecast",
    random_forest: "Random Forest Classification",
    isolation_forest: "Isolation Forest Anomaly Detection"
  };

  const getSeverityColor = (issue) => {
    if (issue.includes("🚨")) return "border-red-500";
    if (issue.includes("⚠️")) return "border-yellow-500";
    return "border-green-500";
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {Object.entries(data).map(([model, rec]) => {
          if (model === "thresholds") return null;
          return (
            <div key={model} className={`bg-white p-4 rounded shadow border-l-4 ${getSeverityColor(rec.issue)}`}>
              <h3 className="font-bold text-lg mb-2">{modelLabels[model]}</h3>
              <p><strong>Issue:</strong> {rec.issue}</p>
              {rec.cause && <p><strong>Cause:</strong> {rec.cause}</p>}
              <p><strong>Solution:</strong> {rec.solution}</p>
              {rec.forecast_temperature && <p><strong>Forecast:</strong> {rec.forecast_temperature}°C</p>}
              {rec.score && <p><strong>Anomaly Score:</strong> {rec.score}</p>}
            </div>
          );
        })}
      </div>

      {data.thresholds && (
        <div className="bg-gray-50 p-4 rounded shadow">
          <h4 className="font-semibold text-lg mb-2">📊 Sensor Status</h4>
          <ul className="space-y-1">
            {Object.entries(data.thresholds).map(([key, val]) => (
              <li key={key}>
                <strong>{key.charAt(0).toUpperCase() + key.slice(1)}:</strong> {val.value} → {val.status}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}