import React, { useState, useEffect } from "react";
import axios from "axios";

const Chatbot = ({ chartData }) => {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!message.trim()) return;
    setLoading(true);

    try {
      const res = await axios.post("http://localhost:5000/chat", { message });
      setMessages((prev) => [
        ...prev,
        { from: "user", text: message },
        { from: "bot", text: res.data.response },
      ]);
      setMessage("");
    } catch {
      setMessages((prev) => [
        ...prev,
        { from: "bot", text: "⚠️ Error connecting to chatbot." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // -------------------------
  //   DRAG & DROP ANALYSIS
  // -------------------------
 const handleDrop = async (e) => {
  e.preventDefault();
  const chartId = e.dataTransfer.getData("chartId");

  if (!chartId || !chartData) return;

  setMessages((prev) => [
    ...prev,
    { from: "bot", text: `📊 You dropped: ${chartId}. Analyzing...` },
  ]);

  const filteredData = {
    temperature: chartData.temperature || [],
    speed: chartData.speed || [],
    vibration: chartData.vibration || [],
  };

  try {
    const res = await axios.post("http://localhost:5000/chat/analyze", {
      chartType: chartId,
      data: filteredData,
    });

    const data = res.data;

    // Safely extract model blocks with fallbacks
    const lstm = data.lstm || {};
    const rf = data.random_forest || {};
    const iso = data.isolation_forest || {};
    const summary = data.overall_summary || "No summary available.";

    // Forecast block
    const f = lstm.forecast || { temperature: "N/A", speed: "N/A", vibration: "N/A" };
    const forecastText = `
• Forecast:
  - Temperature: ${f.temperature?.toFixed(2) ?? 'N/A'}°C
  - Speed: ${f.speed?.toFixed(2) ?? 'N/A'} RPM
  - Vibration: ${f.vibration?.toFixed(2) ?? 'N/A'} mm/s
`;

    const finalResponse = `
🧠 **AI Recommendation Based on Chart:**

📌 **Overall Summary:**  
${summary || "No overall summary provided."}

-----------------------------

📘 **LSTM Forecast Analysis**
• Issue: ${lstm.issue || "Not available"}
• Cause: ${lstm.cause || "Not available"}
• Solution: ${lstm.solution || "Not available"}
${forecastText}

-----------------------------

🟡 **Random Forest**
• Issue: ${rf.issue || "Not available"}
• Cause: ${rf.cause || "Not available"}
• Solution: ${rf.solution || "Not available"}

-----------------------------

🔴 **Isolation Forest**
• Issue: ${iso.issue || "Not available"}
• Cause: ${iso.cause || "Not available"}
• Solution: ${iso.solution || "Not available"}
(Anomaly Score: ${iso.score?.toFixed(4) ?? 'N/A'})
`;

    setMessages((prev) => [...prev, { from: "bot", text: finalResponse }]);

  } catch (err) {
    console.error("Drop Analysis Error:", err);
    setMessages((prev) => [
      ...prev,
      { from: "bot", text: "⚠️ Failed to analyze chart. Check backend." },
    ]);
  }
};


  const handleDragOver = (e) => e.preventDefault();

  // Auto-scroll chat window
  useEffect(() => {
    const chatBox = document.getElementById("chatbox");
    if (chatBox) chatBox.scrollTop = chatBox.scrollHeight;
  }, [messages]);

  return (
    <div
      className="bg-white p-4 rounded shadow space-y-4"
      onDrop={handleDrop}
      onDragOver={handleDragOver}
    >
      <h3 className="font-semibold text-lg">Smart Maintenance Chatbot</h3>

      <input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Ask about failures, anomalies, or forecasts..."
        className="border p-2 rounded w-full"
      />

      <button
        onClick={handleSend}
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
      >
        Send
      </button>

      <div
        id="chatbox"
        className="max-h-64 overflow-y-auto bg-blue-50 p-3 rounded shadow text-sm text-gray-800 space-y-2"
      >
        {loading && <div className="text-blue-600">Thinking...</div>}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`p-2 whitespace-pre-line rounded ${
              msg.from === "bot"
                ? "bg-blue-100 text-blue-800"
                : "bg-gray-200 text-gray-800"
            }`}
          >
            {msg.text}
          </div>
        ))}
      </div>

      <div className="text-xs text-gray-500 text-center">
        💡 Tip: Drag a chart into this panel to get AI insights.
      </div>
    </div>
  );
};

export default Chatbot;
