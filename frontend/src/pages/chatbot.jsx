// src/pages/Chatbot.jsx
import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { HiOutlineChartBar } from "react-icons/hi";

export default function Chatbot({ chartData }) {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const chatboxRef = useRef(null);

  useEffect(() => {
    window.chatbot = {
      say: (msg) => setMessages(prev => [...prev, { from: "bot", text: msg }])
    };
  }, []);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (chatboxRef.current) {
      chatboxRef.current.scrollTop = chatboxRef.current.scrollHeight;
    }
  }, [messages]);

  // Format message with proper styling for sections
  const formatMessage = (text) => {
    if (!text) return text;
    
    // Split by lines
    const lines = text.split('\n');
    
    return lines.map((line, idx) => {
      // Empty line
      if (!line.trim()) return <div key={idx} style={{ height: 10 }} />;
      
      // Separator lines (━━━)
      if (line.includes('━━━')) {
        return (
          <div key={idx} style={{ 
            borderTop: "2px solid #667eea",
            margin: "16px 0",
            opacity: 0.3
          }} />
        );
      }
      
      // Dash separator lines (─────)
      if (line.includes('─────')) {
        return (
          <div key={idx} style={{ 
            borderTop: "1px solid #ddd",
            margin: "8px 0"
          }} />
        );
      }
      
      // Main headers (🧠, 📊, 💡)
      if (line.includes('🧠 Analysis Complete') || line.includes('💡 INTELLIGENT RECOMMENDATIONS') || line.includes('📊')) {
        return (
          <div key={idx} style={{ 
            fontWeight: 700, 
            fontSize: 16, 
            color: "#667eea",
            marginTop: 16,
            marginBottom: 12,
            paddingBottom: 8,
            borderBottom: "2px solid #667eea30",
            textTransform: "uppercase",
            letterSpacing: "0.5px"
          }}>
            {line}
          </div>
        );
      }
      
      // Section headers with icons (🔮, 🌲, 🔍, 🌡️, ⚙️, ⚡, 🤖, 📈)
      if (line.match(/^(🔮|🌲|🔍|🌡️|⚙️|⚡|🤖|📈|🔧|🛡️|⚡)/)) {
        // Check if it's a critical/high priority title
        const isCritical = line.includes('CRITICAL') || line.includes('ALERT');
        const isHigh = line.includes('WARNING') || line.includes('High');
        
        const bgColor = isCritical ? '#fee2e2' : isHigh ? '#fef3c7' : '#f8f9fa';
        const borderColor = isCritical ? '#dc2626' : isHigh ? '#f59e0b' : '#667eea';
        const textColor = isCritical ? '#dc2626' : isHigh ? '#d97706' : '#222';
        
        return (
          <div key={idx} style={{ 
            fontWeight: 700, 
            fontSize: 14, 
            color: textColor,
            marginTop: 14,
            marginBottom: 8,
            background: bgColor,
            padding: "8px 12px",
            borderRadius: 6,
            borderLeft: `4px solid ${borderColor}`
          }}>
            {line}
          </div>
        );
      }
      
      // Sub-headers (Problem:, Impact:, etc.)
      if (line.match(/^(Problem:|Impact:|Why:|Reason:)/)) {
        return (
          <div key={idx} style={{ 
            fontWeight: 600, 
            fontSize: 13, 
            color: "#333",
            marginTop: 8,
            marginBottom: 4
          }}>
            {line}
          </div>
        );
      }
      
      // Numbered steps (1., 2., etc.)
      if (line.trim().match(/^\d+\./)) {
        return (
          <div key={idx} style={{ 
            paddingLeft: 18,
            marginBottom: 5,
            color: "#444",
            fontSize: 13,
            lineHeight: 1.7,
            fontFamily: "monospace"
          }}>
            {line.trim()}
          </div>
        );
      }
      
      // Bullet points (•)
      if (line.trim().startsWith('•')) {
        return (
          <div key={idx} style={{ 
            paddingLeft: 18,
            marginBottom: 4,
            color: "#555",
            fontSize: 13,
            lineHeight: 1.6
          }}>
            {line.trim()}
          </div>
        );
      }
      
      // Status indicators (✅, ⚠️, 🚨)
      if (line.match(/^(✅|⚠️|🚨|📋|🛡️)/)) {
        const color = line.startsWith('🚨') ? '#dc2626' : 
                     line.startsWith('⚠️') ? '#f59e0b' : 
                     line.startsWith('📋') ? '#3b82f6' :
                     line.startsWith('🛡️') ? '#10b981' : '#10b981';
        return (
          <div key={idx} style={{ 
            padding: "10px 14px",
            marginTop: 12,
            marginBottom: 10,
            background: `${color}15`,
            borderLeft: `4px solid ${color}`,
            borderRadius: 6,
            color: color,
            fontWeight: 600,
            fontSize: 13,
            lineHeight: 1.6
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
    <div id="chatbox-widget" style={{ 
      display: "flex", 
      flexDirection: "column", 
      height: "100%",
      minHeight: 0
    }}>
      {/* Drag and Drop Instruction */}
      <div style={{ 
        background: "linear-gradient(135deg, #667eea15 0%, #764ba215 100%)",
        border: "2px dashed #667eea",
        borderRadius: 8,
        padding: "10px 14px",
        marginBottom: 12,
        textAlign: "center",
        flexShrink: 0
      }}>
        <HiOutlineChartBar size={28} style={{ color: "#667eea", marginBottom: 4 }} />
        <div style={{ fontSize: 14, fontWeight: 700, color: "#667eea", marginBottom: 2 }}>
          📊 Drag & Drop Chart Here
        </div>
        <div style={{ fontSize: 12, color: "#666" }}>
          Drop any chart to analyze machine condition
        </div>
      </div>

      <div 
        id="chatbox" 
        ref={chatboxRef} 
        style={{ 
          flex: 1,
          overflowY: "auto", 
          marginBottom: 10, 
          scrollBehavior: "smooth",
          minHeight: 0
        }}
      >
        {messages.length === 0 ? (
          <div style={{ 
            padding: 14, 
            textAlign: "center", 
            color: "#999", 
            fontSize: 13,
            fontStyle: "italic" 
          }}>
            👋 Hi! I'm ready to help analyze your machine data.
          </div>
        ) : (
          messages.map((m, i) => (
            <div key={i} style={{ 
              margin: "8px 0", 
              padding: 10, 
              borderRadius: 8, 
              background: m.from === "bot" ? "linear-gradient(135deg, #e6f0ff 0%, #f0f7ff 100%)" : "#f0f0f0",
              fontSize: 12,
              lineHeight: 1.6,
              boxShadow: m.from === "bot" ? "0 2px 6px rgba(102, 126, 234, 0.15)" : "none",
              borderLeft: m.from === "bot" ? "4px solid #667eea" : "none",
              wordBreak: "break-word"
            }}>
              <div style={{ 
                whiteSpace: "pre-wrap", 
                fontFamily: "system-ui, -apple-system, sans-serif",
                overflowWrap: "break-word"
              }}>
                {formatMessage(m.text)}
              </div>
            </div>
          ))
        )}
      </div>
      
      {/* <div style={{ flexShrink: 0 }}>
        <input 
          value={message} 
          onChange={e => setMessage(e.target.value)} 
          onKeyPress={e => e.key === 'Enter' && handleSend()}
          placeholder="Ask: anomaly / forecast / recommend..." 
          style={{ 
            width: "100%", 
            padding: "10px 12px", 
            marginBottom: 8,
            border: "1px solid #ddd",
            borderRadius: 6,
            fontSize: 13,
            boxSizing: "border-box"
          }} 
        />
        <button 
          onClick={handleSend} 
          style={{ 
            width: "100%", 
            padding: "10px 12px", 
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)", 
            color: "white", 
            borderRadius: 6,
            border: "none",
            cursor: "pointer",
            fontWeight: 700,
            fontSize: 14,
            transition: "opacity 0.2s"
          }}
          onMouseEnter={(e) => e.currentTarget.style.opacity = "0.9"}
          onMouseLeave={(e) => e.currentTarget.style.opacity = "1"}
        >
          Send Message
        </button>
      </div> */}
    </div>
  );
}
