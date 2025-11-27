// src/pages/ChatWidget.jsx
import { useState, useEffect, useRef } from "react";
import { FiX } from "react-icons/fi";
import { RiRobot2Fill } from "react-icons/ri";
import Chatbot from "./chatbot";

const ChatWidget = ({ chartData = null }) => {
  const [open, setOpen] = useState(false);
  const hasSpokenRef = useRef(false);

  useEffect(() => {
    // make window.chatbot.say available
    window.chatbot = window.chatbot || { say: (msg) => console.log("chatbot.say:", msg) };
  }, []);

  // Voice greeting when chatbot opens
  useEffect(() => {
    if (open && !hasSpokenRef.current) {
      hasSpokenRef.current = true;
      
      // Use Web Speech API for voice
      const speak = (text) => {
        if ('speechSynthesis' in window) {
          // Cancel any ongoing speech
          window.speechSynthesis.cancel();
          
          const utterance = new SpeechSynthesisUtterance(text);
          utterance.rate = 0.9; // Slightly slower for clarity
          utterance.pitch = 1.0;
          utterance.volume = 1.0;
          
          // Optional: Select a specific voice (you can customize this)
          const voices = window.speechSynthesis.getVoices();
          const preferredVoice = voices.find(voice => 
            voice.name.includes('Google') || voice.name.includes('Microsoft')
          );
          if (preferredVoice) {
            utterance.voice = preferredVoice;
          }
          
          window.speechSynthesis.speak(utterance);
        }
      };

      // Small delay to ensure smooth opening animation
      setTimeout(() => {
        speak("Hello, I am Optimus Assistant. Drop a chart in the chatbot to analyze the machine condition.");
      }, 100);
    }
  }, [open]);

  const handleClose = () => {
    // Cancel speech when closing
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    setOpen(false);
    hasSpokenRef.current = false; // Reset so it speaks again next time
  };

  return (
    <>
      {!open && (
        <button 
          onClick={() => setOpen(true)} 
          style={{ 
            position: "fixed", 
            right: 24, 
            bottom: 24, 
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)", 
            color: "white", 
            width: 64, 
            height: 64, 
            borderRadius: "50%", 
            border: "none", 
            cursor: "pointer",
            boxShadow: "0 4px 15px rgba(102, 126, 234, 0.4)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            transition: "transform 0.2s, box-shadow 0.2s"
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = "scale(1.1)";
            e.currentTarget.style.boxShadow = "0 6px 20px rgba(102, 126, 234, 0.6)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = "scale(1)";
            e.currentTarget.style.boxShadow = "0 4px 15px rgba(102, 126, 234, 0.4)";
          }}
        >
          <RiRobot2Fill size={32} />
        </button>
      )}
      {open && (
        <div style={{ position: "fixed", right: 24, bottom: 24, width: 420, background: "white", boxShadow: "0 10px 40px rgba(0,0,0,0.2)", borderRadius: 14, zIndex: 1000 }}>
          <div style={{ 
            padding: 14, 
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)", 
            borderTopLeftRadius: 14, 
            borderTopRightRadius: 14,
            display: "flex", 
            justifyContent: "space-between", 
            alignItems: "center",
            color: "white"
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <RiRobot2Fill size={28} />
              <div>
                <div style={{ fontWeight: 700, fontSize: 17 }}>Optimus PdM</div>
                <div style={{ fontSize: 12, opacity: 0.95 }}>AI Maintenance Assistant</div>
              </div>
            </div>
            <button 
              onClick={handleClose} 
              style={{ 
                background: "rgba(255,255,255,0.2)", 
                border: "none", 
                cursor: "pointer",
                borderRadius: "50%",
                width: 36,
                height: 36,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "white",
                transition: "background 0.2s"
              }}
              onMouseEnter={(e) => e.currentTarget.style.background = "rgba(255,255,255,0.3)"}
              onMouseLeave={(e) => e.currentTarget.style.background = "rgba(255,255,255,0.2)"}
            >
              <FiX size={20} />
            </button>
          </div>
          <div style={{ padding: 12 }}>
            <Chatbot chartData={chartData} />
          </div>
        </div>
      )}
    </>
  );
};

export default ChatWidget;
