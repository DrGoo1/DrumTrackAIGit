import React, { useState, useEffect } from 'react';
import { 
  Music, Star, Zap, Upload, Play, CheckCircle, ArrowRight, 
  Brain, AudioWaveform, Database, Crown, Shield, Sparkles,
  Users, TrendingUp, Award, Target, Headphones, Mic, LogOut
} from 'lucide-react';

// Import Components
import LandingPage from './pages/LandingPage';
import TierComparison from './pages/TierComparison';
import BasicTier from './pages/BasicTier';
import ProfessionalTier from './pages/ProfessionalTier';
import ExpertTier from './pages/ExpertTier';
import Studio from './pages/Studio';
import { Login, Register } from './components/AuthComponents';

// Import Context and Config
import { AuthProvider, useAuth } from './contexts/AuthContext';
import APP_CONFIG from './app.config';
import './App.css';

// Main App Component (wrapped with AuthProvider)
function AppContent() {
  const [currentPage, setCurrentPage] = useState('landing');
  const [selectedTier, setSelectedTier] = useState(null);
  
  // Get auth context
  const { 
    user, 
    tier, 
    isAuthenticated, 
    isLoading, 
    logout 
  } = useAuth();

  // Navigation handler
  const navigateTo = (page, tierSelection = null) => {
    setCurrentPage(page);
    if (tierSelection) setSelectedTier(tierSelection);
  };

  // Handle logout
  const handleLogout = async () => {
    await logout();
    navigateTo('landing');
  };

  // Tier data structure (enhanced from original)
  const tiers = {
    basic: {
      name: 'Basic',
      icon: Star,
      color: 'blue',
      price: '$0',
      period: '/month',
      description: 'Perfect for individual drummers and music students',
      features: [
        'Individual drum file analysis',
        'Basic pattern recognition',
        'Tempo and rhythm detection',
        'Simple beat matching',
        'Audio visualization',
        '10 analyses per month',
        'Standard support'
      ],
      capabilities: {
        sophistication: '65%',
        accuracy: '85%',
        processing: 'Standard',
        fileTypes: 'WAV, MP3',
        maxFileSize: '50MB',
        analysisTime: '30-60 seconds'
      }
    },
    professional: {
      name: 'Professional',
      icon: Zap,
      color: 'purple',
      price: '$29.99',
      period: '/month',
      description: 'Advanced analysis for producers and music professionals',
      features: [
        'Batch processing (up to 50 files)',
        'Advanced pattern analysis',
        'Signature song database access',
        'Real-time monitoring',
        'Professional visualizations',
        'Export capabilities',
        'Priority support',
        'API access'
      ],
      capabilities: {
        sophistication: '82%',
        accuracy: '91%',
        processing: 'Advanced',
        fileTypes: 'WAV, MP3, FLAC, M4A',
        maxFileSize: '200MB',
        analysisTime: '15-30 seconds'
      }
    },
    expert: {
      name: 'Expert',
      icon: Crown,
      color: 'gold',
      price: '$79.99',
      period: '/month',
      description: 'Ultimate AI-powered drum analysis with MVSep integration',
      features: [
        'Unlimited batch processing',
        'MVSep stem separation',
        'Expert Model (88.7% sophistication)',
        'Full song analysis',
        'Signature drummer recognition',
        'Custom model training',
        'White-label solutions',
        'Dedicated support'
      ],
      capabilities: {
        sophistication: '88.7%',
        accuracy: '94%',
        processing: 'Expert AI',
        fileTypes: 'All formats',
        maxFileSize: 'Unlimited',
        analysisTime: '5-15 seconds'
      }
    }
  };

  // Loading screen
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-blue-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Brain className="h-8 w-8 text-white animate-pulse" />
          </div>
          <h1 className="text-2xl font-bold text-white mb-2">DrumTracKAI</h1>
          <p className="text-gray-400">Loading your Studio...</p>
        </div>
      </div>
    );
  }

  const renderPage = () => {
    switch (currentPage) {
      case 'landing':
        return <LandingPage tiers={tiers} navigateTo={navigateTo} />;
      case 'comparison':
        return <TierComparison tiers={tiers} navigateTo={navigateTo} />;
      case 'basic':
        return <BasicTier tier={tiers.basic} navigateTo={navigateTo} />;
      case 'professional':
        return <ProfessionalTier tier={tiers.professional} navigateTo={navigateTo} />;
      case 'expert':
        return <ExpertTier tier={tiers.expert} navigateTo={navigateTo} />;
      case 'studio':
        return <Studio navigateTo={navigateTo} />;
      case 'login':
        return <Login navigateTo={navigateTo} />;
      case 'register':
        return <Register navigateTo={navigateTo} />;
      default:
        return <LandingPage tiers={tiers} navigateTo={navigateTo} />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Navigation Header */}
      <header className="bg-gradient-to-r from-purple-900 to-indigo-900 shadow-lg sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-2">
            {/* Logo */}
            <div 
              className="flex items-center cursor-pointer"
              onClick={() => navigateTo('landing')}
            >
              <div className="w-12 h-12 bg-white rounded-lg flex items-center justify-center overflow-hidden shadow-lg mr-3">
                <img 
                  src="/images/drumtrackai-logo.png" 
                  alt="DrumTracKAI Logo" 
                  className="w-full h-full object-contain p-1"
                />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">DrumTracKAI</h1>
                {isAuthenticated && (
                  <div className="text-xs text-purple-300">
                    {tier.charAt(0).toUpperCase() + tier.slice(1)} - {APP_CONFIG.tiers[tier]?.sophistication}
                  </div>
                )}
              </div>
            </div>
            
            {/* Navigation */}
            <div className="hidden md:flex items-center gap-6">
              <button 
                onClick={() => navigateTo('landing')}
                className={`text-sm transition-colors ${
                  currentPage === 'landing' ? 'text-white' : 'text-gray-300 hover:text-white'
                }`}
              >
                Home
              </button>
              
              {isAuthenticated && (
                <button 
                  onClick={() => navigateTo('studio')}
                  className={`text-sm transition-colors ${
                    currentPage === 'studio' ? 'text-white' : 'text-gray-300 hover:text-white'
                  }`}
                >
                  Studio
                </button>
              )}
              
              <button 
                onClick={() => navigateTo('comparison')}
                className={`text-sm transition-colors ${
                  currentPage === 'comparison' ? 'text-white' : 'text-gray-300 hover:text-white'
                }`}
              >
                Pricing
              </button>
              
              {/* Auth Buttons */}
              <div className="flex items-center gap-3">
                {isAuthenticated ? (
                  <div className="flex items-center gap-3">
                    <div className="text-sm text-gray-300">
                      Welcome, {user?.name}
                    </div>
                    <button 
                      onClick={handleLogout}
                      className="px-4 py-2 text-sm text-white border border-white/20 rounded-lg hover:bg-white/10 transition-all flex items-center gap-2"
                    >
                      <LogOut className="h-4 w-4" />
                      Logout
                    </button>
                  </div>
                ) : (
                  <>
                    <button 
                      onClick={() => navigateTo('login')}
                      className="px-4 py-2 text-sm text-white border border-white/20 rounded-lg hover:bg-white/10 transition-all"
                    >
                      Log In
                    </button>
                    <button 
                      onClick={() => navigateTo('register')}
                      className="px-4 py-2 text-sm bg-gradient-to-r from-purple-600 to-purple-700 text-white rounded-lg hover:from-purple-700 hover:to-purple-800 transition-all"
                    >
                      Sign Up
                    </button>
                  </>
                )}
              </div>
            </div>

            {/* Mobile Menu Button */}
            <div className="md:hidden">
              <button className="text-gray-300 hover:text-white">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main>
        {renderPage()}
      </main>

      {/* Footer */}
      <footer className="bg-black/40 backdrop-blur-md border-t border-white/10 mt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <Music className="h-6 w-6 text-purple-400" />
                <span className="text-white font-bold">DrumTracKAI</span>
              </div>
              <p className="text-gray-400 text-sm">
                Professional AI-powered drum analysis with advanced neural network sophistication.
              </p>
              {isAuthenticated && (
                <div className="mt-3">
                  <div className="text-sm text-purple-300">
                    Current Plan: {tier.charAt(0).toUpperCase() + tier.slice(1)}
                  </div>
                  <div className="text-xs text-gray-400">
                    AI Sophistication: {APP_CONFIG.tiers[tier]?.sophistication}
                  </div>
                </div>
              )}
            </div>
            
            <div>
              <h3 className="text-white font-semibold mb-3">Services</h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li>Drum Pattern Analysis</li>
                <li>Stem Separation</li>
                <li>Batch Processing</li>
                <li>Real-time Monitoring</li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-white font-semibold mb-3">Features</h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li>Expert Model (88.7%)</li>
                <li>Neural Processing</li>
                <li>Signature Songs</li>
                <li>Professional Analysis</li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-white font-semibold mb-3">Support</h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li>Documentation</li>
                <li>API Reference</li>
                <li>Community</li>
                <li>Contact</li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-white/10 mt-8 pt-6 text-center">
            <p className="text-gray-400 text-sm">
              © 2025 DrumTracKAI. Professional drum analysis powered by AI.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

// Root App Component with AuthProvider
function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;