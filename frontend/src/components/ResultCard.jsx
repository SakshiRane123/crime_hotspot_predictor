import { motion } from 'framer-motion';

const ResultCard = ({ result }) => {
  if (!result) return null;

  const severityColors = {
    Low: 'bg-gradient-to-br from-green-100 to-emerald-100 border-green-400 text-green-800',
    Medium: 'bg-gradient-to-br from-yellow-100 to-amber-100 border-yellow-400 text-yellow-800',
    High: 'bg-gradient-to-br from-orange-100 to-red-100 border-orange-400 text-orange-800',
    Critical: 'bg-gradient-to-br from-red-100 to-rose-100 border-red-500 text-red-800'
  };

  const severityIcons = {
    Low: '✅',
    Medium: '⚠️',
    High: '🔶',
    Critical: '🚨'
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 30, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.5, type: "spring" }}
      className="mt-8"
    >
      <div className="bg-gradient-to-br from-white via-purple-50 to-blue-50 p-8 rounded-2xl shadow-2xl border-2 border-purple-200">
        <h3 className="text-2xl font-bold bg-gradient-to-r from-purple-900 to-blue-900 bg-clip-text text-transparent mb-6">
          🎯 Prediction Results
        </h3>

        {/* Hotspot + Severity */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* Hotspot Status */}
          <motion.div 
            whileHover={{ scale: 1.05 }}
            className={`p-6 rounded-2xl border-2 shadow-xl ${
              result.Hotspot_Label === 1 
                ? 'bg-gradient-to-br from-red-50 to-orange-50 border-red-400' 
                : 'bg-gradient-to-br from-green-50 to-emerald-50 border-green-400'
            }`}
          >
            <div className="text-center">
              <p className="text-sm font-semibold text-gray-700 mb-2 uppercase tracking-wide">
                Hotspot Status
              </p>
              <p className={`text-4xl font-bold ${
                result.Hotspot_Label === 1 ? 'text-red-600' : 'text-green-600'
              }`}>
                {result.Hotspot_Label === 1 ? '⚠️ HOTSPOT' : '✓ SAFE'}
              </p>
            </div>
          </motion.div>

          {/* Severity Level */}
          <motion.div 
            whileHover={{ scale: 1.05 }}
            className={`p-6 rounded-2xl border-2 shadow-xl ${
              severityColors[result.Predicted_Severity_Level]
            }`}
          >
            <div className="text-center">
              <p className="text-sm font-semibold text-gray-700 mb-2 uppercase tracking-wide">
                Severity Level
              </p>
              <p className="text-4xl font-bold">
                {severityIcons[result.Predicted_Severity_Level]} {result.Predicted_Severity_Level}
              </p>
            </div>
          </motion.div>
        </div>

        {/* Location Info */}
        {result.location && (
          <div className="mt-6 p-4 bg-gray-50 rounded-xl border">
            <p className="text-sm text-gray-600">
              <span className="font-semibold">Location:</span> {result.location.city}
            </p>
            <p className="text-sm text-gray-600">
              <span className="font-semibold">Coordinates:</span> {result.location.lat.toFixed(4)}, {result.location.lng.toFixed(4)}
            </p>
            <p className="text-sm text-gray-600">
              <span className="font-semibold">Timestamp:</span> {new Date(result.timestamp).toLocaleString()}
            </p>
          </div>
        )}

        {/* 🔥 AI-GENERATED ALERT MESSAGE */}
        {result.alert_message && (
          <div className="mt-6 p-6 bg-red-50 border-l-4 border-red-500 rounded-xl">
            <h4 className="text-lg font-bold text-red-700 mb-2">🚨 Instant Alert</h4>
            <p className="text-gray-700">{result.alert_message}</p>
          </div>
        )}

        {/* 🧠 REASON FOR CRIME */}
        {result.reason && (
          <div className="mt-6 p-6 bg-yellow-50 border-l-4 border-yellow-500 rounded-xl">
            <h4 className="text-lg font-bold text-yellow-700 mb-2">📌 Why is crime risk high?</h4>
            <p className="text-gray-700">{result.reason}</p>
          </div>
        )}

        {/* 🛡️ SUGGESTIONS */}
        {result.suggestions && (
          <div className="mt-6 p-6 bg-green-50 border-l-4 border-green-500 rounded-xl">
            <h4 className="text-lg font-bold text-green-700 mb-2">🛡️ Safety Suggestions</h4>
            <p className="text-gray-700 whitespace-pre-line">{result.suggestions}</p>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default ResultCard;
