import React, { useState, useEffect } from 'react';
import WebDAWReal from '../components/WebDAWReal';

const WebDAWTest = () => {
  // Simulate cached stem data that would come from the backend
  const testStemData = {
    bass: {
      name: 'bass.wav',
      path: 'd:/DrumTracKAI_v1.1.10/audio_cache/stems/e51f9193-c73e-4684-b51b-5b57fa2daafb/bass.wav',
      size: '21.2 MB',
      audioData: 'simulated_bass_audio_data',
      type: 'bass'
    },
    drums: {
      name: 'drums_composite.wav',
      audioData: 'simulated_drums_audio_data',
      type: 'drums'
    },
    vocals: {
      name: 'vocals_extracted.wav',
      audioData: 'simulated_vocals_audio_data',
      type: 'vocals'
    },
    other: {
      name: 'other_instruments.wav',
      audioData: 'simulated_other_audio_data',
      type: 'other'
    }
  };

  // Simulate audio analysis data
  const testAudioAnalysis = {
    tempo: 128,
    key: 'G Major',
    time_signature: '4/4',
    sophistication: '88.7%',
    confidence: '96.8%',
    style: {
      primary: 'Alternative Rock',
      secondary: 'Indie Pop',
      confidence: 0.87
    },
    instruments: [
      {
        name: 'Kick Drum',
        confidence: 0.95,
        prominence: 0.8
      },
      {
        name: 'Snare Drum',
        confidence: 0.92,
        prominence: 0.75
      },
      {
        name: 'Hi-Hat',
        confidence: 0.89,
        prominence: 0.65
      }
    ]
  };

  const handleBack = () => {
    console.log('Back button clicked');
    // In a real app, this would navigate back
    window.history.back();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 p-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button 
              onClick={handleBack}
              className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded text-white text-sm font-medium"
            >
              ← Back to Studio
            </button>
            <div>
              <h1 className="text-2xl font-bold text-white">WebDAW Stem Upload Test</h1>
              <p className="text-gray-400">Testing cached audio stem upload functionality</p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-400">Test Mode</div>
            <div className="text-lg font-bold text-purple-400">
              {Object.keys(testStemData).length} Stems Loaded
            </div>
          </div>
        </div>
      </div>

      {/* Stem Data Info Panel */}
      <div className="bg-gray-900 border-b border-gray-700 p-4">
        <div className="max-w-7xl mx-auto">
          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-lg font-bold text-yellow-400 mb-3">📁 Loaded Stem Data:</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {Object.entries(testStemData).map(([stemType, stemInfo]) => (
                <div key={stemType} className="bg-gray-700 rounded-lg p-3">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    <span className="font-bold text-white capitalize">{stemType}</span>
                  </div>
                  <div className="text-sm text-gray-300">
                    <div>📄 {stemInfo.name}</div>
                    {stemInfo.size && <div>💾 {stemInfo.size}</div>}
                    <div>🎵 Type: {stemInfo.type}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* WebDAW Component with Test Data */}
      <WebDAW 
        audioAnalysis={testAudioAnalysis}
        stemData={testStemData}
        analysisType="comprehensive"
        onBack={handleBack}
      />
    </div>
  );
};

export default WebDAWTest;
