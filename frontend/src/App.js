import React, { useState, useEffect } from 'react';
import './App.css';

// Import ChatGPT-5 DAW components
import ProfessionalDAW from './components/ProfessionalDAW';
import LandingPage from './pages/LandingPage';
import { AppDAW } from './daw/AppDAW';

// Import contexts
import { AuthProvider } from './contexts/AuthContext';

function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [systemStatus, setSystemStatus] = useState(null);
  const [currentView, setCurrentView] = useState('landing'); // 'landing', 'daw', or 'v4v5'

  useEffect(() => {
    // Check system status on app load
    checkSystemStatus();
  }, []);

  const checkSystemStatus = async () => {
    try {
      const response = await fetch('/api/health');
      const data = await response.json();
      setSystemStatus(data);
    } catch (error) {
      console.error('System status check failed:', error);
      setSystemStatus({ status: 'error', message: 'Backend unavailable' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartDAW = () => {
    setCurrentView('daw');
  };

  const handleStartV4V5DAW = () => {
    setCurrentView('v4v5');
  };

  const handleBackToLanding = () => {
    setCurrentView('landing');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
          <p className="text-white text-lg">Loading DrumTracKAI Professional DAW...</p>
          <p className="text-gray-400 text-sm mt-2">Initializing LLM-driven drum generation...</p>
        </div>
      </div>
    );
  }

  return (
    <AuthProvider>
      <div className="App min-h-screen bg-gray-900">
        {currentView === 'landing' ? (
          <LandingPage 
            systemStatus={systemStatus} 
            onStartDAW={handleStartDAW}
            onStartV4V5DAW={handleStartV4V5DAW}
          />
        ) : currentView === 'v4v5' ? (
          <div className="relative">
            <div className="absolute top-2 left-2 z-10">
              <button 
                onClick={handleBackToLanding}
                className="px-3 py-1 bg-neutral-800 text-white rounded hover:bg-neutral-700"
              >
                ← Back to Landing
              </button>
            </div>
            <AppDAW />
          </div>
        ) : (
          <ProfessionalDAW 
            onBack={handleBackToLanding}
            systemStatus={systemStatus}
          />
        )}
      </div>
    </AuthProvider>
  );
}

export default App;
