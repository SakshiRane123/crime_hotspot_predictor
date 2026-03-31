import { motion } from 'framer-motion';

const AboutPage = () => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="container mx-auto px-4 py-8"
    >
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-xl shadow-lg p-8">
          <h1 className="text-4xl font-bold text-primary mb-6">About Crime Hotspot Predictor</h1>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-secondary mb-3">Project Overview</h2>
            <p className="text-gray-700 leading-relaxed">
              The Crime Hotspot Prediction System is an AI-powered web application designed to predict 
              whether a specific location is a crime hotspot and determine its severity level. This tool 
              helps law enforcement agencies, urban planners, and citizens make informed decisions about 
              public safety.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-secondary mb-3">Key Features</h2>
            <ul className="list-disc list-inside space-y-2 text-gray-700">
              <li>Real-time crime hotspot prediction using machine learning</li>
              <li>Severity classification: Low, Medium, High, and Critical</li>
              <li>Interactive map visualization with color-coded risk zones</li>
              <li>Geolocation support for automatic coordinate detection</li>
              <li>Time-aware predictions considering day, month, and time of day</li>
              <li>Multiple crime type analysis (Theft, Robbery, Assault, etc.)</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-secondary mb-3">Technology Stack</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="font-bold text-primary mb-2">Frontend</h3>
                <ul className="text-sm text-gray-700 space-y-1">
                  <li>• React 18</li>
                  <li>• Vite</li>
                  <li>• Tailwind CSS</li>
                  <li>• React Router</li>
                  <li>• React Leaflet</li>
                  <li>• Framer Motion</li>
                  <li>• Axios</li>
                </ul>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <h3 className="font-bold text-primary mb-2">Backend</h3>
                <ul className="text-sm text-gray-700 space-y-1">
                  <li>• Flask (Python)</li>
                  <li>• Scikit-learn</li>
                  <li>• Pandas & NumPy</li>
                  <li>• Joblib</li>
                  <li>• Flask-CORS</li>
                </ul>
              </div>
            </div>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-secondary mb-3">How It Works</h2>
            <div className="space-y-3 text-gray-700">
              <div className="flex items-start gap-3">
                <span className="bg-primary text-white rounded-full w-8 h-8 flex items-center justify-center flex-shrink-0 font-bold">1</span>
                <div>
                  <h4 className="font-semibold">Data Input</h4>
                  <p className="text-sm">User enters location details and contextual information like population density, patrol intensity, and crime history.</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <span className="bg-primary text-white rounded-full w-8 h-8 flex items-center justify-center flex-shrink-0 font-bold">2</span>
                <div>
                  <h4 className="font-semibold">ML Prediction</h4>
                  <p className="text-sm">The machine learning model analyzes the input features and predicts hotspot probability and severity level.</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <span className="bg-primary text-white rounded-full w-8 h-8 flex items-center justify-center flex-shrink-0 font-bold">3</span>
                <div>
                  <h4 className="font-semibold">Visualization</h4>
                  <p className="text-sm">Results are displayed with color-coded severity indicators and plotted on an interactive map.</p>
                </div>
              </div>
            </div>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-secondary mb-3">Severity Levels</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="border-l-4 border-green-500 bg-green-50 p-3 rounded">
                <h4 className="font-bold text-green-800">🟢 Low Risk</h4>
                <p className="text-sm text-gray-700">Safe area with minimal crime history</p>
              </div>
              <div className="border-l-4 border-yellow-500 bg-yellow-50 p-3 rounded">
                <h4 className="font-bold text-yellow-800">🟡 Medium Risk</h4>
                <p className="text-sm text-gray-700">Moderate caution advised</p>
              </div>
              <div className="border-l-4 border-orange-500 bg-orange-50 p-3 rounded">
                <h4 className="font-bold text-orange-800">🟠 High Risk</h4>
                <p className="text-sm text-gray-700">Elevated crime activity</p>
              </div>
              <div className="border-l-4 border-red-500 bg-red-50 p-3 rounded">
                <h4 className="font-bold text-red-800">🔴 Critical Risk</h4>
                <p className="text-sm text-gray-700">High crime hotspot zone</p>
              </div>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-secondary mb-3">Use Cases</h2>
            <ul className="list-disc list-inside space-y-2 text-gray-700">
              <li><strong>Law Enforcement:</strong> Optimize patrol routes and resource allocation</li>
              <li><strong>Urban Planning:</strong> Identify areas needing infrastructure improvements</li>
              <li><strong>Public Safety:</strong> Inform citizens about safety concerns in different areas</li>
              <li><strong>Real Estate:</strong> Provide safety insights for property assessments</li>
              <li><strong>Emergency Services:</strong> Better prepare for incidents in high-risk zones</li>
            </ul>
          </section>
        </div>
      </div>
    </motion.div>
  );
};

export default AboutPage;
