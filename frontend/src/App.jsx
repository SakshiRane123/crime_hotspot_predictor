import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import LoginForm from './components/LoginForm';
import PredictPage from './pages/PredictPage';
import MapPage from './pages/MapPage';
import AboutPage from './pages/AboutPage';
import CommunityReport from './pages/CommunityReport';
import ChatbotWidget from './chatbot/ChatbotWidget';

function App() {
  const [predictions, setPredictions] = useState([]);

  const addPrediction = (prediction) => {
    setPredictions(prev => [...prev, prediction]);
  };

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <Routes>
          <Route path="/" element={<LoginForm />} />
          <Route path="/predict" element={<PredictPage addPrediction={addPrediction} />} />
          <Route path="/map" element={<MapPage predictions={predictions} />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/report" element={<CommunityReport />} />
        </Routes>
        <ChatbotWidget />
      </div>
    </Router>
  );
}

export default App;
