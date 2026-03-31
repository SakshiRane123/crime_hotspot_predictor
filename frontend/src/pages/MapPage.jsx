import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import HeatMap from '../components/HeatMap';
import RiskExplanation from '../components/RiskExplanation';
import axios from 'axios';

const MapPage = ({ predictions }) => {
  const [communityReports, setCommunityReports] = useState([]);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [showExplanation, setShowExplanation] = useState(false);

  // Scroll to top whenever this page loads
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  // Fetch community reports
  useEffect(() => {
    const fetchReports = async () => {
      try {
        const response = await axios.get('http://localhost:5000/get-community-reports');
        if (response.data.success) {
          setCommunityReports(response.data.reports || []);
        }
      } catch (error) {
        console.error('Error fetching community reports:', error);
      }
    };

    fetchReports();
    // Refresh reports every 30 seconds
    const interval = setInterval(fetchReports, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleLocationClick = (lat, lng) => {
    setSelectedLocation({ lat, lng });
    setShowExplanation(true);
  };

  const riskColors = {
    Low: "bg-green-500",
    Medium: "bg-yellow-500",
    High: "bg-orange-500",
    Critical: "bg-red-500"
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="container mx-auto px-4 py-8"
    >
      {/* TITLE */}
      <div className="mb-6">
        <h1 className="text-3xl font-extrabold bg-gradient-to-r from-purple-800 to-blue-700 text-transparent bg-clip-text">
          Crime Hotspot Map
        </h1>
        <p className="text-gray-600 mt-1">
          Live prediction-based visualization of high-risk crime zones.
        </p>
      </div>

      {/* LEGEND BOX */}
      <div className="bg-white rounded-xl shadow-lg p-4 mb-6 border border-gray-200">
        <h3 className="font-semibold text-lg mb-3">Legend</h3>

        <div className="flex flex-wrap gap-4">
          {Object.keys(riskColors).map((level) => (
            <div key={level} className="flex items-center gap-2">
              <div className={`w-6 h-6 rounded-full ${riskColors[level]}`}></div>
              <span className="text-sm">{level} Risk</span>
            </div>
          ))}
        </div>

        <p className="text-sm text-gray-600 mt-3">
          Total Predictions:{' '}
          <span className="font-semibold text-primary">{predictions?.length || 0}</span>
        </p>
      </div>

      {/* MAP WRAPPER */}
      <div className="rounded-xl overflow-hidden shadow-xl" style={{ height: '600px' }}>
        <HeatMap 
          predictions={predictions || []} 
          communityReports={communityReports}
          onLocationClick={handleLocationClick}
        />
      </div>

      {/* Risk Explanation Modal */}
      {showExplanation && selectedLocation && (
        <RiskExplanation
          latitude={selectedLocation.lat}
          longitude={selectedLocation.lng}
          onClose={() => {
            setShowExplanation(false);
            setSelectedLocation(null);
          }}
        />
      )}
    </motion.div>
  );
};

export default MapPage;
