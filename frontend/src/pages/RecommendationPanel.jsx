export default function RecommendationPanel({ data }) {
  // No data OR backend returned an error → don't render panel
  if (!data || data.error) return null;

  const modelLabels = {
    lstm: "LSTM Forecast",
    random_forest: "Random Forest Classification",
    isolation_forest: "Isolation Forest Anomaly Detection",
  };

  // 🔥 SAFE getSeverityColor — prevents crash if issue is missing
  const getSeverityColor = (issue = "") => {
    const text = issue.toLowerCase();
    if (text.includes("critical") || text.includes("🚨"))
      return "border-red-500";
    if (text.includes("high") || text.includes("⚠️"))
      return "border-yellow-500";
    return "border-green-500";
  };

  // 🔥 SAFE forecast renderer
  const renderForecast = (forecast) => {
    if (!forecast) return null;

    return (
      <div className="mt-2 text-sm text-gray-700 space-y-1">
        <p><strong>Forecast:</strong></p>
        <ul className="ml-4 list-disc">
          <li>Temperature: {forecast.temperature ?? "N/A"}°C</li>
          <li>Speed: {forecast.speed ?? "N/A"}</li>
          <li>Vibration: {forecast.vibration ?? "N/A"}</li>
        </ul>
      </div>
    );
  };

  return (
    <div className="space-y-6">

      {/* 🔹 ML MODEL CARDS */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {Object.entries(data).map(([model, rec]) => {
          // Skip these keys
          if (
            model === "thresholds" ||
            model === "overall_summary" ||
            model === "latest" ||
            model === "levels" ||
            model === "trends"
          )
            return null;

          // Skip items that are not objects (avoid crash)
          if (!rec || typeof rec !== "object") return null;

          const issueText = rec.issue || "No issue detected";

          return (
            <div
              key={model}
              className={`bg-white p-4 rounded shadow border-l-4 ${getSeverityColor(
                issueText
              )}`}
            >
              <h3 className="font-bold text-lg mb-2">
                {modelLabels[model] || model.replace("_", " ").toUpperCase()}
              </h3>

              <p><strong>Issue:</strong> {issueText}</p>

              {rec.cause && (
                <p><strong>Cause:</strong> {rec.cause}</p>
              )}

              <p><strong>Solution:</strong> {rec.solution || "No solution available"}</p>

              {rec.forecast && renderForecast(rec.forecast)}

              {rec.score !== undefined && (
                <p className="mt-2">
                  <strong>Anomaly Score:</strong> {rec.score}
                </p>
              )}
            </div>
          );
        })}
      </div>

      {/* 🔹 THRESHOLDS SECTION */}
      {data.thresholds && typeof data.thresholds === "object" && (
        <div className="bg-gray-50 p-4 rounded shadow">
          <h4 className="font-semibold text-lg mb-2">📊 Sensor Status</h4>
          <ul className="space-y-1">
            {Object.entries(data.thresholds).map(([key, val]) => (
              <li key={key}>
                <strong>
                  {key.charAt(0).toUpperCase() + key.slice(1)}:
                </strong>{" "}
                {typeof val === "string" ? val : JSON.stringify(val)}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
