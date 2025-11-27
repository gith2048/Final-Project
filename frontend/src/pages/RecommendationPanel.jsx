// src/pages/RecommendationPanel.jsx
export default function RecommendationPanel({ data }) {
  if (!data || data.error) return null;

  // Normalize different response formats to a consistent object
  const normalize = () => {
    const out = { lstm: null, random_forest: null, isolation_forest: null, thresholds: data.thresholds || {}, overall_summary: data.overall_summary || "" };

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
  const getColor = (issue = "") => {
    const t = (issue || "").toLowerCase();
    if (t.includes("critical") || t.includes("anomaly") || t.includes("🚨")) return "red";
    if (t.includes("high") || t.includes("warning") || t.includes("⚠")) return "yellow";
    return "green";
  };

  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }}>
      {[["LSTM", obj.lstm], ["Random Forest", obj.random_forest], ["Isolation Forest", obj.isolation_forest]].map(([title, block]) => {
        if (!block) return null;
        const color = getColor(block.issue);
        return (
          <div key={title} style={{ padding: 12, borderRadius: 8, background: "#fff", borderLeft: `6px solid ${color === "red" ? "#dc2626" : color === "yellow" ? "#f59e0b" : "#10b981"}` }}>
            <h4 style={{ margin: 0 }}>{title}</h4>
            <p style={{ margin: "6px 0" }}><strong>Issue:</strong> {block.issue}</p>
            {block.cause && <p style={{ margin: "6px 0" }}><strong>Cause:</strong> {block.cause}</p>}
            {block.solution && <p style={{ margin: "6px 0" }}><strong>Solution:</strong> {block.solution}</p>}
            {block.forecast && <div><strong>Forecast:</strong><ul><li>Temp: {Number(block.forecast.temperature).toFixed(2)}°C</li><li>Vib: {Number(block.forecast.vibration).toFixed(2)}</li><li>Speed: {Number(block.forecast.speed).toFixed(2)}</li></ul></div>}
            {block.score !== undefined && <p><strong>Score:</strong> {Number(block.score).toFixed(3)}</p>}
          </div>
        );
      })}
      {/* thresholds block */}
      <div style={{ gridColumn: "1 / -1", padding: 12, background: "#f8fafc", borderRadius: 8 }}>
        <h4>Sensor Status</h4>
        <pre style={{ whiteSpace: "pre-wrap" }}>{obj.overall_summary}</pre>
      </div>
    </div>
  );
}
