import React, { useState } from 'react';

const DrumStudio = ({ 
  selectedDrumKit,
  selectedDrummerStyle,
  humanization,
  tempo,
  onDrumKitChange,
  onDrummerStyleChange,
  onHumanizationChange,
  onCreatePattern
}) => {
  const [isCreating, setIsCreating] = useState(false);

  const drumKits = [
    { id: 'rock', name: 'Rock Kit', description: 'Powerful, punchy drums' },
    { id: 'jazz', name: 'Jazz Kit', description: 'Warm, vintage sound' },
    { id: 'electronic', name: 'Electronic Kit', description: 'Modern, synthetic drums' },
    { id: 'vintage', name: 'Vintage Kit', description: 'Classic 70s sound' }
  ];

  const drummerStyles = [
    { 
      id: 'bonham', 
      name: 'John Bonham', 
      description: 'Powerful, behind-the-beat style with signature triplets',
      characteristics: ['Heavy kick', 'Triplet fills', 'Behind the beat']
    },
    { 
      id: 'peart', 
      name: 'Neil Peart', 
      description: 'Complex, precise progressive drumming',
      characteristics: ['Complex fills', 'Odd time signatures', 'Technical precision']
    },
    { 
      id: 'copeland', 
      name: 'Stewart Copeland', 
      description: 'Reggae-influenced, hi-hat focused style',
      characteristics: ['Hi-hat emphasis', 'Reggae influence', 'Syncopated rhythms']
    }
  ];

  const handleCreatePattern = async () => {
    setIsCreating(true);
    try {
      await onCreatePattern();
    } finally {
      setIsCreating(false);
    }
  };

  const handleHumanizationChange = (property, value) => {
    onHumanizationChange({
      ...humanization,
      [property]: value
    });
  };

  return (
    <div className="drum-studio-panel">
      <h3>Drum Studio</h3>
      
      {/* Drum Kit Selector */}
      <div className="drum-kit-section">
        <h4>Drum Kit</h4>
        <div className="kit-selector">
          {drumKits.map(kit => (
            <div 
              key={kit.id}
              className={`kit-option ${selectedDrumKit === kit.id ? 'selected' : ''}`}
              onClick={() => onDrumKitChange(kit.id)}
            >
              <div className="kit-name">{kit.name}</div>
              <div className="kit-description">{kit.description}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Drummer Style Selector */}
      <div className="drummer-style-section">
        <h4>Drummer Style</h4>
        <div className="style-selector">
          {drummerStyles.map(style => (
            <div 
              key={style.id}
              className={`style-option ${selectedDrummerStyle === style.id ? 'selected' : ''}`}
              onClick={() => onDrummerStyleChange(style.id)}
            >
              <div className="style-name">{style.name}</div>
              <div className="style-description">{style.description}</div>
              <div className="style-characteristics">
                {style.characteristics.map((char, index) => (
                  <span key={index} className="characteristic-tag">
                    {char}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Humanization Controls */}
      <div className="humanization-section">
        <h4>Humanization</h4>
        
        <div className="humanization-controls">
          <div className="control-group">
            <label>Timing Variation</label>
            <div className="control-input">
              <input
                type="range"
                min="0"
                max="0.1"
                step="0.001"
                value={humanization.timing}
                onChange={(e) => handleHumanizationChange('timing', parseFloat(e.target.value))}
              />
              <span className="control-value">
                {Math.round(humanization.timing * 1000)}ms
              </span>
            </div>
            <div className="control-description">
              Natural timing drift and imperfection
            </div>
          </div>
          
          <div className="control-group">
            <label>Velocity Variation</label>
            <div className="control-input">
              <input
                type="range"
                min="0"
                max="0.3"
                step="0.01"
                value={humanization.velocity}
                onChange={(e) => handleHumanizationChange('velocity', parseFloat(e.target.value))}
              />
              <span className="control-value">
                {Math.round(humanization.velocity * 100)}%
              </span>
            </div>
            <div className="control-description">
              Dynamic range and accent variation
            </div>
          </div>
          
          <div className="control-group">
            <label>Groove Intensity</label>
            <div className="control-input">
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={humanization.groove}
                onChange={(e) => handleHumanizationChange('groove', parseFloat(e.target.value))}
              />
              <span className="control-value">
                {Math.round(humanization.groove * 100)}%
              </span>
            </div>
            <div className="control-description">
              Swing feel and rhythmic emphasis
            </div>
          </div>
        </div>
      </div>

      {/* Pattern Creation */}
      <div className="pattern-creation-section">
        <h4>Pattern Creation</h4>
        
        <div className="pattern-info">
          <div className="info-item">
            <label>Tempo:</label>
            <span>{tempo} BPM</span>
          </div>
          <div className="info-item">
            <label>Kit:</label>
            <span>{drumKits.find(k => k.id === selectedDrumKit)?.name}</span>
          </div>
          <div className="info-item">
            <label>Style:</label>
            <span>{drummerStyles.find(s => s.id === selectedDrummerStyle)?.name}</span>
          </div>
        </div>
        
        <button 
          className={`btn-primary create-pattern-btn ${isCreating ? 'creating' : ''}`}
          onClick={handleCreatePattern}
          disabled={isCreating}
        >
          {isCreating ? (
            <>
              <span className="spinner"></span>
              Creating Pattern...
            </>
          ) : (
            'Create Drum Pattern'
          )}
        </button>
      </div>

      {/* Advanced Options */}
      <div className="advanced-options-section">
        <h4>Advanced Options</h4>
        
        <div className="option-group">
          <label>
            <input type="checkbox" />
            Ghost Notes
          </label>
          <div className="option-description">
            Add subtle snare ghost notes for groove
          </div>
        </div>
        
        <div className="option-group">
          <label>
            <input type="checkbox" />
            Flam Techniques
          </label>
          <div className="option-description">
            Include flam rudiments and accents
          </div>
        </div>
        
        <div className="option-group">
          <label>
            <input type="checkbox" />
            Fill Variations
          </label>
          <div className="option-description">
            Generate automatic fill patterns
          </div>
        </div>
      </div>
    </div>
  );
};

export default DrumStudio;
