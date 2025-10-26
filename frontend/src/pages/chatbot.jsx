import React, { useState, useEffect } from "react";
import axios from "axios";

const Chatbot = ({ recommendation = {} }) => {
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

  // ✅ Scroll chat to bottom
  useEffect(() => {
    const chatBox = document.getElementById("chatbox");
    if (chatBox) chatBox.scrollTop = chatBox.scrollHeight;
  }, [messages]);

  return (
    <div className="bg-white p-4 rounded shadow space-y-4">
      <h3 className="font-semibold text-lg">Smart Maintenance Chatbot</h3>

      {/* ✅ Show latest recommendation as context */}
      {recommendation?.issue && (
        <div className="text-sm text-gray-600 mb-2 space-y-1">
          <div><strong>Latest Insight:</strong></div>
          <div><strong>Issue:</strong> {recommendation.issue}</div>
          <div><strong>Cause:</strong> {recommendation.cause}</div>
          <div><strong>Solution:</strong> {recommendation.solution}</div>
        </div>
      )}

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
            className={`p-2 rounded ${
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
        💡 Tip: Ask follow-up questions about the latest recommendation.
      </div>
    </div>
  );
};

export default Chatbot;