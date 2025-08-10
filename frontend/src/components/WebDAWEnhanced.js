import React, { useState, useEffect, useRef } from 'react';
import { 
  Play, Pause, Square, SkipBack, SkipForward, Volume2, Settings,
  Copy, Clipboard, ZoomIn, ZoomOut, ChevronUp, ChevronDown,
  Plus, Minus, RefreshCw
} from 'lucide-react';

const SmartArrangementEditor = ({ arrangement, setArrangement, selectedSection, setSelectedSection }) => {
  const addSection = (sectionType) => {
    const newSection = {
      id: Date.now(),
      type: sectionType,
      name: `${sectionType} ${arrangement.filter(s => s.type === sectionType).length + 1}`,
      duration: 16,
      drumSettings: {
        complexity: 7,
        humanization: 75,
        ghostNotes: 40,
        flams: 15,
        rimshots: 20,
        footSplash: 25,
        chokeFrequency: 10,
        snareType: 'Center',
        hihatState: 'Closed',
        timingDrift: 25,
        swingAmount: 0,
        pushPull: 'On Beat',
        bellAccents: 15,
        crashIntegration: 25,
        rideStyle: 'Tip'
      }
    };
    
    setArrangement([...arrangement, newSection]);
  };

  const removeSection = (index) => {
    const newArrangement = arrangement.filter((_, i) => i !== index);
    setArrangement(newArrangement);
    if (selectedSection === index) {
      setSelectedSection(null);
    }
  };

  return (
    <div className="bg-gradient-to-r from-blue-900 to-purple-900 rounded-lg p-4">
      <h4 className="text-sm font-medium text-blue-300 mb-3">🎼 Smart Arrangement Editor</h4>
      
      <div className="grid grid-cols-2 gap-2 mb-4">
        {['Intro', 'Verse', 'Chorus', 'Bridge'].map((type) => (
          <button 
            key={type}
            onClick={() => addSection(type)}
            className="bg-blue-600 hover:bg-blue-700 px-2 py-1 rounded text-xs flex items-center justify-center transition-colors"
          >
            <Plus className="w-3 h-3 mr-1" />
            {type}
          </button>
        ))}
      </div>
      
      <div className="space-y-2">
        <div className="text-xs text-gray-300 mb-2">Current Arrangement:</div>
        {arrangement.map((section, index) => (
          <div 
            key={section.id}
            className={`flex items-center justify-between p-2 rounded text-xs cursor-pointer transition-colors ${
              selectedSection === index ? 'bg-purple-600' : 'bg-gray-700 hover:bg-gray-600'
            }`}
            onClick={() => setSelectedSection(index)}
          >
            <div className="flex items-center space-x-2">
              <span className="font-medium">{index + 1}. {section.name}</span>
              <span className="text-gray-400">({section.duration} bars)</span>
            </div>
            <div className="flex items-center space-x-1">
              <button 
                onClick={(e) => { 
                  e.stopPropagation(); 
                  removeSection(index); 
                }}
                className="p-1 hover:bg-red-600 rounded transition-colors"
                title="Remove section"
              >
                <Minus className="w-3 h-3" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const AdvancedDrumControls = ({ sectionSettings, updateSectionDrums, selectedSection }) => {
  if (selectedSection === null || !sectionSettings) {
    return (
      <div className="bg-gray-800 rounded-lg p-4 text-center">
        <div className="text-gray-400 text-sm">Select a section above to edit advanced drum settings</div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg p-4">
      <h4 className="text-sm font-medium text-orange-300 mb-3">
        🥁 Advanced Drums - Section {selectedSection + 1}
      </h4>
      
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-3">
          <h5 className="text-xs font-medium text-yellow-300">Snare Articulations</h5>
          
          <div>
            <label className="text-xs text-gray-400 block mb-1">
              Ghost Notes: <span className="text-orange-300">{sectionSettings.ghostNotes}%</span>
            </label>
            <input 
              type="range" 
              min="0" 
              max="100" 
              value={sectionSettings.ghostNotes}
              onChange={(e) => updateSectionDrums('ghostNotes', parseInt(e.target.value))}
              className="w-full h-1 bg-gray-600 rounded appearance-none cursor-pointer" 
            />
          </div>
          
          <div>
            <label className="text-xs text-gray-400 block mb-1">
              Flams: <span className="text-orange-300">{sectionSettings.flams}%</span>
            </label>
            <input 
              type="range" 
              min="0" 
              max="100" 
              value={sectionSettings.flams}
              onChange={(e) => updateSectionDrums('flams', parseInt(e.target.value))}
              className="w-full h-1 bg-gray-600 rounded appearance-none cursor-pointer" 
            />
          </div>
          
          <div>
            <label className="text-xs text-gray-400 block mb-1">
              Rimshots: <span className="text-orange-300">{sectionSettings.rimshots}%</span>
            </label>
            <input 
              type="range" 
              min="0" 
              max="100" 
              value={sectionSettings.rimshots}
              onChange={(e) => updateSectionDrums('rimshots', parseInt(e.target.value))}
              className="w-full h-1 bg-gray-600 rounded appearance-none cursor-pointer" 
            />
          </div>
          
          <div className="grid grid-cols-3 gap-1">
            {['Center', 'Edge', 'Rim'].map((type) => (
              <button 
                key={type}
                onClick={() => updateSectionDrums('snareType', type)}
                className={`px-2 py-1 rounded text-xs transition-all ${
                  sectionSettings.snareType === type 
                    ? 'bg-orange-600 shadow-lg' 
                    : 'bg-gray-700 hover:bg-orange-600'
                }`}
              >
                {type}
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-3">
          <h5 className="text-xs font-medium text-cyan-300">Hi-Hat Articulation</h5>
          
          <div>
            <label className="text-xs text-gray-400 block mb-1">
              Foot Splash: <span className="text-cyan-300">{sectionSettings.footSplash}%</span>
            </label>
            <input 
              type="range" 
              min="0" 
              max="100" 
              value={sectionSettings.footSplash}
              onChange={(e) => updateSectionDrums('footSplash', parseInt(e.target.value))}
              className="w-full h-1 bg-gray-600 rounded appearance-none cursor-pointer" 
            />
          </div>
          
          <div>
            <label className="text-xs text-gray-400 block mb-1">
              Choke Frequency: <span className="text-cyan-300">{sectionSettings.chokeFrequency}%</span>
            </label>
            <input 
              type="range" 
              min="0" 
              max="100" 
              value={sectionSettings.chokeFrequency}
              onChange={(e) => updateSectionDrums('chokeFrequency', parseInt(e.target.value))}
              className="w-full h-1 bg-gray-600 rounded appearance-none cursor-pointer" 
            />
          </div>
          
          <div className="grid grid-cols-3 gap-1">
            {['Closed', 'Semi', 'Open'].map((state) => (
              <button 
                key={state}
                onClick={() => updateSectionDrums('hihatState', state)}
                className={`px-2 py-1 rounded text-xs transition-all ${
                  sectionSettings.hihatState === state 
                    ? 'bg-cyan-600 shadow-lg' 
                    : 'bg-gray-700 hover:bg-cyan-600'
                }`}
              >
                {state}
              </button>
            ))}
          </div>
        </div>
      </div>
      
      <div className="mt-4 pt-4 border-t border-gray-700">
        <h5 className="text-xs font-medium text-green-300 mb-3">Timing & Feel</h5>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="text-xs text-gray-400 block mb-1">
              Timing Drift: <span className="text-green-300">{sectionSettings.timingDrift}%</span>
            </label>
            <input 
              type="range" 
              min="0" 
              max="100" 
              value={sectionSettings.timingDrift}
              onChange={(e) => updateSectionDrums('timingDrift', parseInt(e.target.value))}
              className="w-full h-1 bg-gray-600 rounded appearance-none cursor-pointer" 
            />
          </div>
          
          <div>
            <label className="text-xs text-gray-400 block mb-1">
              Swing Amount: <span className="text-green-300">{sectionSettings.swingAmount}%</span>
            </label>
            <input 
              type="range" 
              min="0" 
              max="100" 
              value={sectionSettings.swingAmount}
              onChange={(e) => updateSectionDrums('swingAmount', parseInt(e.target.value))}
              className="w-full h-1 bg-gray-600 rounded appearance-none cursor-pointer" 
            />
          </div>
          
          <div>
            <label className="text-xs text-gray-400 block mb-1">Push/Pull</label>
            <select 
              value={sectionSettings.pushPull}
              onChange={(e) => updateSectionDrums('pushPull', e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded px-2 py-1 text-xs text-white"
            >
              <option value="Laid Back">Laid Back</option>
              <option value="On Beat">On Beat</option>
              <option value="Pushing">Pushing</option>
              <option value="J-Dilla">J-Dilla Feel</option>
              <option value="D'Angelo">D'Angelo Feel</option>
            </select>
          </div>
        </div>
      </div>
      
      <div className="mt-4 pt-4 border-t border-gray-700">
        <h5 className="text-xs font-medium text-yellow-300 mb-3">Cymbal Dynamics</h5>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="text-xs text-gray-400 block mb-1">
              Bell Accents: <span className="text-yellow-300">{sectionSettings.bellAccents}%</span>
            </label>
            <input 
              type="range" 
              min="0" 
              max="100" 
              value={sectionSettings.bellAccents}
              onChange={(e) => updateSectionDrums('bellAccents', parseInt(e.target.value))}
              className="w-full h-1 bg-gray-600 rounded appearance-none cursor-pointer" 
            />
          </div>
          
          <div>
            <label className="text-xs text-gray-400 block mb-1">
              Crash Integration: <span className="text-yellow-300">{sectionSettings.crashIntegration}%</span>
            </label>
            <input 
              type="range" 
              min="0" 
              max="100" 
              value={sectionSettings.crashIntegration}
              onChange={(e) => updateSectionDrums('crashIntegration', parseInt(e.target.value))}
              className="w-full h-1 bg-gray-600 rounded appearance-none cursor-pointer" 
            />
          </div>
          
          <div>
            <label className="text-xs text-gray-400 block mb-1">Ride Style</label>
            <select 
              value={sectionSettings.rideStyle}
              onChange={(e) => updateSectionDrums('rideStyle', e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded px-2 py-1 text-xs text-white"
            >
              <option value="Tip">Tip</option>
              <option value="Shoulder">Shoulder</option>
              <option value="Bell">Bell</option>
              <option value="Mixed">Mixed</option>
            </select>
          </div>
        </div>
      </div>
      
      <div className="mt-4 pt-4 border-t border-gray-700 flex space-x-2">
        <button className="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-xs flex items-center transition-colors">
          <Copy className="w-3 h-3 mr-1" />
          Copy Settings
        </button>
        <button className="bg-green-600 hover:bg-green-700 px-3 py-1 rounded text-xs flex items-center transition-colors">
          <Clipboard className="w-3 h-3 mr-1" />
          Paste Settings
        </button>
        <button className="bg-purple-600 hover:bg-purple-700 px-3 py-1 rounded text-xs flex items-center transition-colors">
          <RefreshCw className="w-3 h-3 mr-1" />
          Reset
        </button>
      </div>
    </div>
  );
};

const EnhancedDrumStudio = ({ 
  showDrumStudio, isGenerating, generationProgress, handleGenerateDrums,
  drumStyle, setDrumStyle, complexity, setComplexity, tempo, setTempo,
  arrangement, setArrangement, selectedSection, setSelectedSection
}) => {
  if (!showDrumStudio) return null;

  const updateSectionDrums = (property, value) => {
    if (selectedSection === null) return;
    
    const newArrangement = [...arrangement];
    newArrangement[selectedSection] = {
      ...newArrangement[selectedSection],
      drumSettings: {
        ...newArrangement[selectedSection].drumSettings,
        [property]: value
      }
    };
    setArrangement(newArrangement);
  };

  const currentSectionSettings = selectedSection !== null ? arrangement[selectedSection]?.drumSettings : null;

  return (
    <div className="h-96 bg-gradient-to-r from-purple-900 to-gray-900 border-t border-purple-600 flex overflow-hidden">
      <div className="flex-1 overflow-y-auto p-4">
        <div className="grid grid-cols-4 gap-4 h-full">
          <SmartArrangementEditor 
            arrangement={arrangement}
            setArrangement={setArrangement}
            selectedSection={selectedSection}
            setSelectedSection={setSelectedSection}
          />
          
          <div className="bg-gray-800 rounded-lg p-4">
            <h4 className="text-sm font-medium text-blue-300 mb-3">🎼 Global Settings</h4>
            
            {isGenerating ? (
              <div className="mb-3">
                <div className="w-full bg-gray-700 rounded-full h-2 mb-2">
                  <div 
                    className="bg-gradient-to-r from-purple-600 to-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${generationProgress}%` }}
                  />
                </div>
                <div className="text-xs text-center text-purple-300">Generating... {generationProgress}%</div>
              </div>
            ) : (
              <button 
                onClick={handleGenerateDrums}
                className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 px-4 py-3 rounded-lg font-medium text-white transition-all duration-200 mb-3 text-sm"
              >
                🥁 Generate All Sections
              </button>
            )}
            
            <div className="space-y-3">
              <div>
                <label className="text-xs text-gray-400 block mb-1">Style</label>
                <select 
                  value={drumStyle}
                  onChange={(e) => setDrumStyle(e.target.value)}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-2 py-1 text-xs text-white"
                >
                  <option>Rock</option>
                  <option>Pop</option>
                  <option>Jazz</option>
                  <option>Funk</option>
                  <option>Metal</option>
                  <option>R&B</option>
                  <option>Country</option>
                </select>
              </div>
              
              <div>
                <label className="text-xs text-gray-400 block mb-1">Base Complexity: {complexity}</label>
                <input 
                  type="range" 
                  min="1" 
                  max="10" 
                  value={complexity}
                  onChange={(e) => setComplexity(parseInt(e.target.value))}
                  className="w-full h-2 bg-gray-600 rounded appearance-none cursor-pointer" 
                />
              </div>
              
              <div>
                <label className="text-xs text-gray-400 block mb-1">Tempo: {tempo} BPM</label>
                <input 
                  type="range" 
                  min="60" 
                  max="200" 
                  value={tempo} 
                  onChange={(e) => setTempo(parseInt(e.target.value))} 
                  className="w-full h-2 bg-gray-600 rounded appearance-none cursor-pointer" 
                />
              </div>
            </div>
          </div>
          
          <div className="col-span-2">
            <AdvancedDrumControls 
              sectionSettings={currentSectionSettings}
              updateSectionDrums={updateSectionDrums}
              selectedSection={selectedSection}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

const DAWHeader = ({ onBack, tempo, timeSignature, isGenerating, showDrumStudio, setShowDrumStudio }) => (
  <div className="bg-gray-800 border-b border-gray-700 p-3">
    <div className="flex items-center justify-between">
      <div className="flex items-center space-x-4">
        <button 
          onClick={onBack} 
          className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm transition-colors"
        >
          ← Back
        </button>
        <h2 className="text-xl font-bold">🎵 DrumTracKAI Enhanced WebDAW</h2>
        <div className="text-sm bg-gray-700 px-3 py-1 rounded flex items-center space-x-2">
          <span>{tempo} BPM</span>
          <span>•</span>
          <span>{timeSignature}</span>
          {isGenerating && (
            <React.Fragment>
              <span>•</span>
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse" />
                <span className="text-purple-400">Generating...</span>
              </div>
            </React.Fragment>
          )}
        </div>
      </div>
      
      <button
        onClick={() => setShowDrumStudio(!showDrumStudio)}
        className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all ${
          showDrumStudio ? 'bg-purple-600' : 'bg-gray-700 hover:bg-purple-600'
        }`}
      >
        <span>🥁</span>
        <span className="text-sm">Enhanced Drum Studio</span>
        {showDrumStudio ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>
    </div>
  </div>
);

const TransportControls = ({ isPlaying, handlePlay, handleStop, currentTime, duration, formatTime }) => (
  <div className="bg-gray-800 border-b border-gray-700 p-4">
    <div className="flex items-center justify-center space-x-4">
      <button 
        onClick={handlePlay}
        className="flex items-center space-x-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
      >
        {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
        <span>{isPlaying ? 'Pause' : 'Play'}</span>
      </button>
      <button 
        onClick={handleStop} 
        className="p-3 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
      >
        <Square className="w-5 h-5" />
      </button>
      <div className="text-lg font-mono bg-gray-700 px-4 py-2 rounded border border-gray-600">
        <div className="text-white">{formatTime(currentTime)} / {formatTime(duration)}</div>
        <div className="text-xs text-gray-400 text-center">Time</div>
      </div>
    </div>
  </div>
);

const WebDAW = ({ audioAnalysis, onBack }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(180);
  const [tempo, setTempo] = useState(120);
  const [timeSignature, setTimeSignature] = useState('4/4');
  const [showDrumStudio, setShowDrumStudio] = useState(true);
  const [drumStyle, setDrumStyle] = useState('Rock');
  const [complexity, setComplexity] = useState(7);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationProgress, setGenerationProgress] = useState(0);
  const [selectedSection, setSelectedSection] = useState(0);
  
  const [arrangement, setArrangement] = useState([
    {
      id: 1,
      type: 'Intro',
      name: 'Intro 1',
      duration: 8,
      drumSettings: {
        complexity: 5,
        humanization: 80,
        ghostNotes: 20,
        flams: 5,
        rimshots: 10,
        footSplash: 15,
        chokeFrequency: 5,
        snareType: 'Center',
        hihatState: 'Closed',
        timingDrift: 20,
        swingAmount: 0,
        pushPull: 'On Beat',
        bellAccents: 10,
        crashIntegration: 20,
        rideStyle: 'Tip'
      }
    },
    {
      id: 2,
      type: 'Verse',
      name: 'Verse 1',
      duration: 16,
      drumSettings: {
        complexity: 6,
        humanization: 75,
        ghostNotes: 40,
        flams: 15,
        rimshots: 20,
        footSplash: 25,
        chokeFrequency: 10,
        snareType: 'Center',
        hihatState: 'Closed',
        timingDrift: 25,
        swingAmount: 10,
        pushPull: 'On Beat',
        bellAccents: 15,
        crashIntegration: 25,
        rideStyle: 'Tip'
      }
    },
    {
      id: 3,
      type: 'Chorus',
      name: 'Chorus 1',
      duration: 16,
      drumSettings: {
        complexity: 8,
        humanization: 70,
        ghostNotes: 30,
        flams: 20,
        rimshots: 30,
        footSplash: 35,
        chokeFrequency: 15,
        snareType: 'Center',
        hihatState: 'Semi',
        timingDrift: 30,
        swingAmount: 5,
        pushPull: 'Pushing',
        bellAccents: 25,
        crashIntegration: 40,
        rideStyle: 'Shoulder'
      }
    }
  ]);

  const animationFrameRef = useRef(null);

  useEffect(() => {
    if (audioAnalysis) {
      setTempo(audioAnalysis.tempo || 120);
      setDuration(audioAnalysis.duration || 180);
    }
  }, [audioAnalysis]);

  const handlePlay = () => {
    if (isPlaying) {
      setIsPlaying(false);
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    } else {
      setIsPlaying(true);
      const startTime = Date.now() - currentTime * 1000;
      const updateTime = () => {
        const elapsed = (Date.now() - startTime) / 1000;
        if (elapsed >= duration) {
          setCurrentTime(0);
          setIsPlaying(false);
        } else {
          setCurrentTime(elapsed);
          animationFrameRef.current = requestAnimationFrame(updateTime);
        }
      };
      updateTime();
    }
  };

  const handleStop = () => {
    setIsPlaying(false);
    setCurrentTime(0);
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
  };

  const handleGenerateDrums = async () => {
    setIsGenerating(true);
    for (let i = 0; i <= 100; i += 20) {
      setGenerationProgress(i);
      await new Promise(resolve => setTimeout(resolve, 500));
    }
    setIsGenerating(false);
    setGenerationProgress(0);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="h-screen bg-gray-900 text-white flex flex-col overflow-hidden">
      <DAWHeader 
        onBack={onBack}
        tempo={tempo}
        timeSignature={timeSignature}
        isGenerating={isGenerating}
        showDrumStudio={showDrumStudio}
        setShowDrumStudio={setShowDrumStudio}
      />

      <TransportControls 
        isPlaying={isPlaying}
        handlePlay={handlePlay}
        handleStop={handleStop}
        currentTime={currentTime}
        duration={duration}
        formatTime={formatTime}
      />

      <div className="flex-1 bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 flex items-center justify-center">
        <div className="text-center p-8">
          <div className="text-6xl mb-4">🎵</div>
          <h3 className="text-2xl font-bold mb-2">Enhanced Drum Creation Studio</h3>
          <p className="text-gray-300 mb-4">
            Create professional drum tracks with section-specific advanced controls
          </p>
          <div className="text-sm text-gray-400">
            Use the Enhanced Drum Studio below to create section-specific drum patterns
          </div>
        </div>
      </div>

      <EnhancedDrumStudio 
        showDrumStudio={showDrumStudio}
        isGenerating={isGenerating}
        generationProgress={generationProgress}
        handleGenerateDrums={handleGenerateDrums}
        drumStyle={drumStyle}
        setDrumStyle={setDrumStyle}
        complexity={complexity}
        setComplexity={setComplexity}
        tempo={tempo}
        setTempo={setTempo}
        arrangement={arrangement}
        setArrangement={setArrangement}
        selectedSection={selectedSection}
        setSelectedSection={setSelectedSection}
      />
    </div>
  );
};

export default WebDAW;