import React, { useState } from "react";
import { MessageCircle } from "lucide-react";

const ChatbotWidget = () => {
  const [open, setOpen] = useState(false);

  return (
    <>
      {/* Floating Chat Button */}
      <div className="fixed bottom-6 right-6 z-50">
        <button
          onClick={() => setOpen(!open)}
          className="bg-red-600 hover:bg-red-700 text-white p-3 rounded-full shadow-lg border-4 border-white focus:outline-none transition"
        >
          <MessageCircle className="w-6 h-6" />
        </button>
      </div>

      {/* Chat Window */}
      {open && (
        <div className="fixed bottom-20 right-6 z-50 w-80 h-96 bg-white border-2 border-blue-900 shadow-xl rounded-xl overflow-hidden flex flex-col">
          {/* Header */}
          <div className="bg-blue-900 text-white px-4 py-2 flex justify-between items-center text-sm font-bold">
            CivicBridge Chatbot 
            <button onClick={() => setOpen(false)} className="text-white hover:text-red-400 text-lg">×</button>
          </div>

          {/* Chat body */}
          <div className="flex-1 p-4 text-sm overflow-y-auto text-gray-700 space-y-2">
            <p><strong>Hi there!</strong></p>
            <p>I’m your civic sidekick. Ask me about laws, policies, or your representatives!</p>
            {/* Future: hook this up to LLM or chat backend */}
          </div>

          {/* Input placeholder (non-functional for now) */}
          <div className="p-2 border-t bg-gray-50">
            <input
              type="text"
              placeholder="Type a question..."
              disabled
              className="w-full px-3 py-2 border rounded-md text-sm bg-gray-100 text-gray-500 cursor-not-allowed"
            />
          </div>
        </div>
      )}
    </>
  );
};

export default ChatbotWidget;
