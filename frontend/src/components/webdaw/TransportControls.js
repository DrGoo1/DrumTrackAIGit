import React, { useState, useRef, useEffect } from 'react';

const TransportControls = ({ 
  isPlaying, 
  isRecording, 
  currentTime, 
  duration, 
  tempo,
  onPlay, 
  onPause, 
  onStop, 
  onRecord, 
  onSeek,
  onTempoChange 
}) => {
  const timelineCanvasRef = useRef(null);

  useEffect(() => {
    drawTimeline();
  }, [currentTime, duration]);

  const drawTimeline = () => {
    const canvas = timelineCanvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    // Clear canvas
    ctx.fillStyle = '#2c3e50';
    ctx.fillRect(0, 0, width, height);
    
    if (duration > 0) {
      // Draw time rulers
      ctx.strokeStyle = '#34495e';
      ctx.lineWidth = 1;
      
      const pixelsPerSecond = width / duration;
      for (let i = 0; i < duration; i++) {
        const x = i * pixelsPerSecond;
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
      }
      
      // Draw playhead
      const playheadX = (currentTime / duration) * width;
      ctx.strokeStyle = '#e74c3c';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(playheadX, 0);
      ctx.lineTo(playheadX, height);
      ctx.stroke();
    }
  };

  const handleTimelineClick = (e) => {
    if (duration === 0) return;
    
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const position = (x / rect.width) * duration;
    onSeek(position);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="transport-section">
      <div className="transport-controls">
        <button 
          className={`transport-btn ${isRecording ? 'recording' : ''}`}
          onClick={onRecord}
          title="Record"
        >
          ⏺
        </button>
        <button 
          className="transport-btn" 
          onClick={onStop}
          title="Stop"
        >
          ⏹
        </button>
        <button 
          className="transport-btn" 
          onClick={isPlaying ? onPause : onPlay}
          title={isPlaying ? "Pause" : "Play"}
        >
          {isPlaying ? '⏸' : '▶'}
        </button>
      </div>
      
      <div className="timeline-container">
        <canvas 
          ref={timelineCanvasRef}
          className="timeline-canvas"
          width={800}
          height={60}
          onClick={handleTimelineClick}
        />
        <div className="time-display">
          {formatTime(currentTime)} / {formatTime(duration)}
        </div>
      </div>
      
      <div className="tempo-display">
        <label>Tempo:</label>
        <input 
          type="number" 
          value={tempo} 
          onChange={(e) => onTempoChange(parseInt(e.target.value))}
          min="60" 
          max="200"
        />
        <span>BPM</span>
      </div>
    </div>
  );
};

export default TransportControls;
