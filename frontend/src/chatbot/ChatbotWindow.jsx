import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';

const ChatbotWindow = ({ onClose }) => {
  const [messages, setMessages] = useState([
    {
      type: 'bot',
      text: "👋 Hello! I'm your Safety Assistant. I can help you with:\n\n• Safety advice for locations\n• Safe route suggestions\n• What to do in emergencies\n• Time-based safety tips\n\nHow can I help you today?"
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    
    // Add user message
    setMessages(prev => [...prev, { type: 'user', text: userMessage }]);
    setLoading(true);

    try {
      const response = await axios.post('http://localhost:5000/chatbot-message', {
        message: userMessage
      }, {
        timeout: 10000 // 10 second timeout
      });

      if (response.data && response.data.success) {
        const botResponse = response.data.response || "I'm here to help with safety questions. How can I assist you?";
        const suggestions = response.data.suggestions || [];
        
        setMessages(prev => [...prev, {
          type: 'bot',
          text: botResponse,
          suggestions: suggestions
        }]);
      } else {
        // Even if success is false, try to show the response if available
        const errorResponse = response.data?.response || "Sorry, I encountered an error. Please try again.";
        setMessages(prev => [...prev, {
          type: 'bot',
          text: errorResponse,
          suggestions: response.data?.suggestions || []
        }]);
      }
    } catch (error) {
      console.error('Chatbot error:', error);
      
      let errorMessage = "Sorry, I'm having trouble connecting. ";
      
      if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error')) {
        errorMessage += "Please make sure the backend server is running on http://localhost:5000";
      } else if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
        errorMessage += "The request took too long. Please try again.";
      } else if (error.response) {
        // Server responded with error status
        errorMessage = error.response.data?.response || error.response.data?.error || errorMessage;
      }
      
      setMessages(prev => [...prev, {
        type: 'bot',
        text: errorMessage,
        suggestions: ["Check connection", "Try again", "Report issue"]
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setInput(suggestion);
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9, y: 20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.9, y: 20 }}
      className="fixed bottom-6 right-6 w-96 h-[600px] bg-white rounded-xl shadow-2xl z-50 flex flex-col border border-gray-200"
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 rounded-t-xl flex justify-between items-center">
        <div className="flex items-center gap-2">
          <span className="text-2xl">🤖</span>
          <div>
            <h3 className="font-bold">Safety Assistant</h3>
            <p className="text-xs opacity-90">Always here to help</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="text-white hover:text-gray-200 text-xl font-bold"
        >
          ×
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-3 ${
                msg.type === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-800 shadow-md'
              }`}
            >
              <p className="whitespace-pre-wrap text-sm">{msg.text}</p>
              {msg.suggestions && msg.suggestions.length > 0 && (
                <div className="mt-2 space-y-1">
                  {msg.suggestions.map((suggestion, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSuggestionClick(suggestion)}
                      className="block w-full text-left text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded hover:bg-blue-100 transition-colors"
                    >
                      💡 {suggestion}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white rounded-lg p-3 shadow-md">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSend} className="p-4 border-t border-gray-200 bg-white rounded-b-xl">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about safety..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Send
          </button>
        </div>
      </form>
    </motion.div>
  );
};

export default ChatbotWindow;

