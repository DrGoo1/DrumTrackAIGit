import React from 'react';

const TrackItem = ({ 
  track, 
  isSelected, 
  channel,
  onSelect, 
  onMute, 
  onSolo,
  onDelete 
}) => {
  return (
    <div 
      className={`track-item ${isSelected ? 'selected' : ''}`}
      onClick={() => onSelect(track.id)}
    >
      <div className="track-info">
        <div className="track-color" style={{ backgroundColor: track.color }}></div>
        <div className="track-details">
          <div className="track-name">{track.name}</div>
          <div className="track-type">{track.type}</div>
        </div>
      </div>
      
      <div className="track-controls">
        <button 
          className={`btn-small ${channel?.mute ? 'active' : ''}`}
          onClick={(e) => {
            e.stopPropagation();
            onMute(track.id);
          }}
          title="Mute"
        >
          M
        </button>
        <button 
          className={`btn-small ${channel?.solo ? 'active' : ''}`}
          onClick={(e) => {
            e.stopPropagation();
            onSolo(track.id);
          }}
          title="Solo"
        >
          S
        </button>
        <button 
          className="btn-small delete-btn"
          onClick={(e) => {
            e.stopPropagation();
            onDelete(track.id);
          }}
          title="Delete Track"
        >
          ×
        </button>
      </div>
    </div>
  );
};

const TrackList = ({ 
  tracks, 
  selectedTrack, 
  mixerChannels,
  onTrackSelect,
  onTrackMute,
  onTrackSolo,
  onTrackDelete,
  onAddTrack 
}) => {
  return (
    <div className="track-list">
      <div className="track-list-header">
        <h4>Tracks</h4>
        <button 
          className="btn-primary add-track-btn"
          onClick={onAddTrack}
          title="Add Track"
        >
          + Add Track
        </button>
      </div>
      
      <div className="track-items">
        {tracks.length === 0 ? (
          <div className="no-tracks">
            <p>No tracks loaded</p>
            <button className="btn-secondary" onClick={onAddTrack}>
              Add Your First Track
            </button>
          </div>
        ) : (
          tracks.map(track => (
            <TrackItem
              key={track.id}
              track={track}
              isSelected={selectedTrack === track.id}
              channel={mixerChannels[track.id]}
              onSelect={onTrackSelect}
              onMute={onTrackMute}
              onSolo={onTrackSolo}
              onDelete={onTrackDelete}
            />
          ))
        )}
      </div>
    </div>
  );
};

export default TrackList;
