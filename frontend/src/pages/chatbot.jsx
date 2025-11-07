import React, { useState, useEffect } from "react";
import axios from "axios";

const Chatbot = ({ chartData }) => {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const TEMP_THRESHOLD = 70.0;
  const VIBRATION_THRESHOLD = 5.0;
  const SPEED_THRESHOLD = 1200;
  const NOISE_THRESHOLD = 80.0;

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

const handleDrop = async (e) => {
  e.preventDefault();
  const chartId = e.dataTransfer.getData("chartId");
  if (!chartId || !chartData) return;

  setMessages((prev) => [
    ...prev,
    { from: "bot", text: `📊 You dropped: ${chartId}. Analyzing...` },
  ]);

  // ✅ Send only 3 features
  const filteredData = {
    temperature: chartData.temperature,
    speed: chartData.speed,
    vibration: chartData.vibration,
  };

  try {
    const res = await axios.post("http://localhost:5000/chat/analyze", {
      chartType: chartId,
      data: filteredData,
    });

    const { issue, cause, solution, forecast } = res.data;

    let forecastText = "";
    let alerts = [];

    if (forecast) {
      forecastText = `\n• Forecast:\n  - Temperature: ${forecast.temperature}°C\n  - Speed: ${forecast.speed}\n  - Vibration: ${forecast.vibration}`;

      if (forecast.temperature > TEMP_THRESHOLD)
        alerts.push("🚨 Temperature forecast exceeds safe threshold.");
      if (forecast.vibration > VIBRATION_THRESHOLD)
        alerts.push("🚨 Vibration forecast is high — check bearings.");
      if (forecast.speed > SPEED_THRESHOLD)
        alerts.push("🚨 Speed forecast is elevated — inspect motor load.");
    }

    const alertText = alerts.length
      ? `\n\n🔔 Real-Time Alerts:\n${alerts.map((a) => `• ${a}`).join("\n")}`
      : "";

    setMessages((prev) => [
      ...prev,
      {
        from: "bot",
        text: `🧠 Recommendation:\n• Issue: ${issue}\n• Cause: ${cause}\n• Solution: ${solution}${forecastText}${alertText}`,
      },
    ]);
  } catch (err) {
    console.error("Chart analysis error:", err);
    setMessages((prev) => [
      ...prev,
      { from: "bot", text: "⚠️ Failed to analyze chart." },
    ]);
  }
};
  const handleDragOver = (e) => e.preventDefault();

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
        placeholder="Ask about anomalies, failure risk, or forecasts..."
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