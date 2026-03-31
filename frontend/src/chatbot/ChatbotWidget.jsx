import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ChatbotWindow from './ChatbotWindow';

const ChatbotWidget = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* Floating Button */}
      {!isOpen && (
        <motion.button
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-full shadow-2xl z-40 flex items-center gap-2 font-semibold hover:from-blue-700 hover:to-purple-700 transition-all"
        >
          <span>💬</span>
          <span>Need Safety Advice? Chat Now</span>
        </motion.button>
      )}

      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <ChatbotWindow onClose={() => setIsOpen(false)} />
        )}
      </AnimatePresence>
    </>
  );
};

export default ChatbotWidget;


