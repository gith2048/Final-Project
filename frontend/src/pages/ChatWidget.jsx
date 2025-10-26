import React, { useState } from "react";
import { FiMessageSquare, FiX } from "react-icons/fi";
import Chatbot from "../pages/Chatbot";

const ChatWidget = ({ chartData = null }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* 🔹 Floating Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 bg-blue-600 text-white p-4 rounded-full shadow-lg hover:bg-blue-700 transition z-50"
          aria-label="Open Chatbot"
        >
          <FiMessageSquare size={24} />
        </button>
      )}

      {/* 🔹 Chat Panel */}
      {isOpen && (
        <div
          className="fixed bottom-6 right-6 w-80 max-w-full bg-white rounded-xl shadow-2xl z-50 border border-gray-200"
          onDragOver={(e) => e.preventDefault()}
        >
          <div className="flex justify-between items-center p-3 border-b">
            <h4 className="font-semibold text-blue-700">Optimus Assistant 🤖</h4>
            <button
              onClick={() => setIsOpen(false)}
              className="text-gray-500 hover:text-red-500"
            >
              <FiX size={20} />
            </button>
          </div>

          <div className="p-3 max-h-[500px] overflow-y-auto">
            {/* ✅ Pass chartData for drag-and-drop analysis */}
            <Chatbot chartData={chartData} />
          </div>
        </div>
      )}
    </>
  );
};

export default ChatWidget;