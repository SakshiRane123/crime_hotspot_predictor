import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';
import InputForm from '../components/InputForm';
import ResultCard from '../components/ResultCard';
import Modal from '../components/Modal';
import Toast from '../components/Toast';
import { 
  requestNotificationPermission, 
  showBrowserNotification, 
  getAlertMessage, 
  getAlertType 
} from '../utils/notifications';

const PredictPage = ({ addPrediction }) => {
  const [currentResult, setCurrentResult] = useState(null);
  const [alertModal, setAlertModal] = useState(null);
  const [toast, setToast] = useState(null);

  // Dataset & scraping stats state
  const [stats, setStats] = useState(null);
  const [statsLoading, setStatsLoading] = useState(true);
  const [statsError, setStatsError] = useState(null);
  const [scrapeLoading, setScrapeLoading] = useState(false);

  const fetchStats = async () => {
    try {
      setStatsLoading(true);
      const res = await axios.get('http://localhost:5000/dataset/stats');
      setStats(res.data);
      setStatsError(null);
    } catch (err) {
      console.error('Error fetching dataset stats', err);
      setStatsError('Unable to load dataset statistics');
    } finally {
      setStatsLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    // Request notification permission on page load
    requestNotificationPermission();
  }, []);

  const handleScrapeRefresh = async () => {
    try {
      setScrapeLoading(true);
      await axios.post('http://localhost:5000/scraping/run');
      await fetchStats();
    } catch (err) {
      console.error('Error running scrapers', err);
      setStatsError('Error running web scrapers');
    } finally {
      setScrapeLoading(false);
    }
  };

  const handlePredictionResult = (result) => {
    setCurrentResult(result);
    addPrediction(result);

    const severity = result?.Predicted_Severity_Level || 'Low';
    const location = result?.location || { city: 'Unknown' };

    // Generate alert message
    const alertMsg = getAlertMessage(severity, location);
    const alertType = getAlertType(severity);

    // Show toast notification for all severity levels
    setToast({
      message: alertMsg,
      type: alertType
    });

    // Show browser notification for Medium, High, and Critical
    if (severity !== 'Low') {
      showBrowserNotification('Crime Risk Alert', {
        body: alertMsg,
        tag: 'crime-alert',
        requireInteraction: severity === 'Critical' || severity === 'High'
      });
    }

    // Show modal for High and Critical
    if (severity === "High" || severity === "Critical") {
      const modalType = severity === "Critical" ? "critical" : "high";
      setAlertModal({
        title: `🚨 ${severity} Risk Crime Alert`,
        message: result.alert_message || 
          `A ${severity.toLowerCase()}-risk area has been detected at ${location.city || 'this location'}.\n\n` +
          `**Safety Recommendations:**\n` +
          `• Avoid this area if possible\n` +
          `• If you must go, travel in groups\n` +
          `• Stay in well-lit, populated areas\n` +
          `• Keep emergency contacts ready\n` +
          `• Report any suspicious activity\n` +
          `• Call 100 in case of emergency`,
        type: modalType
      });
    }
  };

  const totalRecords = stats?.combined_records ?? 0;
  const originalRecords = stats?.original_records ?? 0;
  const scrapedRecords = stats?.scraped_records ?? 0;
  const cities = stats?.cities ?? 0;
  const crimeTypes = stats?.crime_types ?? 0;
  const sev = stats?.severity_distribution || {};

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="container mx-auto px-4 py-8"
    >
      {/* Dataset statistics header */}
      <div className="max-w-6xl mx-auto mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
            <span role="img" aria-label="dataset">📊</span> Dataset Statistics
          </h2>
          <button
            onClick={handleScrapeRefresh}
            disabled={scrapeLoading}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold shadow-md disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {scrapeLoading ? 'Scraping...' : 'Scrape & Refresh'}
          </button>
        </div>

        {statsLoading ? (
          <p className="text-gray-500">Loading dataset statistics...</p>
        ) : statsError ? (
          <p className="text-red-500 text-sm">{statsError}</p>
        ) : stats && stats.success ? (
          <div className="bg-blue-50 border border-blue-100 rounded-2xl p-5 shadow-sm">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
              <div className="bg-white rounded-xl p-4 shadow-sm">
                <p className="text-xs text-gray-500 mb-1">Total Records</p>
                <p className="text-2xl font-bold text-blue-800">{totalRecords.toLocaleString()}</p>
              </div>
              <div className="bg-white rounded-xl p-4 shadow-sm">
                <p className="text-xs text-gray-500 mb-1">Original Dataset</p>
                <p className="text-2xl font-bold text-green-700">{originalRecords.toLocaleString()}</p>
              </div>
              <div className="bg-white rounded-xl p-4 shadow-sm">
                <p className="text-xs text-gray-500 mb-1">Scraped Records</p>
                <p className="text-2xl font-bold text-purple-700">{scrapedRecords.toLocaleString()}</p>
                <p className="text-[11px] text-purple-500 mt-1">Live from India.com & Google News</p>
              </div>
              <div className="bg-white rounded-xl p-4 shadow-sm">
                <p className="text-xs text-gray-500 mb-1">Combined Dataset</p>
                <p className="text-2xl font-bold text-orange-700">{totalRecords.toLocaleString()}</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white rounded-xl p-4 shadow-sm">
                <p className="text-xs text-gray-500 mb-1">Cities Covered</p>
                <p className="text-2xl font-bold text-blue-800">{cities}</p>
              </div>
              <div className="bg-white rounded-xl p-4 shadow-sm">
                <p className="text-xs text-gray-500 mb-1">Crime Types</p>
                <p className="text-2xl font-bold text-blue-800">{crimeTypes}</p>
              </div>
              <div className="bg-white rounded-xl p-4 shadow-sm">
                <p className="text-xs text-gray-500 mb-2">Severity Distribution</p>
                <div className="text-xs text-gray-700 space-y-1">
                  <p>Critical: <span className="font-semibold">{sev.Critical ?? 0}</span></p>
                  <p>High: <span className="font-semibold">{sev.High ?? 0}</span></p>
                  <p>Low: <span className="font-semibold">{sev.Low ?? 0}</span></p>
                  <p>Medium: <span className="font-semibold">{sev.Medium ?? 0}</span></p>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <p className="text-sm text-gray-500">No dataset statistics available.</p>
        )}
      </div>

      <div className="max-w-4xl mx-auto">
        <InputForm onPredictionResult={handlePredictionResult} />
        <ResultCard result={currentResult} />
      </div>

      {/* Alert Modal */}
      {alertModal && (
        <Modal
          title={alertModal.title}
          message={alertModal.message}
          type={alertModal.type || 'warning'}
          onClose={() => setAlertModal(null)}
        />
      )}

      {/* Toast Notification */}
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
          duration={toast.type === 'critical' ? 8000 : 5000}
        />
      )}
    </motion.div>
  );
};

export default PredictPage;
