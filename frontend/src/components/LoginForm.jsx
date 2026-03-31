import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import axios from 'axios';

const LoginForm = () => {
  const [username, setUsername] = useState('');
  const [stats, setStats] = useState(null);
  const [statsError, setStatsError] = useState(null);
  const [statsLoading, setStatsLoading] = useState(true);
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    if (username.trim()) {
      localStorage.setItem('username', username);
      navigate('/predict');
    }
  };

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setStatsLoading(true);
        const res = await axios.get('http://localhost:5000/scraping/stats');
        setStats(res.data);
        setStatsError(null);
      } catch (err) {
        console.error('Error fetching scraping stats', err);
        setStatsError('Unable to load scraping statistics');
      } finally {
        setStatsLoading(false);
      }
    };

    fetchStats();
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="min-h-[80vh] flex items-center justify-center"
    >
      <div className="bg-white p-8 rounded-2xl shadow-2xl w-full max-w-md">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-primary mb-2">Welcome</h2>
          <p className="text-gray-600">Crime Hotspot Prediction System</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-secondary focus:border-transparent outline-none transition"
              placeholder="Enter your username"
              required
            />
          </div>

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            type="submit"
            className="w-full bg-primary hover:bg-blue-900 text-white font-semibold py-3 rounded-lg transition duration-200"
          >
            Login
          </motion.button>
        </form>

        <div className="mt-6 text-center text-sm text-gray-500">
          <p>Current Time: {new Date().toLocaleString()}</p>
        </div>

        <div className="mt-6 text-sm bg-gray-50 border border-gray-200 rounded-xl p-4">
          <h3 className="text-base font-semibold text-gray-700 mb-2">Web Scraping Status</h3>
          {statsLoading && <p className="text-gray-500">Loading scraping statistics...</p>}
          {!statsLoading && statsError && (
            <p className="text-red-500">{statsError}</p>
          )}
          {!statsLoading && !statsError && stats && (
            stats.has_data ? (
              <div className="grid grid-cols-2 gap-3 text-left">
                <div>
                  <p className="text-gray-600">Total scraped events</p>
                  <p className="text-xl font-bold text-primary">{stats.total_records}</p>
                </div>
                <div>
                  <p className="text-gray-600">Cities covered</p>
                  <p className="text-xl font-bold text-secondary">{stats.unique_cities}</p>
                </div>
                <div className="col-span-2 text-gray-600 text-xs mt-2">
                  {stats.earliest_date && stats.latest_date && (
                    <p>Data range: {stats.earliest_date} → {stats.latest_date}</p>
                  )}
                  {stats.last_updated && (
                    <p>Last updated: {new Date(stats.last_updated).toLocaleString()}</p>
                  )}
                </div>
              </div>
            ) : (
              <p className="text-gray-500">
                No scraped data found yet. Run the web scraper to start collecting live crime events.
              </p>
            )
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default LoginForm;
