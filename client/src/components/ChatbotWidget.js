import React, { useState, useEffect } from "react";
import { MessageCircle } from "lucide-react";

const ChatbotWidget = () => {
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState("");

  useEffect(() => {
    const savedId = localStorage.getItem("cb_session_id");
    if (savedId) {
      setSessionId(savedId);
    } else {
      const newId = crypto.randomUUID();
      localStorage.setItem("cb_session_id", newId);
      setSessionId(newId);
    }
  }, []);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg = { role: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("http://localhost:5050/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, message: input }),
      });

      const data = await res.json();
      if (data.error) throw new Error(data.error);

      const botMsg = { role: "bot", text: data.response };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      const errorMsg = { role: "bot", text: "❌ Error: " + err.message };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

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
        <div className="fixed bottom-20 right-6 z-50 w-80 h-[28rem] bg-white border-2 border-blue-900 shadow-xl rounded-xl overflow-hidden flex flex-col">
          {/* Header */}
          <div className="bg-blue-900 text-white px-4 py-2 flex justify-between items-center text-sm font-bold">
            CivicBridge Chatbot
            <button
              onClick={() => setOpen(false)}
              className="text-white hover:text-red-400 text-lg"
            >
              ×
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 p-3 overflow-y-auto text-sm space-y-2">
            {messages.length === 0 && (
              <>
                <p><strong>Hi there!</strong></p>
                <p>I’m your civic sidekick. Ask me about laws, policies, or your representatives!</p>
              </>
            )}

            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`max-w-[90%] px-3 py-2 rounded text-sm ${
                  msg.role === "user"
                    ? "bg-blue-100 self-end text-right ml-auto"
                    : "bg-gray-100 self-start text-left mr-auto"
                }`}
              >
                {msg.text}
              </div>
            ))}

            {loading && (
              <p className="text-xs text-gray-400 italic">Thinking...</p>
            )}
          </div>

          {/* Input */}
          <div className="p-2 border-t bg-gray-50">
            <textarea
              rows={1}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a policy question..."
              className="w-full resize-none px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
        </div>
      )}
    </>
  );
};

export default ChatbotWidget;
