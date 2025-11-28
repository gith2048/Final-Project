// src/pages/ChatWidget.jsx
import { useState, useEffect, useRef } from "react";
import { FiX, FiMove } from "react-icons/fi";
import { RiRobot2Fill } from "react-icons/ri";
import Chatbot from "./chatbot";

const ChatWidget = ({ chartData = null }) => {
  const [open, setOpen] = useState(false);
  const [position, setPosition] = useState({ x: null, y: null });
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const [size, setSize] = useState({ width: 420, height: 600 });
  const hasSpokenRef = useRef(false);
  const chatWidgetRef = useRef(null);

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
          utterance.rate = 0.9;
          utterance.pitch = 1.0;
          utterance.volume = 1.0;
          
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

      setTimeout(() => {
        speak("Hello, I am Optimus Assistant. Drop a chart in the chatbot to analyze the machine condition.");
      }, 100);
    }
  }, [open]);

  // Set initial responsive position
  useEffect(() => {
    if (open && position.x === null) {
      const updatePosition = () => {
        const windowWidth = window.innerWidth;
        const windowHeight = window.innerHeight;
        
        // Responsive sizing
        let width = 420;
        let height = 600;
        let margin = 24;
        
        if (windowWidth < 640) {
          // Small mobile
          width = windowWidth - 16;
          height = windowHeight - 80;
          margin = 8;
        } else if (windowWidth < 768) {
          // Mobile
          width = Math.min(windowWidth - 32, 380);
          height = Math.min(windowHeight - 100, 520);
          margin = 16;
        } else if (windowWidth < 1024) {
          // Tablet
          width = 400;
          height = 550;
          margin = 20;
        }
        
        setSize({ width, height });
        
        // Position in bottom right with margin
        setPosition({
          x: windowWidth - width - margin,
          y: windowHeight - height - margin
        });
      };
      
      updatePosition();
      window.addEventListener('resize', updatePosition);
      return () => window.removeEventListener('resize', updatePosition);
    }
  }, [open, position.x]);

  // Dragging handlers (Mouse)
  const handleMouseDown = (e) => {
    if (e.target.closest('.drag-handle')) {
      e.preventDefault();
      setIsDragging(true);
      setDragOffset({
        x: e.clientX - position.x,
        y: e.clientY - position.y
      });
    }
  };

  const handleMouseMove = (e) => {
    if (isDragging) {
      const newX = e.clientX - dragOffset.x;
      const newY = e.clientY - dragOffset.y;
      
      // Constrain to window bounds
      const maxX = window.innerWidth - size.width;
      const maxY = window.innerHeight - size.height;
      
      setPosition({
        x: Math.max(0, Math.min(newX, maxX)),
        y: Math.max(0, Math.min(newY, maxY))
      });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  // Touch handlers for mobile
  const handleTouchStart = (e) => {
    if (e.target.closest('.drag-handle')) {
      const touch = e.touches[0];
      setIsDragging(true);
      setDragOffset({
        x: touch.clientX - position.x,
        y: touch.clientY - position.y
      });
    }
  };

  const handleTouchMove = (e) => {
    if (isDragging) {
      const touch = e.touches[0];
      const newX = touch.clientX - dragOffset.x;
      const newY = touch.clientY - dragOffset.y;
      
      // Constrain to window bounds
      const maxX = window.innerWidth - size.width;
      const maxY = window.innerHeight - size.height;
      
      setPosition({
        x: Math.max(0, Math.min(newX, maxX)),
        y: Math.max(0, Math.min(newY, maxY))
      });
    }
  };

  const handleTouchEnd = () => {
    setIsDragging(false);
  };

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.addEventListener('touchmove', handleTouchMove);
      document.addEventListener('touchend', handleTouchEnd);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
        document.removeEventListener('touchmove', handleTouchMove);
        document.removeEventListener('touchend', handleTouchEnd);
      };
    }
  }, [isDragging, dragOffset, position]);

  const handleClose = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    setOpen(false);
    setPosition({ x: null, y: null });
    hasSpokenRef.current = false;
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
            transition: "transform 0.2s, box-shadow 0.2s",
            zIndex: 1000
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
      {open && position.x !== null && (
        <div 
          ref={chatWidgetRef}
          style={{ 
            position: "fixed", 
            left: position.x,
            top: position.y,
            width: size.width, 
            height: size.height,
            background: "white", 
            boxShadow: isDragging ? "0 20px 60px rgba(0,0,0,0.3)" : "0 10px 40px rgba(0,0,0,0.2)", 
            borderRadius: 14, 
            zIndex: 1000,
            display: "flex",
            flexDirection: "column",
            transition: isDragging ? "none" : "box-shadow 0.2s",
            userSelect: isDragging ? "none" : "auto"
          }}
          onMouseDown={handleMouseDown}
          onTouchStart={handleTouchStart}
        >
          <div 
            className="drag-handle"
            style={{ 
              padding: 14, 
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)", 
              borderTopLeftRadius: 14, 
              borderTopRightRadius: 14,
              display: "flex", 
              justifyContent: "space-between", 
              alignItems: "center",
              color: "white",
              cursor: isDragging ? "grabbing" : "grab",
              flexShrink: 0
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <RiRobot2Fill size={28} />
              <div>
                <div style={{ fontWeight: 700, fontSize: 17 }}>Optimus PdM</div>
                <div style={{ fontSize: 12, opacity: 0.95 }}>AI Maintenance Assistant</div>
              </div>
            </div>
            <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
              <div 
                style={{ 
                  background: "rgba(255,255,255,0.2)", 
                  borderRadius: "50%",
                  width: 32,
                  height: 32,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "white",
                  cursor: "grab"
                }}
                title="Drag to move"
              >
                <FiMove size={16} />
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
          </div>
          <div style={{ padding: 12, flex: 1, overflow: "hidden", display: "flex", flexDirection: "column" }}>
            <Chatbot chartData={chartData} />
          </div>
        </div>
      )}
    </>
  );
};

export default ChatWidget;
