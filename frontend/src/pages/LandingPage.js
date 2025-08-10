import React from 'react';
import { 
  Play, Music, Zap, Brain, Award, ArrowRight, 
  Star, Crown, Shield, Sparkles, Users, TrendingUp,
  Headphones, Volume2, BarChart3, Activity,
  CheckCircle, ExternalLink
} from 'lucide-react';

const LandingPage = ({ systemStatus, onStartDAW, onStartV4V5DAW }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 text-white">
      {/* Hero Section */}
      <section className="relative overflow-hidden py-20">
        {/* Background Effects */}
        <div className="absolute inset-0 bg-gradient-to-r from-purple-500/10 to-blue-500/10 animate-pulse"></div>
        
        {/* Background Drumset Image */}
        <div className="absolute right-0 top-1/2 transform -translate-y-1/2 opacity-10 z-0">
          <div className="w-96 h-96 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full blur-3xl"></div>
        </div>
        
        <div className="relative z-10 max-w-7xl mx-auto px-4">
          <div className="text-center space-y-8">
            {/* Logo and Title */}
            <div className="space-y-6">
              <div className="flex items-center justify-center space-x-4">
                <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-blue-600 rounded-xl flex items-center justify-center shadow-2xl">
                  <Music className="w-10 h-10 text-white" />
                </div>
                <div>
                  <h1 className="text-6xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
                    DrumTracKAI
                  </h1>
                  <p className="text-2xl text-gray-300">Professional DAW with LLM-Driven Drum Generation</p>
                </div>
              </div>
            </div>

            {/* Hero Description */}
            <div className="max-w-4xl mx-auto space-y-6">
              <h2 className="text-4xl font-bold text-white">
                The Future of Drum Production is Here
              </h2>
              <p className="text-xl text-gray-300 leading-relaxed">
                Experience the world's first LLM-powered drum generation system integrated into a professional DAW. 
                Create authentic, human-like drum performances with advanced AI analysis and real-time editing.
              </p>
            </div>

            {/* Key Features */}
            <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
              <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-purple-500/20">
                <Brain className="w-12 h-12 text-purple-400 mb-4 mx-auto" />
                <h3 className="text-xl font-bold mb-2">LLM-Driven Generation</h3>
                <p className="text-gray-300">Advanced AI analyzes musical context and generates authentic drum patterns with human-like characteristics.</p>
              </div>
              
              <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-blue-500/20">
                <Volume2 className="w-12 h-12 text-blue-400 mb-4 mx-auto" />
                <h3 className="text-xl font-bold mb-2">Professional DAW</h3>
                <p className="text-gray-300">Full-featured digital audio workstation with multi-track editing, mixing, and real-time audio processing.</p>
              </div>
              
              <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-green-500/20">
                <Activity className="w-12 h-12 text-green-400 mb-4 mx-auto" />
                <h3 className="text-xl font-bold mb-2">Real-Time Editing</h3>
                <p className="text-gray-300">Quantize, humanize, and apply swing with instant preview. Undo/redo system for non-destructive editing.</p>
              </div>
            </div>

            {/* Call to Action */}
            <div className="space-y-6">
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                <button
                  onClick={onStartDAW}
                  className="flex items-center space-x-3 px-8 py-4 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 rounded-xl text-lg font-semibold transition-all duration-300 shadow-2xl hover:shadow-purple-500/25"
                >
                  <Play className="w-6 h-6" />
                  <span>Launch Professional DAW</span>
                  <ArrowRight className="w-5 h-5" />
                </button>
                
                <button
                  onClick={onStartV4V5DAW}
                  className="flex items-center space-x-3 px-8 py-4 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 rounded-xl text-lg font-semibold transition-all duration-300 shadow-2xl hover:shadow-emerald-500/25"
                >
                  <Sparkles className="w-6 h-6" />
                  <span>Launch v4/v5 WebDAW</span>
                  <ArrowRight className="w-5 h-5" />
                </button>
                
                <div className="flex items-center space-x-2 text-sm text-gray-400">
                  <div className={`w-2 h-2 rounded-full ${
                    systemStatus?.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'
                  }`}></div>
                  <span>
                    {systemStatus?.status === 'healthy' ? 'Backend Online' : 'Backend Offline'}
                  </span>
                </div>
              </div>
              
              <p className="text-gray-400">
                No installation required • Browser-based • Professional grade
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gray-900/50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Advanced Features</h2>
            <p className="text-xl text-gray-300">Everything you need for professional drum production</p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-purple-600 rounded-full flex items-center justify-center mx-auto">
                <Users className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-lg font-semibold">Drummer Personalities</h3>
              <p className="text-gray-400">Choose from curated drummer profiles with authentic playing styles</p>
            </div>
            
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto">
                <BarChart3 className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-lg font-semibold">Audio Analysis</h3>
              <p className="text-gray-400">Intelligent stem separation and musical structure analysis</p>
            </div>
            
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-green-600 rounded-full flex items-center justify-center mx-auto">
                <Zap className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-lg font-semibold">Real-Time Preview</h3>
              <p className="text-gray-400">Audition generated patterns before applying to your project</p>
            </div>
            
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-orange-600 rounded-full flex items-center justify-center mx-auto">
                <Crown className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-lg font-semibold">Professional Quality</h3>
              <p className="text-gray-400">Studio-grade audio processing and export capabilities</p>
            </div>
          </div>
        </div>
      </section>

      {/* Technology Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Powered by Advanced AI</h2>
            <p className="text-xl text-gray-300">ChatGPT-5 integration with sophisticated drum analysis</p>
          </div>
          
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-6">
              <div className="flex items-start space-x-4">
                <CheckCircle className="w-6 h-6 text-green-500 mt-1 flex-shrink-0" />
                <div>
                  <h3 className="text-lg font-semibold mb-2">LLM-Driven Pattern Generation</h3>
                  <p className="text-gray-300">Advanced language models analyze musical context to generate authentic drum patterns</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-4">
                <CheckCircle className="w-6 h-6 text-green-500 mt-1 flex-shrink-0" />
                <div>
                  <h3 className="text-lg font-semibold mb-2">Style Vector Encoding</h3>
                  <p className="text-gray-300">Sophisticated analysis of drummer characteristics and musical styles</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-4">
                <CheckCircle className="w-6 h-6 text-green-500 mt-1 flex-shrink-0" />
                <div>
                  <h3 className="text-lg font-semibold mb-2">Multi-Section Cohesion</h3>
                  <p className="text-gray-300">Generate consistent patterns across song sections with intelligent variation</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-4">
                <CheckCircle className="w-6 h-6 text-green-500 mt-1 flex-shrink-0" />
                <div>
                  <h3 className="text-lg font-semibold mb-2">Humanization & Swing</h3>
                  <p className="text-gray-300">Apply natural timing variations and groove characteristics</p>
                </div>
              </div>
            </div>
            
            <div className="bg-gradient-to-br from-purple-900/50 to-blue-900/50 rounded-2xl p-8 border border-purple-500/20">
              <div className="text-center space-y-4">
                <Brain className="w-16 h-16 text-purple-400 mx-auto" />
                <h3 className="text-2xl font-bold">88.7% Sophistication</h3>
                <p className="text-gray-300">Expert-level AI model trained on thousands of professional drum performances</p>
                
                <div className="grid grid-cols-2 gap-4 mt-6">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-400">5,650+</div>
                    <div className="text-sm text-gray-400">Training Files</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-400">Real-time</div>
                    <div className="text-sm text-gray-400">Generation</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 bg-gray-900 border-t border-gray-800">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center space-y-4">
            <div className="flex items-center justify-center space-x-2">
              <Music className="w-6 h-6 text-purple-500" />
              <span className="text-xl font-bold">DrumTracKAI</span>
            </div>
            <p className="text-gray-400">
              Professional drum production powered by advanced AI
            </p>
            <div className="flex justify-center space-x-6 text-sm text-gray-500">
              <span>© 2025 DrumTracKAI</span>
              <span>•</span>
              <span>Professional DAW</span>
              <span>•</span>
              <span>LLM Integration</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
