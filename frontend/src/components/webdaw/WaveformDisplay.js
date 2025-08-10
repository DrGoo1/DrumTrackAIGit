import React, { useRef, useEffect } from 'react';

const WaveformDisplay = ({ 
  tracks, 
  currentTime, 
  duration, 
  selectedTrack,
  onTrackSelect,
  onTimeSeek 
}) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    drawWaveforms();
  }, [tracks, currentTime, duration, selectedTrack]);

  const drawWaveforms = () => {
    const canvas = canvasRef.current;
    if (!canvas || tracks.length === 0) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    // Clear canvas
    ctx.fillStyle = '#34495e';
    ctx.fillRect(0, 0, width, height);
    
    const trackHeight = height / tracks.length;
    
    tracks.forEach((track, index) => {
      const y = index * trackHeight;
      const centerY = y + trackHeight / 2;
      
      // Draw track background
      ctx.fillStyle = selectedTrack === track.id ? 
        'rgba(52, 152, 219, 0.1)' : 'rgba(52, 73, 94, 0.3)';
      ctx.fillRect(0, y, width, trackHeight);
      
      // Draw track separator
      if (index > 0) {
        ctx.strokeStyle = '#2c3e50';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }
      
      // Draw waveform
      if (track.waveform && track.waveform.length > 0) {
        ctx.strokeStyle = track.color || '#3498db';
        ctx.lineWidth = 1.5;
        ctx.globalAlpha = selectedTrack === track.id ? 1.0 : 0.7;
        
        ctx.beginPath();
        track.waveform.forEach((sample, i) => {
          const x = (i / track.waveform.length) * width;
          const amplitude = sample * (trackHeight / 4);
          
          if (i === 0) {
            ctx.moveTo(x, centerY - amplitude);
          } else {
            ctx.lineTo(x, centerY - amplitude);
          }
        });
        ctx.stroke();
        
        // Draw mirrored waveform
        ctx.beginPath();
        track.waveform.forEach((sample, i) => {
          const x = (i / track.waveform.length) * width;
          const amplitude = sample * (trackHeight / 4);
          
          if (i === 0) {
            ctx.moveTo(x, centerY + amplitude);
          } else {
            ctx.lineTo(x, centerY + amplitude);
          }
        });
        ctx.stroke();
        
        ctx.globalAlpha = 1.0;
      }
      
      // Draw track label
      ctx.fillStyle = track.color || '#ecf0f1';
      ctx.font = '12px Arial';
      ctx.fillText(track.name, 10, y + 20);
    });
    
    // Draw playhead
    if (duration > 0) {
      const playheadX = (currentTime / duration) * width;
      ctx.strokeStyle = '#e74c3c';
      ctx.lineWidth = 2;
      ctx.setLineDash([5, 5]);
      ctx.beginPath();
      ctx.moveTo(playheadX, 0);
      ctx.lineTo(playheadX, height);
      ctx.stroke();
      ctx.setLineDash([]);
    }
  };

  const handleCanvasClick = (e) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    // Determine which track was clicked
    const trackHeight = canvas.height / tracks.length;
    const clickedTrackIndex = Math.floor(y / trackHeight);
    
    if (clickedTrackIndex >= 0 && clickedTrackIndex < tracks.length) {
      const clickedTrack = tracks[clickedTrackIndex];
      onTrackSelect(clickedTrack.id);
    }
    
    // Handle time seeking
    if (duration > 0) {
      const clickTime = (x / canvas.width) * duration;
      onTimeSeek(clickTime);
    }
  };

  return (
    <div className="waveform-display">
      <canvas 
        ref={canvasRef}
        className="waveform-canvas"
        width={800}
        height={300}
        onClick={handleCanvasClick}
      />
      
      {tracks.length === 0 && (
        <div className="no-tracks-message">
          <p>No audio tracks loaded</p>
          <p>Upload audio files or load stems to begin</p>
        </div>
      )}
    </div>
  );
};

export default WaveformDisplay;
