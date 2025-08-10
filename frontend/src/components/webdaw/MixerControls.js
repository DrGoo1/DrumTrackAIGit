import React from 'react';

const MixerChannel = ({ 
  track, 
  channel, 
  levels, 
  onVolumeChange, 
  onPanChange, 
  onMuteToggle, 
  onSoloToggle 
}) => {
  const getLevelColor = (level) => {
    if (level > 0.8) return '#e74c3c';
    if (level > 0.6) return '#f39c12';
    if (level > 0.3) return '#f1c40f';
    return '#27ae60';
  };

  return (
    <div className="mixer-channel">
      <div className="channel-name" style={{ color: track.color }}>
        {track.name}
      </div>
      
      {/* Level meter */}
      <div className="level-meter">
        <div 
          className="level-bar peak"
          style={{ 
            height: `${(levels?.peak || 0) * 100}%`,
            backgroundColor: getLevelColor(levels?.peak || 0)
          }}
        />
        <div 
          className="level-bar rms"
          style={{ 
            height: `${(levels?.rms || 0) * 100}%`,
            backgroundColor: getLevelColor(levels?.rms || 0)
          }}
        />
      </div>
      
      {/* Mute/Solo buttons */}
      <div className="channel-buttons">
        <button 
          className={`btn-small ${channel?.mute ? 'active' : ''}`}
          onClick={onMuteToggle}
          title="Mute"
        >
          M
        </button>
        <button 
          className={`btn-small ${channel?.solo ? 'active' : ''}`}
          onClick={onSoloToggle}
          title="Solo"
        >
          S
        </button>
      </div>
      
      {/* Volume fader */}
      <div className="fader-container">
        <input
          type="range"
          className="volume-fader"
          min="0"
          max="1"
          step="0.01"
          value={channel?.volume || 0.8}
          onChange={(e) => onVolumeChange(parseFloat(e.target.value))}
          orient="vertical"
        />
        <div className="fader-value">
          {Math.round((channel?.volume || 0.8) * 100)}%
        </div>
      </div>
      
      {/* Pan knob */}
      <div className="pan-control">
        <input
          type="range"
          className="pan-knob"
          min="-1"
          max="1"
          step="0.01"
          value={channel?.pan || 0}
          onChange={(e) => onPanChange(parseFloat(e.target.value))}
        />
        <label>Pan</label>
        <div className="pan-value">
          {channel?.pan > 0 ? `R${Math.round(channel.pan * 100)}` : 
           channel?.pan < 0 ? `L${Math.round(Math.abs(channel.pan) * 100)}` : 'C'}
        </div>
      </div>
    </div>
  );
};

const MixerControls = ({ 
  tracks, 
  mixerChannels, 
  levelMeters, 
  masterVolume,
  onChannelUpdate,
  onMasterVolumeChange 
}) => {
  const handleChannelUpdate = (trackId, property, value) => {
    onChannelUpdate(trackId, property, value);
  };

  return (
    <div className="mixer-panel">
      <h3>Mixer</h3>
      
      <div className="mixer-channels">
        {tracks.map(track => {
          const channel = mixerChannels[track.id] || {};
          const levels = levelMeters[track.id] || {};
          
          return (
            <MixerChannel
              key={track.id}
              track={track}
              channel={channel}
              levels={levels}
              onVolumeChange={(value) => handleChannelUpdate(track.id, 'volume', value)}
              onPanChange={(value) => handleChannelUpdate(track.id, 'pan', value)}
              onMuteToggle={() => handleChannelUpdate(track.id, 'mute', !channel.mute)}
              onSoloToggle={() => handleChannelUpdate(track.id, 'solo', !channel.solo)}
            />
          );
        })}
      </div>
      
      {/* Master section */}
      <div className="master-section">
        <h4>Master</h4>
        <div className="master-controls">
          <input
            type="range"
            className="master-fader"
            min="0"
            max="1"
            step="0.01"
            value={masterVolume}
            onChange={(e) => onMasterVolumeChange(parseFloat(e.target.value))}
            orient="vertical"
          />
          <div className="master-value">
            {Math.round(masterVolume * 100)}%
          </div>
        </div>
      </div>
    </div>
  );
};

export default MixerControls;
