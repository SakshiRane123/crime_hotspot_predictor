import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';

const RiskExplanation = ({ latitude, longitude, onClose }) => {
  const [explanation, setExplanation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchExplanation = async () => {
      if (!latitude || !longitude) return;

      setLoading(true);
      setError(null);

      try {
        const response = await axios.post('http://localhost:5000/explain-risk', {
          latitude,
          longitude
        });

        if (response.data.success) {
          setExplanation(response.data);
        } else {
          setError('Failed to get explanation');
        }
      } catch (err) {
        console.error('Error fetching explanation:', err);
        setError('Error loading explanation');
      } finally {
        setLoading(false);
      }
    };

    fetchExplanation();
  }, [latitude, longitude]);

  const getRiskColor = (riskLevel) => {
    switch (riskLevel?.toLowerCase()) {
      case 'high':
        return 'bg-red-500';
      case 'medium':
        return 'bg-yellow-500';
      case 'low':
        return 'bg-green-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getRiskTextColor = (riskLevel) => {
    switch (riskLevel?.toLowerCase()) {
      case 'high':
        return 'text-red-700';
      case 'medium':
        return 'text-yellow-700';
      case 'low':
        return 'text-green-700';
      default:
        return 'text-gray-700';
    }
  };

  if (!latitude || !longitude) return null;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className="fixed bottom-4 right-4 bg-white rounded-xl shadow-2xl p-6 max-w-md z-50 border border-gray-200"
    >
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-xl font-bold text-gray-800">Risk Explanation</h3>
        <button
          onClick={onClose}
          className="text-gray-500 hover:text-gray-700 text-xl"
        >
          ×
        </button>
      </div>

      {loading && (
        <div className="text-center py-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-gray-600 mt-2">Analyzing risk...</p>
        </div>
      )}

      {error && (
        <div className="text-red-600 py-4">
          <p>{error}</p>
        </div>
      )}

      {explanation && !loading && (
        <div>
          {/* Risk Level Badge */}
          <div className="mb-4">
            <div className="flex items-center gap-3">
              <div className={`w-4 h-4 rounded-full ${getRiskColor(explanation.risk_level)}`}></div>
              <span className={`font-bold text-lg ${getRiskTextColor(explanation.risk_level)}`}>
                {explanation.risk_level} Risk
              </span>
            </div>
          </div>

          {/* Reasons */}
          <div>
            <h4 className="font-semibold text-gray-700 mb-2">Why is this area {explanation.risk_level.toLowerCase()} risk?</h4>
            <ul className="space-y-2">
              {explanation.top_reasons?.map((reason, index) => (
                <li key={index} className="flex items-start gap-2 text-sm text-gray-600">
                  <span className="text-blue-600 mt-1">•</span>
                  <span>{reason}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Coordinates */}
          <div className="mt-4 pt-4 border-t border-gray-200">
            <p className="text-xs text-gray-500">
              Location: {latitude.toFixed(4)}, {longitude.toFixed(4)}
            </p>
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default RiskExplanation;


