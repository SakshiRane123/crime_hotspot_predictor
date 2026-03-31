import { motion } from 'framer-motion';

const Modal = ({ title, message, onClose, type = 'warning' }) => {
  const typeStyles = {
    critical: 'border-red-500 bg-red-50',
    high: 'border-orange-500 bg-orange-50',
    medium: 'border-yellow-500 bg-yellow-50',
    low: 'border-green-500 bg-green-50',
    warning: 'border-yellow-500 bg-yellow-50'
  };

  const icons = {
    critical: '🚨',
    high: '⚠️',
    medium: '⚠️',
    low: '✅',
    warning: '⚠️'
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, y: 20 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.9, y: 20 }}
        onClick={(e) => e.stopPropagation()}
        className={`bg-white p-6 rounded-xl shadow-2xl w-96 max-w-[90vw] border-2 ${typeStyles[type]}`}
      >
        <div className="flex items-start gap-3 mb-4">
          <span className="text-3xl">{icons[type]}</span>
          <h2 className="text-xl font-bold flex-1">{title}</h2>
        </div>
        <p className="mb-6 text-gray-700 whitespace-pre-line">{message}</p>

        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 font-semibold transition-colors"
          >
            Understood
          </button>
          {type === 'critical' || type === 'high' ? (
            <button
              onClick={() => {
                window.open('tel:100', '_self');
                onClose();
              }}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 font-semibold transition-colors"
            >
              Call 100
            </button>
          ) : null}
        </div>
      </motion.div>
    </motion.div>
  );
};

export default Modal;
