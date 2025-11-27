// src/pages/Chatbot.jsx
import { useState, useEffect } from "react";
import axios from "axios";
import { HiOutlineChartBar } from "react-icons/hi";

export default function Chatbot({ chartData }) {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    window.chatbot = {
      say: (msg) => setMessages(prev => [...prev, { from: "bot", text: msg }])
    };
  }, []);

  // Format message with proper styling for sections
  const formatMessage = (text) => {
    if (!text) return text;
    
    // Split by lines
    const lines = text.split('\n');
    
    return lines.map((line, idx) => {
      // Empty line
      if (!line.trim()) return <div key={idx} style={{ height: 10 }} />;
      
      // Main headers (🧠, 📊)
      if (line.includes('🧠 Analysis Complete') || line.includes('📊')) {
        return (
          <div key={idx} style={{ 
            fontWeight: 700, 
            fontSize: 15, 
            color: "#667eea",
            marginBottom: 10,
            paddingBottom: 8,
            borderBottom: "2px solid #667eea30"
          }}>
            {line}
          </div>
        );
      }
      
      // Section headers (📋, 🔮, 🌲, 🔍)
      if (line.match(/^(📋|🔮|🌲|🔍)/)) {
        return (
          <div key={idx} style={{ 
            fontWeight: 700, 
            fontSize: 14, 
            color: "#222",
            marginTop: 12,
            marginBottom: 6,
            background: "#f8f9fa",
            padding: "6px 10px",
            borderRadius: 5
          }}>
            {line}
          </div>
        );
      }
      
      // Bullet points (•)
      if (line.trim().startsWith('•')) {
        return (
          <div key={idx} style={{ 
            paddingLeft: 14,
            marginBottom: 4,
            color: "#444",
            fontSize: 13,
            lineHeight: 1.6
          }}>
            {line}
          </div>
        );
      }
      
      // Status indicators (✅, ⚠️, 🚨)
      if (line.match(/^(✅|⚠️|🚨)/)) {
        const color = line.startsWith('🚨') ? '#dc2626' : line.startsWith('⚠️') ? '#f59e0b' : '#10b981';
        return (
          <div key={idx} style={{ 
            padding: "8px 12px",
            marginBottom: 8,
            background: `${color}15`,
            borderLeft: `4px solid ${color}`,
            borderRadius: 5,
            color: color,
            fontWeight: 600,
            fontSize: 13,
            lineHeight: 1.5
          }}>
            {line}
          </div>
        );
      }
      
      // Regular text
      return (
        <div key={idx} style={{ 
          marginBottom: 4, 
          color: "#555",
          fontSize: 13,
          lineHeight: 1.6
        }}>
          {line}
        </div>
      );
    });
  };

  const buildSequence = () => {
    if (!chartData) return [];
    const SEQ_LEN = 10;
    const t = chartData.temperature.slice(-SEQ_LEN);
    const v = chartData.vibration.slice(-SEQ_LEN);
    const s = chartData.speed.slice(-SEQ_LEN);
    if (t.length < SEQ_LEN) return [];
    const seq = [];
    for (let i = 0; i < SEQ_LEN; i++) seq.push([t[i], v[i], s[i]]);
    return seq;
  };

  const handleSend = async () => {
    if (!message.trim()) return;
    setMessages(prev => [...prev, { from: "user", text: message }]);
    try {
      const payload = { message, chartData, sequence: buildSequence() };
      const res = await axios.post("http://localhost:5000/chat", payload);
      setMessages(prev => [...prev, { from: "bot", text: res.data.response }]);
    } catch (err) {
      setMessages(prev => [...prev, { from: "bot", text: "⚠️ Chatbot unavailable." }]);
    }
    setMessage("");
  };

  return (
    <div id="chatbox-widget">
      {/* Drag and Drop Instruction */}
      <div style={{ 
        background: "linear-gradient(135deg, #667eea15 0%, #764ba215 100%)",
        border: "2px dashed #667eea",
        borderRadius: 8,
        padding: 14,
        marginBottom: 12,
        textAlign: "center"
      }}>
        <HiOutlineChartBar size={32} style={{ color: "#667eea", marginBottom: 6 }} />
        <div style={{ fontSize: 15, fontWeight: 700, color: "#667eea", marginBottom: 4 }}>
          📊 Drag & Drop Chart Here
        </div>
        <div style={{ fontSize: 13, color: "#666" }}>
          Drop any chart to analyze machine condition
        </div>
      </div>

      <div id="chatbox" style={{ maxHeight: 220, overflowY: "auto", marginBottom: 10 }}>
        {messages.length === 0 ? (
          <div style={{ 
            padding: 14, 
            textAlign: "center", 
            color: "#999", 
            fontSize: 14,
            fontStyle: "italic" 
          }}>
            👋 Hi! I'm ready to help analyze your machine data.
          </div>
        ) : (
          messages.map((m, i) => (
            <div key={i} style={{ 
              margin: "8px 0", 
              padding: 12, 
              borderRadius: 8, 
              background: m.from === "bot" ? "linear-gradient(135deg, #e6f0ff 0%, #f0f7ff 100%)" : "#f0f0f0",
              fontSize: 13,
              lineHeight: 1.7,
              boxShadow: m.from === "bot" ? "0 2px 6px rgba(102, 126, 234, 0.15)" : "none",
              borderLeft: m.from === "bot" ? "4px solid #667eea" : "none"
            }}>
              <div style={{ whiteSpace: "pre-wrap", fontFamily: "system-ui, -apple-system, sans-serif" }}>
                {formatMessage(m.text)}
              </div>
            </div>
          ))
        )}
      </div>
      <input 
        value={message} 
        onChange={e => setMessage(e.target.value)} 
        onKeyPress={e => e.key === 'Enter' && handleSend()}
        placeholder="Ask: anomaly / forecast / recommend..." 
        style={{ 
          width: "100%", 
          padding: 10, 
          marginBottom: 8,
          border: "1px solid #ddd",
          borderRadius: 6,
          fontSize: 14
        }} 
      />
      <button 
        onClick={handleSend} 
        style={{ 
          width: "100%", 
          padding: 12, 
          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)", 
          color: "white", 
          borderRadius: 6,
          border: "none",
          cursor: "pointer",
          fontWeight: 700,
          fontSize: 15,
          transition: "opacity 0.2s"
        }}
        onMouseEnter={(e) => e.currentTarget.style.opacity = "0.9"}
        onMouseLeave={(e) => e.currentTarget.style.opacity = "1"}
      >
        Send Message
      </button>
    </div>
  );
}
