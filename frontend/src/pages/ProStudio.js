import React, { useState, useEffect, useRef } from 'react';
import { 
  Upload, Play, Pause, Download, Settings, Share, Eye, 
  Brain, AudioWaveform, Database, Crown, Star, Zap,
  CheckCircle, AlertCircle, Clock, FileAudio, Mic, Target,
  ArrowRight, Lock, Users, TrendingUp, X, Plus, Trash2,
  Music2, Sliders, Layers, Volume2, RotateCcw,
  Drum, Activity, Shuffle, BarChart3, Timer, Repeat,
  Search, Filter, Copy, Edit, Move, Maximize2, Minimize2,
  Headphones, VolumeX, Volume1, SkipBack,
  SkipForward, PlayCircle, PauseCircle, Square, Circle,
  Triangle, Hexagon, Waves, Signal,
  Gauge, Radar, Focus, Sparkles, ExternalLink
} from 'lucide-react';

const ProStudio = () => {
  // Main workflow state
  const [currentPhase, setCurrentPhase] = useState('upload');
  const [uploadedFile, setUploadedFile] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [reaperLaunched, setReaperLaunched] = useState(false);
  
  // Advanced audio analysis results
  const [audioAnalysis, setAudioAnalysis] = useState({
    tempo: null,
    key: null,
    timeSignature: null,
    style: null,
    structure: null,
    instruments: null,
    dynamics: null,
    harmony: null
  });

  // Creation options
  const [creationMode, setCreationMode] = useState(null);
  const [followTarget, setFollowTarget] = useState(null);
  
  // DAW-style arrangement state
  const [arrangement, setArrangement] = useState({
    sections: [],
    totalLength: 0,
    currentSection: null
  });

  // Advanced per-section drum controls
  const [sectionControls, setSectionControls] = useState({});
  
  // Audio player state
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [selectedSection, setSelectedSection] = useState(null);
  const [soloTracks, setSoloTracks] = useState(new Set());
  const [muteTracks, setMuteTracks] = useState(new Set());

  // Mock sophisticated audio analysis
  const performAdvancedAnalysis = async (file) => {
    setIsAnalyzing(true);
    setAnalysisProgress(0);

    const analysisSteps = [
      'Analyzing audio waveform and spectral content...',
      'Detecting tempo, key, and time signature...',
      'Identifying musical style and genre characteristics...',
      'Separating and analyzing individual instruments...',
      'Mapping song structure and arrangement sections...',
      'Analyzing harmonic progression and dynamics...',
      'Generating intelligent recommendations...'
    ];

    for (let i = 0; i < analysisSteps.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      setAnalysisProgress(((i + 1) / analysisSteps.length) * 100);
    }

    // Mock sophisticated analysis results
    const mockAnalysis = {
      tempo: 128,
      key: 'G Major',
      timeSignature: '4/4',
      style: {
        primary: 'Alternative Rock',
        secondary: 'Indie Pop',
        confidence: 0.87,
        characteristics: ['driving rhythm', 'melodic bass', 'layered guitars', 'dynamic vocals']
      },
      structure: {
        sections: [
          { name: 'Intro', start: 0, end: 8, bars: 8, intensity: 0.3 },
          { name: 'Verse 1', start: 8, end: 24, bars: 16, intensity: 0.6 },
          { name: 'Pre-Chorus', start: 24, end: 32, bars: 8, intensity: 0.75 },
          { name: 'Chorus', start: 32, end: 48, bars: 16, intensity: 0.9 },
          { name: 'Verse 2', start: 48, end: 64, bars: 16, intensity: 0.65 },
          { name: 'Pre-Chorus', start: 64, end: 72, bars: 8, intensity: 0.8 },
          { name: 'Chorus', start: 72, end: 88, bars: 16, intensity: 0.95 },
          { name: 'Bridge', start: 88, end: 104, bars: 16, intensity: 0.5 },
          { name: 'Final Chorus', start: 104, end: 120, bars: 16, intensity: 1.0 },
          { name: 'Outro', start: 120, end: 128, bars: 8, intensity: 0.4 }
        ],
        totalBars: 128,
        totalDuration: 240
      },
      instruments: {
        detected: [
          { name: 'Lead Vocals', confidence: 0.95, frequency_range: '80-4000Hz', prominence: 0.8 },
          { name: 'Electric Guitar (Lead)', confidence: 0.92, frequency_range: '200-8000Hz', prominence: 0.7 },
          { name: 'Electric Guitar (Rhythm)', confidence: 0.88, frequency_range: '80-4000Hz', prominence: 0.6 },
          { name: 'Bass Guitar', confidence: 0.94, frequency_range: '40-500Hz', prominence: 0.75 },
          { name: 'Synthesizer Pad', confidence: 0.76, frequency_range: '100-2000Hz', prominence: 0.4 },
          { name: 'Background Vocals', confidence: 0.82, frequency_range: '200-3000Hz', prominence: 0.3 }
        ],
        missing: ['Drums', 'Percussion'],
        recommendations: ['Full drum kit', 'Shaker/tambourine', 'Crash cymbals for emphasis']
      },
      dynamics: {
        overall_energy: 0.75,
        dynamic_range: 0.68,
        sections_energy: {
          'Intro': 0.3, 'Verse 1': 0.6, 'Pre-Chorus': 0.75, 'Chorus': 0.9,
          'Verse 2': 0.65, 'Bridge': 0.5, 'Final Chorus': 1.0, 'Outro': 0.4
        }
      },
      harmony: {
        key_stability: 0.89,
        chord_progression: ['G', 'Em', 'C', 'D'],
        modulations: [],
        harmonic_rhythm: 'moderate'
      }
    };

    setAudioAnalysis(mockAnalysis);
    setArrangement({
      sections: mockAnalysis.structure.sections,
      totalLength: mockAnalysis.structure.totalDuration,
      currentSection: 0
    });

    // Initialize per-section controls
    const initialControls = {};
    mockAnalysis.structure.sections.forEach((section, index) => {
      initialControls[index] = {
        humanness: 75,
        groove: 65,
        timing: 0,
        velocity: 85,
        kick: {
          pattern: 'auto',
          velocity: 90,
          timing: 0,
          emphasis: section.intensity * 100
        },
        snare: {
          pattern: 'auto',
          velocity: 95,
          timing: 0,
          ghosting: 25,
          rimshots: 10,
          crossStick: 0
        },
        hihat: {
          pattern: 'auto',
          velocity: 75,
          timing: 0,
          openness: 20,
          footWork: 15,
          chops: 5
        },
        ride: {
          enabled: section.name.includes('Verse'),
          velocity: 80,
          timing: 0,
          bell: 10,
          edge: 90
        },
        toms: {
          fills: true,
          frequency: 20,
          complexity: 'medium'
        },
        cymbals: {
          crashes: section.intensity > 0.7,
          frequency: Math.round(section.intensity * 30)
        }
      };
    });
    setSectionControls(initialControls);

    setIsAnalyzing(false);
    setCurrentPhase('analysis');
  };

  // Launch Reaper with stems
  const launchReaper = () => {
    setReaperLaunched(true);
    // In a real implementation, this would:
    // 1. Export stems to temp directory
    // 2. Create Reaper project file with stems on separate tracks
    // 3. Launch Reaper with the project
    console.log('Launching Reaper with stems and full audio...');
  };

  // Compact upload interface
  const renderUploadInterface = () => (
    <div className="space-y-6">
      <div className="text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-purple-500/20 to-blue-500/20 rounded-xl mb-4">
          <Upload className="h-8 w-8 text-purple-400" />
        </div>
        <h2 className="text-2xl font-bold text-white mb-2">Pro Studio</h2>
        <p className="text-gray-300 text-sm mb-6" style={{fontSize: '12px'}}>
          Professional analysis with Reaper DAW integration
        </p>
      </div>

      <div className="max-w-2xl mx-auto">
        <div 
          className="border-2 border-dashed border-purple-500/50 rounded-2xl p-12 text-center hover:border-purple-400/70 transition-colors cursor-pointer bg-white/5"
          onDrop={(e) => {
            e.preventDefault();
            const file = e.dataTransfer.files[0];
            if (file && file.type.startsWith('audio/')) {
              setUploadedFile(file);
              performAdvancedAnalysis(file);
            }
          }}
          onDragOver={(e) => e.preventDefault()}
          onClick={() => document.getElementById('audio-upload').click()}
        >
          <input
            id="audio-upload"
            type="file"
            accept="audio/*"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files[0];
              if (file) {
                setUploadedFile(file);
                performAdvancedAnalysis(file);
              }
            }}
          />
          
          <div className="space-y-4">
            <FileAudio className="h-16 w-16 text-purple-400 mx-auto" />
            <div>
              <p className="text-xl font-semibold text-white mb-2">
                Drop your audio file here
              </p>
              <p className="text-gray-400">
                Supports WAV, MP3, FLAC, and other audio formats
              </p>
            </div>
            <button className="px-8 py-4 bg-gradient-to-r from-purple-500 to-blue-500 text-white rounded-xl font-semibold hover:from-purple-600 hover:to-blue-600 transition-all">
              Choose Audio File
            </button>
          </div>
        </div>

        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white/5 rounded-xl p-6 text-center">
            <Brain className="h-8 w-8 text-purple-400 mx-auto mb-3" />
            <h3 className="font-semibold text-white mb-2">AI Analysis</h3>
            <p className="text-sm text-gray-400">Advanced tempo, key, and style detection</p>
          </div>
          <div className="bg-white/5 rounded-xl p-6 text-center">
            <Layers className="h-8 w-8 text-blue-400 mx-auto mb-3" />
            <h3 className="font-semibold text-white mb-2">Instrument Separation</h3>
            <p className="text-sm text-gray-400">Individual track identification and analysis</p>
          </div>
          <div className="bg-white/5 rounded-xl p-6 text-center">
            <Target className="h-8 w-8 text-green-400 mx-auto mb-3" />
            <h3 className="font-semibold text-white mb-2">Intelligent Recommendations</h3>
            <p className="text-sm text-gray-400">Optimized drum patterns for your music</p>
          </div>
        </div>
      </div>
    </div>
  );

  // Advanced analysis results interface
  const renderAnalysisInterface = () => (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold text-white">Analysis Results</h2>
        <button
          onClick={() => setCurrentPhase('options')}
          className="px-6 py-3 bg-gradient-to-r from-purple-500 to-blue-500 text-white rounded-xl font-semibold hover:from-purple-600 hover:to-blue-600 transition-all"
        >
          Create Drum Track →
        </button>
      </div>

      {/* Core Musical Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-purple-500/20 to-blue-500/20 rounded-xl p-6 border border-purple-500/30">
          <div className="flex items-center gap-3 mb-4">
            <Timer className="h-6 w-6 text-purple-400" />
            <h3 className="text-lg font-semibold text-white">Tempo</h3>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-white mb-2">{audioAnalysis.tempo}</div>
            <div className="text-purple-300">BPM</div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-blue-500/20 to-cyan-500/20 rounded-xl p-6 border border-blue-500/30">
          <div className="flex items-center gap-3 mb-4">
            <Music2 className="h-6 w-6 text-blue-400" />
            <h3 className="text-lg font-semibold text-white">Key</h3>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-white mb-2">{audioAnalysis.key}</div>
            <div className="text-blue-300">{audioAnalysis.timeSignature}</div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-500/20 to-emerald-500/20 rounded-xl p-6 border border-green-500/30">
          <div className="flex items-center gap-3 mb-4">
            <Star className="h-6 w-6 text-green-400" />
            <h3 className="text-lg font-semibold text-white">Style</h3>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-white mb-1">{audioAnalysis.style?.primary}</div>
            <div className="text-sm text-green-300 mb-2">{audioAnalysis.style?.secondary}</div>
            <div className="text-xs text-gray-400">{Math.round(audioAnalysis.style?.confidence * 100)}% confidence</div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-orange-500/20 to-red-500/20 rounded-xl p-6 border border-orange-500/30">
          <div className="flex items-center gap-3 mb-4">
            <Activity className="h-6 w-6 text-orange-400" />
            <h3 className="text-lg font-semibold text-white">Energy</h3>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-white mb-2">
              {Math.round(audioAnalysis.dynamics?.overall_energy * 100)}%
            </div>
            <div className="text-orange-300">Overall Energy</div>
          </div>
        </div>
      </div>

      {/* Instrument Analysis */}
      <div className="bg-white/5 rounded-xl p-8">
        <h3 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
          <Layers className="h-7 w-7 text-purple-400" />
          Detected Instruments
        </h3>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div>
            <h4 className="text-lg font-semibold text-white mb-4">Present Instruments</h4>
            <div className="space-y-3">
              {audioAnalysis.instruments?.detected.map((instrument, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                  <div className="flex-1">
                    <div className="font-medium text-white">{instrument.name}</div>
                    <div className="text-sm text-gray-400">{instrument.frequency_range}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium text-green-400">
                      {Math.round(instrument.confidence * 100)}%
                    </div>
                    <div className="w-20 bg-white/20 rounded-full h-2 mt-1">
                      <div 
                        className="bg-gradient-to-r from-green-400 to-blue-400 h-2 rounded-full"
                        style={{ width: `${instrument.prominence * 100}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h4 className="text-lg font-semibold text-white mb-4">Missing Elements</h4>
            <div className="space-y-3">
              {audioAnalysis.instruments?.missing.map((missing, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
                  <div className="font-medium text-red-300">{missing}</div>
                  <div className="text-sm text-red-400">Not Detected</div>
                </div>
              ))}
            </div>
            
            <div className="mt-6">
              <h5 className="font-medium text-white mb-3">AI Recommendations</h5>
              <div className="space-y-2">
                {audioAnalysis.instruments?.recommendations.map((rec, index) => (
                  <div key={index} className="flex items-center gap-2 text-sm text-purple-300">
                    <Sparkles className="h-4 w-4" />
                    {rec}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Song Structure Visualization */}
      <div className="bg-white/5 rounded-xl p-8">
        <h3 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
          <BarChart3 className="h-7 w-7 text-blue-400" />
          Song Structure Analysis
        </h3>
        
        <div className="space-y-6">
          {/* Timeline visualization */}
          <div className="relative">
            <div className="flex h-16 rounded-lg overflow-hidden">
              {audioAnalysis.structure?.sections.map((section, index) => (
                <div
                  key={index}
                  className="relative flex items-center justify-center text-white font-medium text-sm"
                  style={{
                    width: `${(section.bars / audioAnalysis.structure.totalBars) * 100}%`,
                    backgroundColor: `hsl(${index * 40}, 70%, ${30 + section.intensity * 30}%)`
                  }}
                >
                  <span>{section.name}</span>
                  <div className="absolute bottom-0 left-0 right-0 h-1 bg-white/30"></div>
                </div>
              ))}
            </div>
            <div className="flex justify-between text-xs text-gray-400 mt-2">
              <span>0:00</span>
              <span>{Math.floor(audioAnalysis.structure?.totalDuration / 60)}:{String(audioAnalysis.structure?.totalDuration % 60).padStart(2, '0')}</span>
            </div>
          </div>

          {/* Section details */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {audioAnalysis.structure?.sections.map((section, index) => (
              <div key={index} className="bg-white/5 rounded-lg p-4">
                <div className="font-medium text-white mb-2">{section.name}</div>
                <div className="space-y-1 text-sm text-gray-400">
                  <div>Bars: {section.bars}</div>
                  <div>Duration: {Math.round((section.end - section.start) * (60/audioAnalysis.tempo) * 4)}s</div>
                  <div className="flex items-center gap-2">
                    <span>Energy:</span>
                    <div className="flex-1 bg-white/20 rounded-full h-2">
                      <div 
                        className="bg-gradient-to-r from-purple-500 to-blue-500 h-2 rounded-full"
                        style={{ width: `${section.intensity * 100}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  // Creation options selection
  const renderOptionsInterface = () => (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-white mb-4">Choose Creation Method</h2>
        <p className="text-gray-300 text-lg">
          Select how you want the AI to generate your drum track
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Style-Matched Option */}
        <div 
          className={`p-8 rounded-2xl border-2 cursor-pointer transition-all ${
            creationMode === 'style_match' 
              ? 'border-purple-500 bg-purple-500/20' 
              : 'border-white/20 bg-white/5 hover:border-purple-400/50'
          }`}
          onClick={() => setCreationMode('style_match')}
        >
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-purple-500/20 rounded-2xl mb-6">
              <Star className="h-8 w-8 text-purple-400" />
            </div>
            <h3 className="text-xl font-bold text-white mb-4">Style-Matched Drums</h3>
            <p className="text-gray-300 mb-6">
              Generate drums that perfectly match the style, tempo, and energy of your track
            </p>
            <div className="space-y-2 text-sm text-gray-400">
              <div> Automatic style adaptation</div>
              <div> Energy-matched sections</div>
              <div> Genre-appropriate patterns</div>
              <div> Quick generation</div>
            </div>
          </div>
        </div>

        {/* Instrument-Following Option */}
        <div 
          className={`p-8 rounded-2xl border-2 cursor-pointer transition-all ${
            creationMode === 'instrument_follow' 
              ? 'border-blue-500 bg-blue-500/20' 
              : 'border-white/20 bg-white/5 hover:border-blue-400/50'
          }`}
          onClick={() => setCreationMode('instrument_follow')}
        >
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-500/20 rounded-2xl mb-6">
              <Target className="h-8 w-8 text-blue-400" />
            </div>
            <h3 className="text-xl font-bold text-white mb-4">Instrument-Following</h3>
            <p className="text-gray-300 mb-6">
              Create drums that follow and complement a specific instrument or vocal line
            </p>
            <div className="space-y-2 text-sm text-gray-400">
              <div> Rhythmic synchronization</div>
              <div> Melodic phrase matching</div>
              <div> Dynamic response</div>
              <div> Musical conversation</div>
            </div>
          </div>
          
          {creationMode === 'instrument_follow' && (
            <div className="mt-6 pt-6 border-t border-blue-500/30">
              <label className="block text-sm font-medium text-blue-300 mb-3">Follow Target:</label>
              <select 
                value={followTarget || ''}
                onChange={(e) => setFollowTarget(e.target.value)}
                className="w-full p-3 bg-white/10 border border-blue-500/30 rounded-lg text-white"
              >
                <option value="">Select instrument to follow</option>
                {audioAnalysis.instruments?.detected.map((instrument, index) => (
                  <option key={index} value={instrument.name}>{instrument.name}</option>
                ))}
              </select>
            </div>
          )}
        </div>

        {/* Bass-Influenced Option */}
        <div 
          className={`p-8 rounded-2xl border-2 cursor-pointer transition-all ${
            creationMode === 'bass_lock' 
              ? 'border-green-500 bg-green-500/20' 
              : 'border-white/20 bg-white/5 hover:border-green-400/50'
          }`}
          onClick={() => setCreationMode('bass_lock')}
        >
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-green-500/20 rounded-2xl mb-6">
              <Waves className="h-8 w-8 text-green-400" />
            </div>
            <h3 className="text-xl font-bold text-white mb-4">Bass-Locked Rhythm</h3>
            <p className="text-gray-300 mb-6">
              Create a tight rhythm section with drums locked to the bass line
            </p>
            <div className="space-y-2 text-sm text-gray-400">
              <div> Rhythmic locking</div>
              <div> Groove pocket creation</div>
              <div> Bass-kick synchronization</div>
              <div> Professional feel</div>
            </div>
          </div>
        </div>
      </div>

      {creationMode && (
        <div className="text-center">
          <button
            onClick={() => setCurrentPhase('arrangement')}
            className="px-12 py-4 bg-gradient-to-r from-purple-500 to-blue-500 text-white rounded-xl font-bold text-xl hover:from-purple-600 hover:to-blue-600 transition-all flex items-center gap-4 mx-auto"
          >
            <Brain className="h-8 w-8" />
            Open DAW Arrangement Editor
            <ArrowRight className="h-8 w-8" />
          </button>
          <p className="text-gray-400 mt-4">
            Advanced per-section controls with professional DAW interface
          </p>
        </div>
      )}
    </div>
  );

  // DAW-style arrangement editor (simplified for space)
  const renderArrangementInterface = () => (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2">DAW Arrangement Editor</h2>
          <p className="text-gray-300">Professional per-section drum programming</p>
        </div>
        <div className="flex gap-4">
          <button
            onClick={() => setCurrentPhase('options')}
            className="px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors"
          >
            ← Back to Options
          </button>
          <button
            onClick={() => setCurrentPhase('generation')}
            className="px-6 py-3 bg-gradient-to-r from-purple-500 to-blue-500 text-white rounded-xl font-semibold hover:from-purple-600 hover:to-blue-600 transition-all"
          >
            Generate Track
          </button>
        </div>
      </div>

      {/* Timeline Overview */}
      <div className="bg-white/5 rounded-xl p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold text-white flex items-center gap-3">
            <BarChart3 className="h-6 w-6 text-purple-400" />
            Song Timeline
          </h3>
          <div className="flex items-center gap-4">
            <div className="text-sm text-gray-400">
              Duration: {Math.floor(arrangement.totalLength / 60)}:{String(arrangement.totalLength % 60).padStart(2, '0')}
            </div>
            <div className="text-sm text-gray-400">
              Tempo: {audioAnalysis.tempo} BPM
            </div>
          </div>
        </div>

        {/* Interactive Timeline */}
        <div className="relative mb-6">
          <div className="flex h-20 rounded-lg overflow-hidden border border-white/20">
            {arrangement.sections.map((section, index) => (
              <div
                key={index}
                className={`relative flex flex-col justify-center px-2 cursor-pointer transition-all ${
                  selectedSection === index 
                    ? 'bg-purple-500/40 border-2 border-purple-400' 
                    : 'bg-gradient-to-br from-white/10 to-white/5 hover:from-white/20 hover:to-white/10'
                }`}
                style={{
                  width: `${(section.bars / audioAnalysis.structure.totalBars) * 100}%`,
                }}
                onClick={() => setSelectedSection(index)}
              >
                <div className="text-white font-medium text-sm text-center">{section.name}</div>
                <div className="text-gray-300 text-xs text-center">{section.bars} bars</div>
                <div 
                  className="absolute bottom-0 left-0 right-0 h-1 rounded-full"
                  style={{
                    background: `linear-gradient(90deg, hsl(${index * 40}, 70%, 50%) 0%, hsl(${index * 40}, 70%, 60%) 100%)`
                  }}
                ></div>
              </div>
            ))}
          </div>
          <div className="flex justify-between text-xs text-gray-400 mt-2">
            <span>0:00</span>
            <span>{Math.floor(arrangement.totalLength / 60)}:{String(arrangement.totalLength % 60).padStart(2, '0')}</span>
          </div>
        </div>

        {/* Quick Section Navigation */}
        <div className="flex gap-2 flex-wrap">
          {arrangement.sections.map((section, index) => (
            <button
              key={index}
              onClick={() => setSelectedSection(index)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                selectedSection === index
                  ? 'bg-purple-500 text-white'
                  : 'bg-white/10 text-gray-300 hover:bg-white/20'
              }`}
            >
              {section.name}
            </button>
          ))}
        </div>
      </div>

      {/* Section-Specific Controls */}
      {selectedSection !== null && sectionControls[selectedSection] && (
        <div className="bg-white/5 rounded-xl p-8">
          <div className="flex items-center justify-between mb-8">
            <h3 className="text-2xl font-bold text-white flex items-center gap-3">
              <Sliders className="h-7 w-7 text-blue-400" />
              {arrangement.sections[selectedSection].name} Controls
            </h3>
            <div className="flex items-center gap-4">
              <div className="text-sm text-gray-400">
                Bars: {arrangement.sections[selectedSection].bars}
              </div>
              <div className="text-sm text-gray-400">
                Intensity: {Math.round(arrangement.sections[selectedSection].intensity * 100)}%
              </div>
            </div>
          </div>

          {/* Global Section Controls */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-gradient-to-br from-purple-500/20 to-blue-500/20 rounded-xl p-6 border border-purple-500/30">
              <h4 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Activity className="h-5 w-5 text-purple-400" />
                Humanness
              </h4>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-gray-300 mb-2">
                    Human Feel: {sectionControls[selectedSection].humanness}%
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={sectionControls[selectedSection].humanness}
                    onChange={(e) => setSectionControls(prev => ({
                      ...prev,
                      [selectedSection]: { ...prev[selectedSection], humanness: parseInt(e.target.value) }
                    }))}
                    className="w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-300 mb-2">
                    Groove: {sectionControls[selectedSection].groove}%
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={sectionControls[selectedSection].groove}
                    onChange={(e) => setSectionControls(prev => ({
                      ...prev,
                      [selectedSection]: { ...prev[selectedSection], groove: parseInt(e.target.value) }
                    }))}
                    className="w-full"
                  />
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-green-500/20 to-emerald-500/20 rounded-xl p-6 border border-green-500/30">
              <h4 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Timer className="h-5 w-5 text-green-400" />
                Timing
              </h4>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-gray-300 mb-2">
                    Push/Lay Back: {sectionControls[selectedSection].timing > 0 ? '+' : ''}{sectionControls[selectedSection].timing}ms
                  </label>
                  <input
                    type="range"
                    min="-50"
                    max="50"
                    value={sectionControls[selectedSection].timing}
                    onChange={(e) => setSectionControls(prev => ({
                      ...prev,
                      [selectedSection]: { ...prev[selectedSection], timing: parseInt(e.target.value) }
                    }))}
                    className="w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-300 mb-2">
                    Overall Velocity: {sectionControls[selectedSection].velocity}%
                  </label>
                  <input
                    type="range"
                    min="40"
                    max="127"
                    value={sectionControls[selectedSection].velocity}
                    onChange={(e) => setSectionControls(prev => ({
                      ...prev,
                      [selectedSection]: { ...prev[selectedSection], velocity: parseInt(e.target.value) }
                    }))}
                    className="w-full"
                  />
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-orange-500/20 to-red-500/20 rounded-xl p-6 border border-orange-500/30">
              <h4 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Gauge className="h-5 w-5 text-orange-400" />
                Dynamics
              </h4>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-gray-300 mb-2">Creation Mode</label>
                  <div className="text-sm text-orange-300 capitalize">{creationMode?.replace('_', ' ')}</div>
                </div>
                {creationMode === 'instrument_follow' && followTarget && (
                  <div>
                    <label className="block text-sm text-gray-300 mb-2">Following</label>
                    <div className="text-sm text-orange-300">{followTarget}</div>
                  </div>
                )}
                <div>
                  <label className="block text-sm text-gray-300 mb-2">Section Intensity</label>
                  <div className="w-full bg-white/20 rounded-full h-3">
                    <div 
                      className="bg-gradient-to-r from-orange-500 to-red-500 h-3 rounded-full"
                      style={{ width: `${arrangement.sections[selectedSection].intensity * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-cyan-500/20 to-blue-500/20 rounded-xl p-6 border border-cyan-500/30">
              <h4 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Focus className="h-5 w-5 text-cyan-400" />
                Focus
              </h4>
              <div className="space-y-4">
                <button
                  onClick={() => {
                    const currentSettings = sectionControls[selectedSection];
                    const newControls = {};
                    arrangement.sections.forEach((_, index) => {
                      newControls[index] = { ...currentSettings };
                    });
                    setSectionControls(newControls);
                  }}
                  className="w-full px-4 py-2 bg-cyan-500/20 border border-cyan-500/50 text-cyan-300 rounded-lg hover:bg-cyan-500/30 transition-colors text-sm"
                >
                  Apply to All Sections
                </button>
                <button
                  onClick={() => {
                    setSectionControls(prev => ({
                      ...prev,
                      [selectedSection]: {
                        humanness: 75, groove: 65, timing: 0, velocity: 85,
                        kick: { pattern: 'auto', velocity: 90, timing: 0, emphasis: 75 },
                        snare: { pattern: 'auto', velocity: 95, timing: 0, ghosting: 25, rimshots: 10, crossStick: 0 },
                        hihat: { pattern: 'auto', velocity: 75, timing: 0, openness: 20, footWork: 15, chops: 5 },
                        ride: { enabled: false, velocity: 80, timing: 0, bell: 10, edge: 90 },
                        toms: { fills: true, frequency: 20, complexity: 'medium' },
                        cymbals: { crashes: true, frequency: 15 }
                      }
                    }));
                  }}
                  className="w-full px-4 py-2 bg-white/10 border border-white/20 text-gray-300 rounded-lg hover:bg-white/20 transition-colors text-sm"
                >
                  Reset Section
                </button>
              </div>
            </div>
          </div>

          {/* Individual Drum Controls */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            
            {/* Kick Drum */}
            <div className="bg-white/5 rounded-xl p-6">
              <h4 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Circle className="h-5 w-5 text-red-500" />
                Kick Drum
              </h4>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-gray-300 mb-2">
                    Velocity: {sectionControls[selectedSection].kick.velocity}
                  </label>
                  <input
                    type="range"
                    min="60"
                    max="127"
                    value={sectionControls[selectedSection].kick.velocity}
                    onChange={(e) => setSectionControls(prev => ({
                      ...prev,
                      [selectedSection]: { 
                        ...prev[selectedSection], 
                        kick: { ...prev[selectedSection].kick, velocity: parseInt(e.target.value) }
                      }
                    }))}
                    className="w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-300 mb-2">
                    Emphasis: {sectionControls[selectedSection].kick.emphasis}%
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={sectionControls[selectedSection].kick.emphasis}
                    onChange={(e) => setSectionControls(prev => ({
                      ...prev,
                      [selectedSection]: { 
                        ...prev[selectedSection], 
                        kick: { ...prev[selectedSection].kick, emphasis: parseInt(e.target.value) }
                      }
                    }))}
                    className="w-full"
                  />
                </div>
              </div>
            </div>

            {/* Snare Drum */}
            <div className="bg-white/5 rounded-xl p-6">
              <h4 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Hexagon className="h-5 w-5 text-yellow-500" />
                Snare Drum
              </h4>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-gray-300 mb-2">
                    Ghost Notes: {sectionControls[selectedSection].snare.ghosting}%
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="80"
                    value={sectionControls[selectedSection].snare.ghosting}
                    onChange={(e) => setSectionControls(prev => ({
                      ...prev,
                      [selectedSection]: { 
                        ...prev[selectedSection], 
                        snare: { ...prev[selectedSection].snare, ghosting: parseInt(e.target.value) }
                      }
                    }))}
                    className="w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-300 mb-2">
                    Rimshots: {sectionControls[selectedSection].snare.rimshots}%
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="50"
                    value={sectionControls[selectedSection].snare.rimshots}
                    onChange={(e) => setSectionControls(prev => ({
                      ...prev,
                      [selectedSection]: { 
                        ...prev[selectedSection], 
                        snare: { ...prev[selectedSection].snare, rimshots: parseInt(e.target.value) }
                      }
                    }))}
                    className="w-full"
                  />
                </div>
              </div>
            </div>

            {/* Hi-Hat */}
            <div className="bg-white/5 rounded-xl p-6">
              <h4 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Triangle className="h-5 w-5 text-cyan-500" />
                Hi-Hat
              </h4>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-gray-300 mb-2">
                    Openness: {sectionControls[selectedSection].hihat.openness}%
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="60"
                    value={sectionControls[selectedSection].hihat.openness}
                    onChange={(e) => setSectionControls(prev => ({
                      ...prev,
                      [selectedSection]: { 
                        ...prev[selectedSection], 
                        hihat: { ...prev[selectedSection].hihat, openness: parseInt(e.target.value) }
                      }
                    }))}
                    className="w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-300 mb-2">
                    Chops: {sectionControls[selectedSection].hihat.chops}%
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="50"
                    value={sectionControls[selectedSection].hihat.chops}
                    onChange={(e) => setSectionControls(prev => ({
                      ...prev,
                      [selectedSection]: { 
                        ...prev[selectedSection], 
                        hihat: { ...prev[selectedSection].hihat, chops: parseInt(e.target.value) }
                      }
                    }))}
                    className="w-full"
                  />
                </div>
              </div>
            </div>

            {/* Professional Audio Player */}
            <div className="bg-white/5 rounded-xl p-6">
              <h4 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Headphones className="h-5 w-5 text-purple-400" />
                Audio Player
              </h4>
              <div className="space-y-4">
                <div className="flex items-center gap-4">
                  <button 
                    className="p-3 bg-green-500 hover:bg-green-600 rounded-full transition-all"
                    onClick={() => setIsPlaying(!isPlaying)}
                  >
                    {isPlaying ? <Pause className="h-5 w-5 text-white" /> : <Play className="h-5 w-5 text-white" />}
                  </button>
                  
                  <div className="flex-1 bg-white/20 rounded-full h-2 cursor-pointer">
                    <div className="bg-gradient-to-r from-purple-500 to-blue-500 h-2 rounded-full w-1/3"></div>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-2">
                  {['Original', 'Drums', 'Mix'].map((track) => (
                    <button
                      key={track}
                      className={`px-3 py-2 text-xs rounded ${
                        soloTracks.has(track) 
                          ? 'bg-yellow-500 text-black' 
                          : 'bg-white/20 text-white hover:bg-white/30'
                      }`}
                      onClick={() => {
                        const newSolo = new Set(soloTracks);
                        if (newSolo.has(track)) {
                          newSolo.delete(track);
                        } else {
                          newSolo.add(track);
                        }
                        setSoloTracks(newSolo);
                      }}
                    >
                      {track}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  // Generation interface
  const renderGenerationInterface = () => (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-white mb-4">Generate Professional Drum Track</h2>
        <p className="text-gray-300 text-lg">
          Ready to create your sophisticated drum arrangement
        </p>
      </div>

      <div className="text-center">
        <button
          onClick={() => setCurrentPhase('results')}
          className="px-16 py-6 bg-gradient-to-r from-purple-500 to-blue-500 text-white rounded-2xl font-bold text-2xl hover:from-purple-600 hover:to-blue-600 transition-all flex items-center gap-6 mx-auto"
        >
          <Brain className="h-10 w-10" />
          Generate Advanced Drum Track
          <Zap className="h-10 w-10" />
        </button>
      </div>
    </div>
  );

  // Results interface
  const renderResultsInterface = () => (
    <div className="space-y-8">
      <div className="text-center">
        <div className="inline-flex items-center justify-center w-20 h-20 bg-green-500/20 rounded-2xl mb-6">
          <CheckCircle className="h-12 w-12 text-green-400" />
        </div>
        <h2 className="text-3xl font-bold text-white mb-4">Professional Track Generated</h2>
        <p className="text-gray-300 text-lg">
          Your sophisticated drum arrangement is ready
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <button className="p-6 bg-green-500/20 border border-green-500/50 rounded-xl hover:bg-green-500/30 transition-all">
          <Download className="h-8 w-8 text-green-400 mx-auto mb-3" />
          <div className="text-white font-semibold mb-1">Master Track</div>
          <div className="text-sm text-gray-400">Full mixed drum track</div>
        </button>
        
        <button className="p-6 bg-blue-500/20 border border-blue-500/50 rounded-xl hover:bg-blue-500/30 transition-all">
          <Layers className="h-8 w-8 text-blue-400 mx-auto mb-3" />
          <div className="text-white font-semibold mb-1">Stems</div>
          <div className="text-sm text-gray-400">Individual drum elements</div>
        </button>
        
        <button className="p-6 bg-purple-500/20 border border-purple-500/50 rounded-xl hover:bg-purple-500/30 transition-all">
          <Share className="h-8 w-8 text-purple-400 mx-auto mb-3" />
          <div className="text-white font-semibold mb-1">Share</div>
          <div className="text-sm text-gray-400">Send to collaborators</div>
        </button>
        
        <button className="p-6 bg-orange-500/20 border border-orange-500/50 rounded-xl hover:bg-orange-500/30 transition-all">
          <Settings className="h-8 w-8 text-orange-400 mx-auto mb-3" />
          <div className="text-white font-semibold mb-1">Project</div>
          <div className="text-sm text-gray-400">Save as project file</div>
        </button>
      </div>
    </div>
  );

  // Main render function
  const renderCurrentPhase = () => {
    if (isAnalyzing) {
      return (
        <div className="text-center py-20">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-purple-500/20 rounded-2xl mb-8">
            <Brain className="h-12 w-12 text-purple-400 animate-pulse" />
          </div>
          <h2 className="text-2xl font-bold text-white mb-4">Analyzing Your Audio</h2>
          <p className="text-gray-300 mb-8">Advanced AI processing in progress...</p>
          
          <div className="max-w-md mx-auto">
            <div className="w-full bg-white/20 rounded-full h-3 mb-4">
              <div 
                className="bg-gradient-to-r from-purple-500 to-blue-500 h-3 rounded-full transition-all duration-300"
                style={{ width: `${analysisProgress}%` }}
              ></div>
            </div>
            <p className="text-sm text-gray-400">{analysisProgress.toFixed(0)}% Complete</p>
          </div>
        </div>
      );
    }

    switch (currentPhase) {
      case 'upload':
        return renderUploadInterface();
      case 'analysis':
        return renderAnalysisInterface();
      case 'options':
        return renderOptionsInterface();
      case 'arrangement':
        return renderArrangementInterface();
      case 'generation':
        return renderGenerationInterface();
      case 'results':
        return renderResultsInterface();
      default:
        return renderUploadInterface();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-blue-900 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-purple-500/30 to-blue-500/30 rounded-2xl mb-6">
            <Crown className="h-8 w-8 text-purple-400" />
          </div>
          <h1 className="text-5xl font-bold text-white mb-4">Advanced Pro Studio</h1>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Sophisticated audio analysis, DAW-style arrangement editing, and professional drum generation
          </p>
        </div>

        {/* Progress Indicator */}
        <div className="flex justify-center mb-12">
          <div className="flex items-center gap-4">
            {[
              { phase: 'upload', label: 'Upload', icon: Upload },
              { phase: 'analysis', label: 'Analysis', icon: Brain },
              { phase: 'options', label: 'Options', icon: Target },
              { phase: 'arrangement', label: 'Arrangement', icon: Sliders },
              { phase: 'generation', label: 'Generation', icon: Zap },
              { phase: 'results', label: 'Results', icon: CheckCircle }
            ].map((item, index) => {
              const phaseOrder = ['upload', 'analysis', 'options', 'arrangement', 'generation', 'results'];
              const currentIndex = phaseOrder.indexOf(currentPhase);
              const isActive = currentPhase === item.phase;
              const isCompleted = currentIndex > index;
              
              return (
                <React.Fragment key={item.phase}>
                  <div className={`flex flex-col items-center ${
                    isActive ? 'text-purple-400' : 
                    isCompleted ? 'text-green-400' : 'text-gray-500'
                  }`}>
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center mb-2 ${
                      isActive ? 'bg-purple-500/30 border-2 border-purple-400' :
                      isCompleted ? 'bg-green-500/30 border-2 border-green-400' : 'bg-white/10'
                    }`}>
                      <item.icon className="h-5 w-5" />
                    </div>
                    <span className="text-xs font-medium">{item.label}</span>
                  </div>
                  {index < 5 && (
                    <div className={`w-8 h-0.5 mt-5 ${
                      isCompleted ? 'bg-green-400' : 'bg-white/20'
                    }`} />
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </div>

        {/* Main Content */}
        {renderCurrentPhase()}
      </div>
    </div>
  );
};

export default ProStudioAdvanced;