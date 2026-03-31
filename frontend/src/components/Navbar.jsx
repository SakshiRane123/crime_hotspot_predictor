import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';

const Navbar = () => {
  const location = useLocation();
  
  const navItems = [
    { path: '/', label: 'Login' },
    { path: '/predict', label: 'Predict' },
    { path: '/map', label: 'Map' },
    { path: '/report', label: 'Report' },
    { path: '/about', label: 'About' }
  ];

  return (
    <motion.nav 
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5, type: "spring" }}
      className="bg-gradient-to-r from-blue-900 via-blue-800 to-indigo-900 text-white shadow-2xl"
    >
      <div className="container mx-auto px-6">
        <div className="flex items-center justify-between h-18">
          <div className="flex items-center space-x-3">
            <span className="text-3xl">🚨</span>
            <span className="text-2xl font-bold tracking-tight">Crime Hotspot Predictor</span>
          </div>
          
          <div className="flex space-x-2">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`px-5 py-2.5 rounded-xl transition-all duration-300 font-medium ${
                  location.pathname === item.path
                    ? 'bg-white text-blue-900 shadow-lg font-bold'
                    : 'hover:bg-blue-700 hover:shadow-md'
                }`}
              >
                {item.label}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </motion.nav>
  );
};

export default Navbar;
