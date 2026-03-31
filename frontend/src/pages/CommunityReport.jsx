import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';
import { showBrowserNotification, requestNotificationPermission } from '../utils/notifications';

const CommunityReport = () => {
  const [formData, setFormData] = useState({
    type: 'theft',
    location: '',
    description: '',
    image: ''
  });
  const [locationDetected, setLocationDetected] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [showToast, setShowToast] = useState(false);

  useEffect(() => {
    requestNotificationPermission();
  }, []);

  const crimeTypes = [
    { value: 'theft', label: 'Theft' },
    { value: 'harassment', label: 'Harassment' },
    { value: 'fight', label: 'Fight/Violence' },
    { value: 'other', label: 'Other' }
  ];

  const handleAutoDetectLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const lat = position.coords.latitude;
          const lng = position.coords.longitude;
          setFormData(prev => ({
            ...prev,
            location: `${lat},${lng}`
          }));
          setLocationDetected(true);
        },
        (error) => {
          alert('Unable to detect location. Please enter manually.');
          console.error('Geolocation error:', error);
        }
      );
    } else {
      alert('Geolocation is not supported by your browser.');
    }
  };

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64String = reader.result;
        setFormData(prev => ({
          ...prev,
          image: base64String
        }));
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      const response = await axios.post('http://localhost:5000/report-crime', formData);
      
      if (response.data.success) {
        setShowToast(true);
        
        // Show browser notification
        showBrowserNotification('Report Submitted', {
          body: `Your ${formData.type} report has been submitted successfully. Thank you for keeping the community safe!`,
          tag: 'report-submitted'
        });
        
        // Reset form
        setFormData({
          type: 'theft',
          location: '',
          description: '',
          image: ''
        });
        setLocationDetected(false);
        
        // Hide toast after 5 seconds
        setTimeout(() => setShowToast(false), 5000);
      } else {
        alert('Failed to submit report. Please try again.');
      }
    } catch (error) {
      console.error('Error submitting report:', error);
      alert('Error submitting report. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      className="container mx-auto px-4 py-8 max-w-2xl"
    >
      {/* Toast Notification */}
      {showToast && (
        <motion.div
          initial={{ opacity: 0, y: -50, x: 300 }}
          animate={{ opacity: 1, y: 0, x: 0 }}
          exit={{ opacity: 0, x: 300 }}
          className="fixed top-20 right-4 bg-green-500 text-white px-6 py-4 rounded-lg shadow-2xl z-50 min-w-[300px] flex items-center gap-3"
        >
          <span className="text-2xl">✅</span>
          <div>
            <p className="font-bold">Report Submitted Successfully!</p>
            <p className="text-sm opacity-90">Thank you for keeping the community safe.</p>
          </div>
          <button
            onClick={() => setShowToast(false)}
            className="text-white hover:text-gray-200 font-bold text-xl ml-2"
          >
            ×
          </button>
        </motion.div>
      )}

      <div className="bg-white rounded-xl shadow-xl p-8">
        <h1 className="text-3xl font-extrabold bg-gradient-to-r from-purple-800 to-blue-700 text-transparent bg-clip-text mb-2">
          Community Crime Report
        </h1>
        <p className="text-gray-600 mb-6">
          Help keep your community safe by reporting incidents you've witnessed or experienced.
        </p>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Crime Type */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Crime Type <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.type}
              onChange={(e) => setFormData(prev => ({ ...prev, type: e.target.value }))}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            >
              {crimeTypes.map(type => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          {/* Location */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Location <span className="text-red-500">*</span>
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={formData.location}
                onChange={(e) => setFormData(prev => ({ ...prev, location: e.target.value }))}
                placeholder="Enter latitude,longitude (e.g., 19.0760,72.8777)"
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
              <button
                type="button"
                onClick={handleAutoDetectLocation}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                📍 Auto-detect
              </button>
            </div>
            {locationDetected && (
              <p className="text-sm text-green-600 mt-1">✓ Location detected successfully</p>
            )}
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Description <span className="text-red-500">*</span>
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              placeholder="Describe what happened, when, and any other relevant details..."
              rows="5"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          {/* Image Upload */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Image (Optional)
            </label>
            <input
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            {formData.image && (
              <p className="text-sm text-green-600 mt-1">✓ Image uploaded</p>
            )}
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={submitting}
            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {submitting ? 'Submitting...' : 'Submit Report'}
          </button>
        </form>
      </div>
    </motion.div>
  );
};

export default CommunityReport;


