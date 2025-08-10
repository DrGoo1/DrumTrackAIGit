import React, { useState, useEffect, useRef } from 'react';
import { 
  Play, Pause, Square, SkipBack, SkipForward, Volume2, Settings,
  Scissors, Copy, Clipboard, Trash2, Undo, Redo, ZoomIn, ZoomOut,
  Move, RotateCcw, Maximize2, Minimize2, Grid, Lock, Unlock,
  VolumeX, Volume1, Mic, MicOff, Eye, EyeOff, MoreHorizontal,
  Download, Upload, Save, FileText, Split, Merge, Edit3
} from 'lucide-react';

const WebDAW = ({ audioAnalysis, onBack }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(180);
  const [zoom, setZoom] = useState(1);
  const [snapToGrid, setSnapToGrid] = useState(true);
  const [selectedTrack, setSelectedTrack] = useState(0);
  const [tracks, setTracks] = useState([]);
  const [tempo, setTempo] = useState(120);
  const [timeSignature, setTimeSignature] = useState('4/4');
  
  // Cut/Copy/Paste functionality
  const [clipboard, setClipboard] = useState(null);
  const [selectedRegion, setSelectedRegion] = useState(null);
  const [selectionStart, setSelectionStart] = useState(null);
  const [selectionEnd, setSelectionEnd] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState(null);
  
  // Track editing states
  const [soloTracks, setSoloTracks] = useState(new Set());
  const [muteTracks, setMuteTracks] = useState(new Set());
  const [recordingTracks, setRecordingTracks] = useState(new Set());
  const [lockedTracks, setLockedTracks] = useState(new Set());
  
  // Undo/Redo system
  const [history, setHistory] = useState([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  
  const animationFrameRef = useRef(null);
  const waveformContainerRef = useRef(null);

  // Initialize tracks from audio analysis
  useEffect(() => {
    if (audioAnalysis) {
      const analysisData = audioAnalysis;
      setTempo(analysisData.tempo || 120);
      setTimeSignature(analysisData.timeSignature || '4/4');
      
      // Create comprehensive track list with individual drum instruments
      const trackList = [
        { id: 'master', name: 'Master Mix', type: 'audio', color: '#3B82F6', muted: false, solo: false, volume: 80, pan: 0, height: 60, regions: [] },
        { id: 'bass', name: 'Bass', type: 'audio', color: '#EF4444', muted: false, solo: false, volume: 70, pan: 0, height: 50, regions: [] },
        { id: 'vocals', name: 'Vocals', type: 'audio', color: '#F59E0B', muted: false, solo: false, volume: 60, pan: 0, height: 50, regions: [] },
        { id: 'other', name: 'Other Instruments', type: 'audio', color: '#8B5CF6', muted: false, solo: false, volume: 50, pan: 0, height: 50, regions: [] },
        
        // Individual drum instruments
        { id: 'kick', name: 'Kick Drum', type: 'drum', color: '#DC2626', muted: false, solo: false, volume: 85, pan: 0, height: 40, regions: [] },
        { id: 'snare', name: 'Snare Drum', type: 'drum', color: '#EA580C', muted: false, solo: false, volume: 75, pan: 0, height: 40, regions: [] },
        { id: 'hihat', name: 'Hi-Hat', type: 'drum', color: '#D97706', muted: false, solo: false, volume: 60, pan: 10, height: 35, regions: [] },
        { id: 'crash', name: 'Crash Cymbal', type: 'drum', color: '#CA8A04', muted: false, solo: false, volume: 70, pan: -15, height: 35, regions: [] },
        { id: 'ride', name: 'Ride Cymbal', type: 'drum', color: '#65A30D', muted: false, solo: false, volume: 65, pan: 20, height: 35, regions: [] },
        { id: 'tom1', name: 'High Tom', type: 'drum', color: '#16A34A', muted: false, solo: false, volume: 70, pan: -10, height: 35, regions: [] },
        { id: 'tom2', name: 'Mid Tom', type: 'drum', color: '#059669', muted: false, solo: false, volume: 70, pan: 0, height: 35, regions: [] },
        { id: 'tom3', name: 'Floor Tom', type: 'drum', color: '#0891B2', muted: false, solo: false, volume: 75, pan: 15, height: 35, regions: [] }
      ];
      
      setTracks(trackList);
      setDuration(analysisData.duration || 180);
      saveToHistory(trackList);
    }
  }, [audioAnalysis]);

  // History management
  const saveToHistory = (newTracks) => {
    const newHistory = history.slice(0, historyIndex + 1);
    newHistory.push(JSON.parse(JSON.stringify(newTracks)));
    setHistory(newHistory);
    setHistoryIndex(newHistory.length - 1);
  };

  const undo = () => {
    if (historyIndex > 0) {
      setHistoryIndex(historyIndex - 1);
      setTracks(JSON.parse(JSON.stringify(history[historyIndex - 1])));
    }
  };

  const redo = () => {
    if (historyIndex < history.length - 1) {
      setHistoryIndex(historyIndex + 1);
      setTracks(JSON.parse(JSON.stringify(history[historyIndex + 1])));
    }
  };

  // Transport controls
  const handlePlay = () => {
    setIsPlaying(!isPlaying);
    if (!isPlaying) {
      // Start playback animation
      const startTime = Date.now() - (currentTime * 1000);
      const updateTime = () => {
        const elapsed = (Date.now() - startTime) / 1000;
        if (elapsed < duration) {
          setCurrentTime(elapsed);
          animationFrameRef.current = requestAnimationFrame(updateTime);
        } else {
          setIsPlaying(false);
          setCurrentTime(0);
        }
      };
      animationFrameRef.current = requestAnimationFrame(updateTime);
    } else {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    }
  };

  const handleStop = () => {
    setIsPlaying(false);
    setCurrentTime(0);
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
  };

  const handleSeek = (time) => {
    setCurrentTime(Math.max(0, Math.min(time, duration)));
  };

  // Track controls
  const updateTrack = (trackId, property, value) => {
    const newTracks = tracks.map(track => 
      track.id === trackId ? { ...track, [property]: value } : track
    );
    setTracks(newTracks);
    if (property !== 'volume' && property !== 'pan') {
      saveToHistory(newTracks);
    }
  };

  const toggleTrackProperty = (trackId, property, stateSet, setStateSet) => {
    const newSet = new Set(stateSet);
    if (newSet.has(trackId)) {
      newSet.delete(trackId);
    } else {
      newSet.add(trackId);
    }
    setStateSet(newSet);
  };

  // Selection handling
  const handleMouseDown = (e, trackIndex) => {
    if (e.button !== 0) return; // Only left click
    
    const rect = waveformContainerRef.current?.getBoundingClientRect();
    if (!rect) return;
    
    const x = e.clientX - rect.left;
    const time = (x / (rect.width * zoom)) * duration;
    
    setIsDragging(true);
    setDragStart(time);
    setSelectionStart(time);
    setSelectionEnd(time);
    setSelectedTrack(trackIndex);
  };

  const handleMouseMove = (e) => {
    if (!isDragging || !waveformContainerRef.current) return;
    
    const rect = waveformContainerRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const time = (x / (rect.width * zoom)) * duration;
    
    setSelectionEnd(time);
  };

  const handleMouseUp = () => {
    if (isDragging && selectionStart !== null && selectionEnd !== null) {
      const start = Math.min(selectionStart, selectionEnd);
      const end = Math.max(selectionStart, selectionEnd);
      
      if (Math.abs(end - start) > 0.1) { // Minimum selection of 0.1 seconds
        setSelectedRegion({ start, end, trackIndex: selectedTrack });
      }
    }
    
    setIsDragging(false);
    setDragStart(null);
  };

  // Cut, Copy, Paste operations
  const cutSelection = () => {
    if (!selectedRegion) return;
    
    const { start, end, trackIndex } = selectedRegion;
    const track = tracks[trackIndex];
    
    // Store the cut region in clipboard
    setClipboard({
      type: 'cut',
      data: { start, end, trackId: track.id },
      duration: end - start
    });
    
    // Remove the selected region from the track
    const newTracks = [...tracks];
    // In a real implementation, this would modify the actual audio data
    newTracks[trackIndex] = {
      ...track,
      regions: [...(track.regions || []), { type: 'cut', start, end }]
    };
    
    setTracks(newTracks);
    setSelectedRegion(null);
    saveToHistory(newTracks);
  };

  const copySelection = () => {
    if (!selectedRegion) return;
    
    const { start, end, trackIndex } = selectedRegion;
    const track = tracks[trackIndex];
    
    setClipboard({
      type: 'copy',
      data: { start, end, trackId: track.id },
      duration: end - start
    });
  };

  const pasteClipboard = () => {
    if (!clipboard || selectedTrack === null) return;
    
    const track = tracks[selectedTrack];
    const pasteTime = currentTime;
    
    const newTracks = [...tracks];
    newTracks[selectedTrack] = {
      ...track,
      regions: [...(track.regions || []), {
        type: 'paste',
        start: pasteTime,
        end: pasteTime + clipboard.duration,
        source: clipboard.data
      }]
    };
    
    setTracks(newTracks);
    saveToHistory(newTracks);
  };

  const deleteSelection = () => {
    if (!selectedRegion) return;
    
    const { start, end, trackIndex } = selectedRegion;
    const newTracks = [...tracks];
    const track = tracks[trackIndex];
    
    newTracks[trackIndex] = {
      ...track,
      regions: [...(track.regions || []), { type: 'delete', start, end }]
    };
    
    setTracks(newTracks);
    setSelectedRegion(null);
    saveToHistory(newTracks);
  };

  // Format time display
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    const ms = Math.floor((seconds % 1) * 100);
    return `${mins}:${secs.toString().padStart(2, '0')}.${ms.toString().padStart(2, '0')}`;
  };

  // Format bars.beats.ticks
  const formatBBT = (seconds) => {
    const beatsPerSecond = tempo / 60;
    const totalBeats = seconds * beatsPerSecond;
    const bars = Math.floor(totalBeats / 4) + 1;
    const beats = Math.floor(totalBeats % 4) + 1;
    const ticks = Math.floor((totalBeats % 1) * 480);
    return `${bars}.${beats}.${ticks.toString().padStart(3, '0')}`;
  };

  // Generate arrangement sections
  const getArrangementSections = () => {
    if (!audioAnalysis?.structure) {
      return [
        { section: 'Intro', start: 0, end: 8, color: '#3B82F6' },
        { section: 'Verse', start: 8, end: 32, color: '#10B981' },
        { section: 'Chorus', start: 32, end: 56, color: '#EF4444' },
        { section: 'Verse', start: 56, end: 80, color: '#10B981' },
        { section: 'Chorus', start: 80, end: 104, color: '#EF4444' },
        { section: 'Bridge', start: 104, end: 120, color: '#F59E0B' },
        { section: 'Chorus', start: 120, end: 144, color: '#EF4444' },
        { section: 'Outro', start: 144, end: 180, color: '#6B7280' }
      ];
    }
    return audioAnalysis.structure.map(section => ({
      ...section,
      color: {
        'Intro': '#3B82F6', 'Verse': '#10B981', 'Chorus': '#EF4444',
        'Bridge': '#F59E0B', 'Solo': '#8B5CF6', 'Outro': '#6B7280'
      }[section.section] || '#6B7280'
    }));
  };

  // Generate timeline markers
  const generateTimelineMarkers = () => {
    const markers = [];
    const pixelsPerSecond = 50 * zoom;
    const beatsPerSecond = tempo / 60;
    
    for (let i = 0; i <= duration; i += 60 / tempo) {
      const x = i * pixelsPerSecond;
      const beatNumber = Math.floor(i * beatsPerSecond) + 1;
      const isDownbeat = (beatNumber - 1) % 4 === 0;
      
      markers.push({ x, time: i, isDownbeat, beatNumber });
    }
    
    return markers;
  };

  // Generate waveform data for visualization
  const generateWaveformData = (trackId, width = 800) => {
    const points = [];
    for (let i = 0; i < width; i++) {
      const t = (i / width) * duration;
      const freq = {
        master: 1, bass: 0.5, vocals: 2, other: 1.5,
        kick: 0.3, snare: 4, hihat: 8, crash: 6,
        ride: 5, tom1: 3, tom2: 2.5, tom3: 2
      }[trackId] || 1;
      
      const amplitude = Math.sin(t * freq) * Math.exp(-t * 0.1) * 0.8;
      points.push(amplitude);
    }
    return points;
  };

  // Generate waveform path
  const generateWaveformPath = (data, width, height) => {
    if (!data || data.length === 0) return '';
    
    const points = data.map((point, i) => {
      const x = (i / data.length) * width;
      const y = height / 2 + (point * height / 4);
      return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
    }).join(' ');
    
    return points;
  };

  return (
    <div 
      className="w-full h-full bg-gray-900 text-white flex flex-col" 
      style={{ width: '100vw', height: '100vh' }}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
    >
      {/* DAW Header */}
      <div className="bg-gray-800 border-b border-gray-700 p-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button 
              onClick={onBack}
              className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm transition-colors"
            >
              ← Back to Analysis
            </button>
            <h2 className="text-xl font-bold flex items-center space-x-2">
              <span>🎵 DrumTracKAI Pro Studio</span>
              <span className="text-sm font-normal text-gray-400">WebDAW</span>
            </h2>
            <div className="text-sm text-gray-400 bg-gray-700 px-3 py-1 rounded">
              {tempo} BPM • {audioAnalysis?.key || 'C'} • {timeSignature}
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button className="p-2 hover:bg-gray-700 rounded transition-colors">
              <Settings className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Transport Controls */}
      <div className="bg-gray-800 border-b border-gray-700 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button 
              onClick={handlePlay}
              className="flex items-center space-x-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors shadow-lg"
            >
              {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
              <span className="font-medium">{isPlaying ? 'Pause' : 'Play'}</span>
            </button>
            
            <button 
              onClick={handleStop}
              className="p-3 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
            >
              <Square className="w-5 h-5" />
            </button>
            
            <button className="p-3 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">
              <SkipBack className="w-5 h-5" />
            </button>
            
            <button className="p-3 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">
              <SkipForward className="w-5 h-5" />
            </button>

            {/* Edit Controls */}
            <div className="flex items-center space-x-2 ml-6 border-l border-gray-600 pl-6">
              <button 
                onClick={undo}
                disabled={historyIndex <= 0}
                className="p-2 bg-gray-700 hover:bg-gray-600 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                title="Undo"
              >
                <Undo className="w-4 h-4" />
              </button>
              
              <button 
                onClick={redo}
                disabled={historyIndex >= history.length - 1}
                className="p-2 bg-gray-700 hover:bg-gray-600 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                title="Redo"
              >
                <Redo className="w-4 h-4" />
              </button>
              
              <button 
                onClick={cutSelection}
                disabled={!selectedRegion}
                className="p-2 bg-gray-700 hover:bg-gray-600 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                title="Cut"
              >
                <Scissors className="w-4 h-4" />
              </button>
              
              <button 
                onClick={copySelection}
                disabled={!selectedRegion}
                className="p-2 bg-gray-700 hover:bg-gray-600 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                title="Copy"
              >
                <Copy className="w-4 h-4" />
              </button>
              
              <button 
                onClick={pasteClipboard}
                disabled={!clipboard}
                className="p-2 bg-gray-700 hover:bg-gray-600 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                title="Paste"
              >
                <Clipboard className="w-4 h-4" />
              </button>
              
              <button 
                onClick={deleteSelection}
                disabled={!selectedRegion}
                className="p-2 bg-red-700 hover:bg-red-600 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                title="Delete"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
          
          <div className="flex items-center space-x-6">
            <div className="text-lg font-mono bg-gray-700 px-4 py-2 rounded">
              {formatTime(currentTime)} / {formatTime(duration)}
            </div>
            <div className="text-lg font-mono text-blue-400 bg-blue-900 bg-opacity-30 px-4 py-2 rounded">
              {formatBBT(currentTime)}
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <label className="flex items-center space-x-2 bg-gray-700 px-3 py-2 rounded">
              <input 
                type="checkbox" 
                checked={snapToGrid}
                onChange={(e) => setSnapToGrid(e.target.checked)}
                className="rounded"
              />
              <span className="text-sm font-medium">Snap to Grid</span>
            </label>
            
            <div className="flex items-center space-x-3 bg-gray-700 px-3 py-2 rounded">
              <span className="text-sm font-medium">Zoom:</span>
              <button 
                onClick={() => setZoom(Math.max(0.1, zoom - 0.2))}
                className="p-1 hover:bg-gray-600 rounded"
              >
                <ZoomOut className="w-3 h-3" />
              </button>
              <input 
                type="range" 
                min="0.5" 
                max="5" 
                step="0.1" 
                value={zoom}
                onChange={(e) => setZoom(parseFloat(e.target.value))}
                className="w-24"
              />
              <button 
                onClick={() => setZoom(Math.min(5, zoom + 0.2))}
                className="p-1 hover:bg-gray-600 rounded"
              >
                <ZoomIn className="w-3 h-3" />
              </button>
              <span className="text-sm font-mono w-12">{zoom.toFixed(1)}x</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Drum Creation Controls - Separate Column */}
        <div className="w-80 bg-gradient-to-b from-purple-900 to-gray-900 border-r border-purple-600 flex flex-col">
          {/* Drum Creation Header */}
          <div className="p-4 border-b border-purple-600 bg-purple-800 bg-opacity-50">
            <h3 className="font-bold text-purple-200 flex items-center text-lg">
              🥁 Drum Creation Studio
            </h3>
            <p className="text-sm text-purple-300 mt-1">AI-Powered Professional Controls</p>
          </div>
          
          {/* Scrollable Creation Controls */}
          <div className="flex-1 overflow-y-auto p-2">
            {/* Quick Generation Controls - Most Visible */}
            <div className="p-3 border-b border-gray-700 bg-gradient-to-r from-purple-900 to-blue-900 bg-opacity-50">
              <h4 className="font-medium text-sm text-yellow-300 mb-3 flex items-center">
                ⚡ Quick Generate
              </h4>
              <button className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 px-4 py-3 rounded-lg font-medium text-white transition-all duration-200 mb-3 text-sm">
                🥁 Generate Drum Track Now
              </button>
              <div className="grid grid-cols-2 gap-2">
                <button className="bg-gray-700 hover:bg-blue-600 px-3 py-2 rounded text-xs transition-colors">
                  🎸 Rock Style
                </button>
                <button className="bg-gray-700 hover:bg-green-600 px-3 py-2 rounded text-xs transition-colors">
                  🎵 Jazz Style
                </button>
                <button className="bg-gray-700 hover:bg-red-600 px-3 py-2 rounded text-xs transition-colors">
                  🔥 Metal Style
                </button>
                <button className="bg-gray-700 hover:bg-yellow-600 px-3 py-2 rounded text-xs transition-colors">
                  🎶 Funk Style
                </button>
              </div>
            </div>
            
            {/* Style & Genre Controls */}
            <div className="p-3 border-b border-gray-700">
              <h4 className="font-medium text-sm text-blue-300 mb-2">🎼 Style & Genre</h4>
              <div className="space-y-2">
                <div>
                  <label className="text-xs text-gray-400 block mb-1">Primary Style</label>
                  <select className="w-full bg-gray-700 border border-gray-600 rounded px-2 py-1 text-xs text-white focus:border-blue-500">
                    <option>Rock</option>
                    <option>Pop</option>
                    <option>Jazz</option>
                    <option>Funk</option>
                    <option>R&B</option>
                    <option>Metal</option>
                    <option>Country</option>
                    <option>Latin</option>
                    <option>Electronic</option>
                    <option>Hip-Hop</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs text-gray-400 block mb-1">Complexity: <span className="text-yellow-300 font-mono">7</span></label>
                  <input type="range" min="1" max="10" defaultValue="7" className="w-full h-2 bg-gray-600 rounded appearance-none cursor-pointer" />
                </div>
              </div>
            </div>
            
            {/* Tempo & Feel Controls */}
            <div className="p-3 border-b border-gray-700">
              <h4 className="font-medium text-sm text-green-300 mb-2">🎯 Tempo & Feel</h4>
              <div className="space-y-2">
                <div>
                  <label className="text-xs text-gray-400 block mb-1">Base Tempo: <span className="text-green-300 font-mono">{tempo} BPM</span></label>
                  <input type="range" min="60" max="200" value={tempo} onChange={(e) => setTempo(parseInt(e.target.value))} className="w-full h-2 bg-gray-600 rounded appearance-none cursor-pointer" />
                </div>
                <div>
                  <label className="text-xs text-gray-400 block mb-1">Timing Feel</label>
                  <div className="grid grid-cols-3 gap-1">
                    <button className="bg-gray-700 hover:bg-green-600 px-2 py-1 rounded text-xs transition-colors">Laid Back</button>
                    <button className="bg-green-600 px-2 py-1 rounded text-xs">On Beat</button>
                    <button className="bg-gray-700 hover:bg-green-600 px-2 py-1 rounded text-xs transition-colors">Pushing</button>
                  </div>
                </div>
                <div>
                  <label className="text-xs text-gray-400 block mb-1">Groove Tightness: <span className="text-green-300 font-mono">85%</span></label>
                  <input type="range" min="0" max="100" defaultValue="85" className="w-full h-2 bg-gray-600 rounded appearance-none cursor-pointer" />
                </div>
              </div>
            </div>
            
            {/* Human Factors */}
            <div className="p-3 border-b border-gray-700">
              <h4 className="font-medium text-sm text-yellow-300 mb-2">🧠 Human Factors</h4>
              <div className="space-y-2">
                <div>
                  <label className="text-xs text-gray-400 block mb-1">Humanization: <span className="text-yellow-300 font-mono">75%</span></label>
                  <input type="range" min="0" max="100" defaultValue="75" className="w-full h-2 bg-gray-600 rounded appearance-none cursor-pointer" />
                </div>
                <div>
                  <label className="text-xs text-gray-400 block mb-1">Velocity Variation: <span className="text-yellow-300 font-mono">60%</span></label>
                  <input type="range" min="0" max="100" defaultValue="60" className="w-full h-2 bg-gray-600 rounded appearance-none cursor-pointer" />
                </div>
                <div>
                  <label className="text-xs text-gray-400 block mb-1">Timing Drift: <span className="text-yellow-300 font-mono">25%</span></label>
                  <input type="range" min="0" max="100" defaultValue="25" className="w-full h-2 bg-gray-600 rounded appearance-none cursor-pointer" />
                </div>
              </div>
            </div>
            
            {/* Drum Velocity & Dynamics */}
            <div className="p-3 border-b border-gray-700">
              <h4 className="font-medium text-sm text-red-300 mb-2">Velocity & Dynamics</h4>
              <div className="space-y-2">
                <div>
                  <label className="text-xs text-gray-400 block mb-1">Overall Velocity: <span className="text-white font-mono">80</span></label>
                  <input type="range" min="1" max="127" defaultValue="80" className="w-full h-1 bg-gray-600 rounded appearance-none cursor-pointer" />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-xs text-gray-400 block mb-1">Kick: <span className="text-white font-mono">95</span></label>
                    <input type="range" min="1" max="127" defaultValue="95" className="w-full h-1 bg-gray-600 rounded appearance-none cursor-pointer" />
                  </div>
                  <div>
                    <label className="text-xs text-gray-400 block mb-1">Snare: <span className="text-white font-mono">85</span></label>
                    <input type="range" min="1" max="127" defaultValue="85" className="w-full h-1 bg-gray-600 rounded appearance-none cursor-pointer" />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-xs text-gray-400 block mb-1">Hi-Hat: <span className="text-white font-mono">70</span></label>
                    <input type="range" min="1" max="127" defaultValue="70" className="w-full h-1 bg-gray-600 rounded appearance-none cursor-pointer" />
                  </div>
                  <div>
                    <label className="text-xs text-gray-400 block mb-1">Cymbals: <span className="text-white font-mono">90</span></label>
                    <input type="range" min="1" max="127" defaultValue="90" className="w-full h-1 bg-gray-600 rounded appearance-none cursor-pointer" />
                  </div>
                </div>
              </div>
            </div>
            
            {/* Generate Button */}
            <div className="p-3">
              <button className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 px-4 py-2 rounded font-medium text-white transition-all duration-200">
                🥁 Generate Drum Track
              </button>
            </div>
          </div>
        </div>
        
        {/* DAW Window - Full Width */}
        <div className="flex-1 flex flex-col bg-gray-900 border border-gray-700 rounded-l-lg overflow-hidden">
          {/* Enhanced Timeline Header - Full Width */}
          <div className="h-24 bg-gray-800 border-b border-gray-700 relative">
            <div className="absolute inset-0 p-2">
              {/* Tempo and Musical Information */}
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-3 text-sm">
                  <div className="bg-blue-900 bg-opacity-70 px-3 py-1 rounded border border-blue-600">
                    <span className="font-bold text-blue-200">{tempo} BPM</span>
                  </div>
                  <div className="bg-green-900 bg-opacity-70 px-3 py-1 rounded border border-green-600">
                    <span className="font-bold text-green-200">{timeSignature}</span>
                  </div>
                  <div className="bg-purple-900 bg-opacity-70 px-3 py-1 rounded border border-purple-600">
                    <span className="font-bold text-purple-200">Key: {audioAnalysis?.key || 'G'}</span>
                  </div>
                </div>
                <div className="text-sm text-gray-300 bg-gray-700 px-3 py-1 rounded border border-gray-600">
                  Duration: {formatTime(duration)}
                </div>
              </div>
              
              {/* Professional Timeline Ruler */}
              <div className="relative h-12 bg-gray-700 rounded border border-gray-600 overflow-hidden">
                {/* Arrangement Sections */}
                {getArrangementSections().map((section, index) => {
                  const startX = (section.start / duration) * 1200 * zoom;
                  const width = ((section.end - section.start) / duration) * 1200 * zoom;
                  return (
                    <div
                      key={index}
                      className="absolute top-0 h-6 border-r border-gray-500 flex items-center"
                      style={{
                        left: `${startX}px`,
                        width: `${Math.max(width, 40)}px`,
                        backgroundColor: section.color,
                        opacity: 0.8
                      }}
                    >
                      <span className="text-xs text-white font-bold px-2 truncate">
                        {section.section}
                      </span>
                    </div>
                  );
                })}
                
                {/* Playhead */}
                <div
                  className="absolute top-0 w-0.5 h-full bg-red-500 z-30"
                  style={{ left: `${(currentTime / duration) * 1200 * zoom}px` }}
                >
                  <div className="absolute -top-1 -left-1.5 w-3 h-3 bg-red-500 rounded-full" />
                </div>
              </div>
            </div>
          </div>
          
          {/* Horizontal Layout: Mixer + Output Meters + Waveforms */}
          <div className="flex-1 flex overflow-hidden">
            {/* Clean Mixer Console */}
            <div className="w-64 bg-gray-800 border-r border-gray-700 flex flex-col">
              <div className="p-2 border-b border-gray-700">
                <h3 className="font-semibold text-white text-sm">Mixer</h3>
                <p className="text-xs text-gray-400">{tracks.length} tracks</p>
              </div>
            
              <div className="flex-1 overflow-y-auto">
                {tracks.map((track, index) => {
                  const isMuted = muteTracks.has(track.id);
                  const isSolo = soloTracks.has(track.id);
                  const isRecording = recordingTracks.has(track.id);
                  const actualVolume = isMuted ? 0 : (track.volume || 75);
                  
                  return (
                    <div 
                      key={track.id}
                      className="border-b border-gray-700 p-2"
                      style={{ height: '80px' }}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-medium text-white truncate">{track.name}</span>
                        <div className="flex space-x-1">
                          <button 
                            onClick={() => {
                              toggleTrackProperty(track.id, 'mute', muteTracks, setMuteTracks);
                              updateTrack(track.id, 'muted', !isMuted);
                            }}
                            className={`px-1 py-0.5 text-xs rounded transition-colors ${
                              isMuted ? 'bg-red-600 text-white shadow-lg' : 'bg-gray-600 hover:bg-red-600'
                            }`}
                            title="Mute"
                          >
                            M
                          </button>
                          <button 
                            onClick={() => {
                              toggleTrackProperty(track.id, 'solo', soloTracks, setSoloTracks);
                              updateTrack(track.id, 'solo', !isSolo);
                            }}
                            className={`px-1 py-0.5 text-xs rounded transition-colors ${
                              isSolo ? 'bg-yellow-600 text-white shadow-lg' : 'bg-gray-600 hover:bg-yellow-600'
                            }`}
                            title="Solo"
                          >
                            S
                          </button>
                          <button 
                            onClick={() => {
                              toggleTrackProperty(track.id, 'record', recordingTracks, setRecordingTracks);
                              updateTrack(track.id, 'recording', !isRecording);
                            }}
                            className={`px-1 py-0.5 text-xs rounded transition-colors ${
                              isRecording ? 'bg-red-600 text-white shadow-lg animate-pulse' : 'bg-gray-600 hover:bg-red-600'
                            }`}
                            title="Record"
                          >
                            R
                          </button>
                        </div>
                      </div>
                      
                      {/* Volume Control */}
                      <div className="flex items-center space-x-2 mb-1">
                        <Volume2 className="w-3 h-3 text-gray-400" />
                        <input 
                          type="range" 
                          min="0" 
                          max="100" 
                          value={track.volume || 75}
                          onChange={(e) => updateTrack(track.id, 'volume', parseInt(e.target.value))}
                          className="flex-1 h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer slider-volume"
                          style={{
                            background: `linear-gradient(to right, #3B82F6 0%, #3B82F6 ${track.volume || 75}%, #4B5563 ${track.volume || 75}%, #4B5563 100%)`
                          }}
                        />
                        <span className="text-xs text-gray-300 w-8 text-right">{track.volume || 75}</span>
                      </div>
                      
                      {/* Pan Control - Smaller and Different Color */}
                      <div className="flex items-center space-x-2">
                        <span className="text-xs text-orange-400 w-6">Pan</span>
                        <input 
                          type="range" 
                          min="-100" 
                          max="100" 
                          value={track.pan || 0}
                          onChange={(e) => updateTrack(track.id, 'pan', parseInt(e.target.value))}
                          className="flex-1 h-1 bg-gray-600 rounded-lg appearance-none cursor-pointer slider-pan"
                          style={{
                            background: `linear-gradient(to right, #F97316 0%, #F97316 ${((track.pan || 0) + 100) / 2}%, #4B5563 ${((track.pan || 0) + 100) / 2}%, #4B5563 100%)`
                          }}
                        />
                        <span className="text-xs text-orange-300 w-8 text-right">{track.pan > 0 ? `R${track.pan}` : track.pan < 0 ? `L${Math.abs(track.pan)}` : 'C'}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Output Meters - Purple Bar */}
            <div className="w-12 bg-gradient-to-b from-purple-800 to-purple-900 border-r border-purple-600 flex flex-col">
              <div className="p-1 border-b border-purple-600 text-center">
                <h4 className="text-xs font-medium text-purple-200">Meters</h4>
              </div>
              
              <div className="flex-1 overflow-y-auto">
                {tracks.map((track, index) => {
                  const isMuted = muteTracks.has(track.id);
                  const isSolo = soloTracks.has(track.id);
                  
                  // Calculate meter level based on track properties and playback
                  const baseLevel = isMuted ? 0 : (track.volume || 75);
                  const playbackMultiplier = isPlaying ? (0.7 + Math.sin(currentTime * 10 + index) * 0.3) : 0.1;
                  const meterLevel = (baseLevel / 100) * playbackMultiplier;
                  const meterHeight = Math.min(meterLevel * 70, 70); // Max 70px height per track
                  
                  // Color based on level
                  const getMeterColor = (level) => {
                    if (level > 0.9) return '#EF4444'; // Red - clipping
                    if (level > 0.7) return '#F59E0B'; // Yellow - high
                    return '#10B981'; // Green - normal
                  };
                  
                  return (
                    <div 
                      key={track.id}
                      className="flex flex-col justify-end items-center border-b border-purple-700 relative"
                      style={{ height: '80px' }}
                    >
                      {/* Meter Background */}
                      <div className="w-6 h-16 bg-gray-800 rounded border border-gray-600 relative overflow-hidden">
                        {/* Peak Indicators */}
                        <div className="absolute inset-x-0 top-0 h-1 bg-red-500 opacity-30"></div>
                        <div className="absolute inset-x-0 top-2 h-px bg-yellow-500 opacity-50"></div>
                        <div className="absolute inset-x-0 top-6 h-px bg-green-500 opacity-50"></div>
                        
                        {/* Active Meter */}
                        <div 
                          className="absolute bottom-0 left-0 right-0 transition-all duration-100 rounded-b"
                          style={{ 
                            height: `${meterHeight}px`,
                            backgroundColor: getMeterColor(meterLevel),
                            boxShadow: `0 0 4px ${getMeterColor(meterLevel)}`
                          }}
                        ></div>
                        
                        {/* Peak Hold */}
                        {meterLevel > 0.1 && (
                          <div 
                            className="absolute left-0 right-0 h-px bg-white"
                            style={{ bottom: `${Math.max(meterHeight - 2, 0)}px` }}
                          ></div>
                        )}
                      </div>
                      
                      {/* Track Status Indicators */}
                      <div className="flex space-x-px mt-1">
                        {isMuted && <div className="w-1 h-1 bg-red-500 rounded-full"></div>}
                        {isSolo && <div className="w-1 h-1 bg-yellow-500 rounded-full"></div>}
                        {recordingTracks.has(track.id) && <div className="w-1 h-1 bg-red-500 rounded-full animate-pulse"></div>}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
            
            {/* Waveforms Section */}
            <div className="flex-1 flex flex-col bg-gray-900 overflow-hidden">
              <div className="p-2 border-b border-gray-700 flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-white text-sm">Arrangement & Waveforms</h3>
                  <div className="text-xs text-gray-400">
                    {selectedRegion && `Selection: ${formatTime(selectedRegion.start)} - ${formatTime(selectedRegion.end)}`}
                    {clipboard && ` | Clipboard: ${clipboard.type} (${formatTime(clipboard.duration)})`}
                  </div>
                </div>
                
                {/* Arrangement Sections Header - Aligned with Waveforms */}
                <div className="flex items-center space-x-2 text-xs">
                  {getArrangementSections().slice(0, 4).map((section, index) => (
                    <div 
                      key={index}
                      className="px-2 py-1 rounded text-white text-xs font-medium"
                      style={{ backgroundColor: section.color, opacity: 0.8 }}
                    >
                      {section.section}
                    </div>
                  ))}
                  {getArrangementSections().length > 4 && (
                    <span className="text-gray-400">+{getArrangementSections().length - 4} more</span>
                  )}
                </div>
              </div>
              
              <div 
                ref={waveformContainerRef}
                className="flex-1 overflow-auto bg-gray-900 relative"
                style={{ width: `${1000 * zoom}px` }}
              >
                {/* Arrangement Sections - Aligned with Waveforms */}
                <div className="absolute top-0 left-0 right-0 h-6 z-10 pointer-events-none">
                  {getArrangementSections().map((section, index) => {
                    const startX = (section.start / duration) * 1000 * zoom;
                    const width = ((section.end - section.start) / duration) * 1000 * zoom;
                    return (
                      <div
                        key={index}
                        className="absolute top-0 h-6 border-r border-gray-500 flex items-center"
                        style={{
                          left: `${startX}px`,
                          width: `${Math.max(width, 40)}px`,
                          backgroundColor: section.color,
                          opacity: 0.8
                        }}
                      >
                        <span className="text-xs text-white font-bold px-2 truncate">
                          {section.section}
                        </span>
                      </div>
                    );
                  })}
                </div>

                {/* Selection overlay */}
                {selectedRegion && (
                  <div
                    className="absolute bg-blue-500 bg-opacity-30 border border-blue-500 z-20 pointer-events-none"
                    style={{
                      left: `${(selectedRegion.start / duration) * 1000 * zoom}px`,
                      width: `${((selectedRegion.end - selectedRegion.start) / duration) * 1000 * zoom}px`,
                      top: '24px', // Start below arrangement sections
                      height: `${tracks.length * 80}px`
                    }}
                  />
                )}
                
                {/* Current drag selection */}
                {isDragging && selectionStart !== null && selectionEnd !== null && (
                  <div
                    className="absolute bg-yellow-500 bg-opacity-20 border border-yellow-500 z-15 pointer-events-none"
                    style={{
                      left: `${(Math.min(selectionStart, selectionEnd) / duration) * 1000 * zoom}px`,
                      width: `${(Math.abs(selectionEnd - selectionStart) / duration) * 1000 * zoom}px`,
                      top: `${24 + selectedTrack * 80}px`, // Account for arrangement sections
                      height: '80px'
                    }}
                  />
                )}
                
                {/* Waveform Tracks - 1:1 Alignment with Mixer */}
                <div className="mt-6"> {/* Space for arrangement sections */}
                  {tracks.map((track, index) => {
                    const waveformData = generateWaveformData(track.id, 1000 * zoom);
                    const isMuted = muteTracks.has(track.id);
                    const isSolo = soloTracks.has(track.id);
                    const isRecording = recordingTracks.has(track.id);
                    
                    // Apply solo logic - if any track is soloed, mute all non-solo tracks
                    const hasSoloTracks = soloTracks.size > 0;
                    const isAudible = !isMuted && (!hasSoloTracks || isSolo);
                    
                    return (
                      <div
                        key={track.id}
                        className={`border-b border-gray-700 relative ${
                          selectedTrack === index ? 'bg-blue-900 bg-opacity-20' : 'hover:bg-gray-800 hover:bg-opacity-30'
                        } ${!isAudible ? 'opacity-50' : ''}`}
                        style={{ height: '80px', minHeight: '80px', maxHeight: '80px' }}
                        onMouseDown={(e) => handleMouseDown(e, index)}
                      >
                        {/* Track Name & Status */}
                        <div className="absolute top-2 left-4 z-10 bg-gray-800 bg-opacity-90 px-2 py-1 rounded text-xs font-medium">
                          <span style={{ color: track.color }}>{track.name}</span>
                          {isMuted && <span className="ml-2 text-red-400 font-bold">[MUTED]</span>}
                          {isSolo && <span className="ml-2 text-yellow-400 font-bold">[SOLO]</span>}
                          {isRecording && <span className="ml-2 text-red-400 font-bold animate-pulse">[REC ●]</span>}
                          {lockedTracks.has(track.id) && <span className="ml-2 text-gray-400">[LOCKED]</span>}
                        </div>
                        
                        {/* Volume/Pan Display */}
                        <div className="absolute top-2 right-4 z-10 bg-gray-800 bg-opacity-90 px-2 py-1 rounded text-xs">
                          <span className="text-blue-300">Vol: {track.volume || 75}</span>
                          <span className="text-orange-300 ml-2">
                            Pan: {track.pan > 0 ? `R${track.pan}` : track.pan < 0 ? `L${Math.abs(track.pan)}` : 'C'}
                          </span>
                        </div>
                        
                        {/* Waveform */}
                        <svg className="w-full h-full" viewBox={`0 0 ${1000 * zoom} 80`}>
                          <defs>
                            <linearGradient id={`gradient-${track.id}`} x1="0%" y1="0%" x2="0%" y2="100%">
                              <stop offset="0%" stopColor={track.color} stopOpacity={isAudible ? "0.8" : "0.3"} />
                              <stop offset="50%" stopColor={track.color} stopOpacity={isAudible ? "0.4" : "0.15"} />
                              <stop offset="100%" stopColor={track.color} stopOpacity={isAudible ? "0.1" : "0.05"} />
                            </linearGradient>
                          </defs>
                          
                          {/* Center line */}
                          <line x1="0" y1="40" x2={1000 * zoom} y2="40" stroke="#374151" strokeWidth="0.5" opacity="0.5" />
                          
                          {/* Waveform - Apply volume scaling */}
                          <path
                            d={`M 0 40 ${waveformData.map((point, i) => {
                              const x = i;
                              const volumeScale = isAudible ? (track.volume || 75) / 100 : 0.1;
                              const y = 40 + (point * 25 * volumeScale);
                              return `L ${x} ${y}`;
                            }).join(' ')}`}
                            fill="none"
                            stroke={track.color}
                            strokeWidth={isAudible ? "1.5" : "0.8"}
                            opacity={isAudible ? "0.8" : "0.3"}
                          />
                          
                          {/* Negative waveform */}
                          <path
                            d={`M 0 40 ${waveformData.map((point, i) => {
                              const x = i;
                              const volumeScale = isAudible ? (track.volume || 75) / 100 : 0.1;
                              const y = 40 - (point * 25 * volumeScale);
                              return `L ${x} ${y}`;
                            }).join(' ')}`}
                            fill="none"
                            stroke={track.color}
                            strokeWidth={isAudible ? "1.5" : "0.8"}
                            opacity={isAudible ? "0.6" : "0.2"}
                          />
                          
                          {/* Filled area */}
                          <path
                            d={`M 0 40 ${waveformData.map((point, i) => {
                              const x = i;
                              const volumeScale = isAudible ? (track.volume || 75) / 100 : 0.1;
                              const y = 40 + (point * 25 * volumeScale);
                              return `L ${x} ${y}`;
                            }).join(' ')} ${waveformData.map((point, i) => {
                              const x = waveformData.length - 1 - i;
                              const volumeScale = isAudible ? (track.volume || 75) / 100 : 0.1;
                              const y = 40 - (point * 25 * volumeScale);
                              return `L ${x} ${y}`;
                            }).reverse().join(' ')} Z`}
                            fill={`url(#gradient-${track.id})`}
                            opacity={isAudible ? "0.3" : "0.1"}
                          />
                          
                          {/* Track regions (cut, copy, paste) */}
                          {(track.regions || []).map((region, regionIndex) => (
                            <rect
                              key={regionIndex}
                              x={(region.start / duration) * 1000 * zoom}
                              y="0"
                              width={((region.end - region.start) / duration) * 1000 * zoom}
                              height="80"
                              fill={region.type === 'cut' ? '#ff0000' : region.type === 'paste' ? '#00ff00' : '#ffff00'}
                              opacity="0.3"
                              stroke={region.type === 'cut' ? '#ff0000' : region.type === 'paste' ? '#00ff00' : '#ffff00'}
                              strokeWidth="1"
                            />
                          ))}
                        </svg>
                        
                        {/* Track Playhead */}
                        <div
                          className="absolute top-0 w-1 h-full bg-red-500 opacity-90 z-10 pointer-events-none"
                          style={{ left: `${(currentTime / duration) * 1000 * zoom}px` }}
                        />
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>"
                          stroke={track.color}
                          strokeWidth="1.5"
                          opacity="0.6"
                        />
                        
                        {/* Filled area */}
                        <path
                          d={`M 0 40 ${waveformData.map((point, i) => {
                            const x = i;
                            const y = 40 + (point * 25);
                            return `L ${x} ${y}`;
                          }).join(' ')} ${waveformData.map((point, i) => {
                            const x = waveformData.length - 1 - i;
                            const y = 40 - (point * 25);
                            return `L ${x} ${y}`;
                          }).reverse().join(' ')} Z`}
                          fill={`url(#gradient-${track.id})`}
                          opacity="0.3"
                        />
                        
                        {/* Track regions (cut, copy, paste) */}
                        {(track.regions || []).map((region, regionIndex) => (
                          <rect
                            key={regionIndex}
                            x={(region.start / duration) * 1000 * zoom}
                            y="0"
                            width={((region.end - region.start) / duration) * 1000 * zoom}
                            height="80"
                            fill={region.type === 'cut' ? '#ff0000' : region.type === 'paste' ? '#00ff00' : '#ffff00'}
                            opacity="0.3"
                            stroke={region.type === 'cut' ? '#ff0000' : region.type === 'paste' ? '#00ff00' : '#ffff00'}
                            strokeWidth="1"
                          />
                        ))}
                      </svg>
                      
                      {/* Track Playhead */}
                      <div
                        className="absolute top-0 w-1 h-full bg-red-500 opacity-90 z-10 pointer-events-none"
                        style={{ left: `${(currentTime / duration) * 1000 * zoom}px` }}
                      />
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Status Bar */}
      <div className="bg-gray-800 border-t border-gray-700 p-3">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center space-x-4">
            <span className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span>Ready for Playback</span>
            </span>
            <span className="text-gray-400">•</span>
            <span>{tracks.length} tracks loaded</span>
            <span className="text-gray-400">•</span>
            <span>Sample Rate: 44.1 kHz</span>
            {selectedRegion && (
              <>
                <span className="text-gray-400">•</span>
                <span className="text-blue-400">Selection: {formatTime(selectedRegion.end - selectedRegion.start)}</span>
              </>
            )}
            {clipboard && (
              <>
                <span className="text-gray-400">•</span>
                <span className="text-green-400">Clipboard: {clipboard.type}</span>
              </>
            )}
          </div>
          
          <div className="flex items-center space-x-4">
            <span className="text-gray-400">CPU: 12%</span>
            <span className="text-gray-400">•</span>
            <span className="text-green-400">Latency: 5.8ms</span>
            <span className="text-gray-400">•</span>
            <span className="text-blue-400">Zoom: {zoom.toFixed(1)}x</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WebDAW;