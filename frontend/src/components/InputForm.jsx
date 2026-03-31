import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';

const InputForm = ({ onPredictionResult }) => {
  const [formData, setFormData] = useState({
    City: '',
    Latitude: '',
    Longitude: '',
    Population_Density: '',
    Previous_Crimes_Area: '',
    Police_Station_Distance: '',
    Patrol_Intensity: 'Medium',
    State: 'Maharashtra',
    Day_of_Week: '',
    Month: '',
    Time_Slot: ''
  });

  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const now = new Date();
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const months = ['January', 'February', 'March', 'April', 'May', 'June', 
                    'July', 'August', 'September', 'October', 'November', 'December'];
    
    const hour = now.getHours();
    let timeSlot;
    if (hour >= 5 && hour < 12) timeSlot = 'Morning';
    else if (hour >= 12 && hour < 17) timeSlot = 'Afternoon';
    else if (hour >= 17 && hour < 21) timeSlot = 'Evening';
    else timeSlot = 'Night';

    setFormData(prev => ({
      ...prev,
      Day_of_Week: days[now.getDay()],
      Month: months[now.getMonth()],
      Time_Slot: timeSlot
    }));
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const getMyLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setFormData(prev => ({
            ...prev,
            Latitude: position.coords.latitude.toFixed(6),
            Longitude: position.coords.longitude.toFixed(6)
          }));
        },
        (error) => {
          alert('Error getting location: ' + error.message);
        }
      );
    } else {
      alert('Geolocation is not supported by your browser');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axios.post('http://localhost:5000/predict', {
        ...formData,
        Population_Density: parseInt(formData.Population_Density),
        Previous_Crimes_Area: parseInt(formData.Previous_Crimes_Area),
        Police_Station_Distance: parseFloat(formData.Police_Station_Distance),
        Latitude: parseFloat(formData.Latitude),
        Longitude: parseFloat(formData.Longitude)
      });

    const predictionData = {
  ...response.data,
  alert_message: response.data.alert_message,      // ⬅ NEW
  reason: response.data.reason,                    // ⬅ NEW
  suggestions: response.data.suggestions,          // ⬅ NEW
  severity: response.data.Predicted_Severity_Level, // ⬅ NEW
  location: {
    city: formData.City,
    lat: parseFloat(formData.Latitude),
    lng: parseFloat(formData.Longitude)
  },
  timestamp: new Date().toISOString()
};

      
      console.log('📍 Prediction Coordinates:', {
        inputLat: formData.Latitude,
        inputLng: formData.Longitude,
        parsedLat: predictionData.location.lat,
        parsedLng: predictionData.location.lng
      });
      
      onPredictionResult(predictionData);
    } catch (error) {
      console.error('Error making prediction:', error);
      alert('Error making prediction. Please ensure the backend server is running.');
    } finally {
      setLoading(false);
    }
  };

  const inputClass = "w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all duration-200 hover:border-gray-400 bg-white";
  const readOnlyClass = "w-full px-4 py-3 border-2 border-blue-200 rounded-xl bg-gradient-to-r from-blue-50 to-indigo-50 text-blue-900 font-semibold cursor-not-allowed";
  const labelClass = "block text-sm font-semibold text-gray-700 mb-2";

  return (
    <motion.form
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      onSubmit={handleSubmit}
      className="bg-gradient-to-br from-white via-blue-50 to-indigo-50 p-8 rounded-2xl shadow-2xl border-2 border-blue-100"
    >
      <div className="mb-8">
        <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-900 via-blue-700 to-indigo-600 bg-clip-text text-transparent mb-2">
          🎯 Crime Hotspot Prediction
        </h2>
        <p className="text-gray-600 text-sm">Enter location details to predict crime hotspot severity</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Auto-filled Time Fields */}
        <div>
          <label className={labelClass}>📅 Day of Week</label>
          <input
            type="text"
            name="Day_of_Week"
            value={formData.Day_of_Week}
            readOnly
            className={readOnlyClass}
          />
        </div>

        <div>
          <label className={labelClass}>📆 Month</label>
          <input
            type="text"
            name="Month"
            value={formData.Month}
            readOnly
            className={readOnlyClass}
          />
        </div>

        <div>
          <label className={labelClass}>⏰ Time Slot</label>
          <input
            type="text"
            name="Time_Slot"
            value={formData.Time_Slot}
            readOnly
            className={readOnlyClass}
          />
        </div>

        {/* Manual Input Fields */}
        <div>
          <label className={labelClass}>🏙️ City</label>
          <input
            type="text"
            name="City"
            value={formData.City}
            onChange={handleChange}
            className={inputClass}
            placeholder="e.g., Mumbai"
            required
          />
        </div>

        <div>
          <label className={labelClass}>🌐 Latitude</label>
          <input
            type="number"
            step="any"
            name="Latitude"
            value={formData.Latitude}
            onChange={handleChange}
            className={inputClass}
            placeholder="e.g., 19.0760"
            required
          />
        </div>

        <div className="relative">
          <label className={labelClass}>🌐 Longitude</label>
          <div className="flex gap-2">
            <input
              type="number"
              step="any"
              name="Longitude"
              value={formData.Longitude}
              onChange={handleChange}
              className={inputClass}
              placeholder="e.g., 72.8777"
              required
            />
            <button
              type="button"
              onClick={getMyLocation}
              className="px-4 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl hover:from-green-700 hover:to-emerald-700 transition-all duration-200 shadow-lg hover:shadow-xl font-semibold whitespace-nowrap"
            >
              📍 Get
            </button>
          </div>
        </div>

        <div>
          <label className={labelClass}>👥 Population Density</label>
          <input
            type="number"
            name="Population_Density"
            value={formData.Population_Density}
            onChange={handleChange}
            className={inputClass}
            placeholder="e.g., 25000"
            required
          />
        </div>

        <div>
          <label className={labelClass}>📊 Previous Crimes in Area</label>
          <input
            type="number"
            name="Previous_Crimes_Area"
            value={formData.Previous_Crimes_Area}
            onChange={handleChange}
            className={inputClass}
            placeholder="e.g., 12"
            required
          />
        </div>

        <div>
          <label className={labelClass}>🚓 Police Station Distance (km)</label>
          <input
            type="number"
            step="0.1"
            name="Police_Station_Distance"
            value={formData.Police_Station_Distance}
            onChange={handleChange}
            className={inputClass}
            placeholder="e.g., 2.5"
            required
          />
        </div>

        <div>
          <label className={labelClass}>🚔 Patrol Intensity</label>
          <select
            name="Patrol_Intensity"
            value={formData.Patrol_Intensity}
            onChange={handleChange}
            className={inputClass}
          >
            <option value="Low">Low</option>
            <option value="Medium">Medium</option>
            <option value="High">High</option>
          </select>
        </div>

        <div>
          <label className={labelClass}>📍 State</label>
          <select
            name="State"
            value={formData.State}
            onChange={handleChange}
            className={inputClass}
          >
            <option value="Maharashtra">Maharashtra</option>
            <option value="Gujarat">Gujarat</option>
            <option value="Karnataka">Karnataka</option>
            <option value="Tamil Nadu">Tamil Nadu</option>
            <option value="Delhi">Delhi</option>
            <option value="Rajasthan">Rajasthan</option>
            <option value="Uttar Pradesh">Uttar Pradesh</option>
            <option value="West Bengal">West Bengal</option>
            <option value="Telangana">Telangana</option>
          </select>
        </div>
      </div>

      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        type="submit"
        disabled={loading}
        className="w-full mt-8 bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-700 hover:from-blue-700 hover:via-blue-800 hover:to-indigo-800 text-white font-bold py-4 rounded-xl transition-all duration-300 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed shadow-xl hover:shadow-2xl"
      >
        {loading ? (
          <span className="flex items-center justify-center gap-3">
            <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Predicting...
          </span>
        ) : (
          '🔮 Predict Crime Hotspot'
        )}
      </motion.button>
    </motion.form>
  );
};

export default InputForm;
