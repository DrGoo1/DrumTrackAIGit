import React, { useState } from 'react';

const ExportDialog = ({ 
  isOpen, 
  onClose, 
  onExport,
  isExporting = false 
}) => {
  const [exportSettings, setExportSettings] = useState({
    format: 'wav',
    quality: 'high',
    sampleRate: 44100,
    bitDepth: 16,
    includeStems: false,
    normalizeAudio: true
  });

  const formatOptions = [
    { value: 'wav', label: 'WAV (Uncompressed)', description: 'Best quality, larger file size' },
    { value: 'mp3', label: 'MP3 (320kbps)', description: 'Good quality, smaller file size' },
    { value: 'flac', label: 'FLAC (Lossless)', description: 'Lossless compression' },
    { value: 'aiff', label: 'AIFF (Uncompressed)', description: 'Apple format, high quality' }
  ];

  const qualityOptions = [
    { value: 'high', label: 'High Quality', sampleRate: 48000, bitDepth: 24 },
    { value: 'standard', label: 'Standard Quality', sampleRate: 44100, bitDepth: 16 },
    { value: 'web', label: 'Web Quality', sampleRate: 44100, bitDepth: 16 }
  ];

  const handleSettingChange = (key, value) => {
    setExportSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleQualityChange = (qualityKey) => {
    const quality = qualityOptions.find(q => q.value === qualityKey);
    setExportSettings(prev => ({
      ...prev,
      quality: qualityKey,
      sampleRate: quality.sampleRate,
      bitDepth: quality.bitDepth
    }));
  };

  const handleExport = () => {
    onExport(exportSettings);
  };

  const getEstimatedFileSize = () => {
    // Rough estimation based on format and quality
    const duration = 180; // Assume 3 minutes for estimation
    let sizeMB = 0;
    
    switch (exportSettings.format) {
      case 'wav':
      case 'aiff':
        sizeMB = (exportSettings.sampleRate * exportSettings.bitDepth * 2 * duration) / (8 * 1024 * 1024);
        break;
      case 'flac':
        sizeMB = (exportSettings.sampleRate * exportSettings.bitDepth * 2 * duration) / (8 * 1024 * 1024) * 0.6;
        break;
      case 'mp3':
        sizeMB = (320 * duration) / (8 * 1024);
        break;
      default:
        sizeMB = 30;
    }
    
    return Math.round(sizeMB * 10) / 10;
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="export-dialog">
        <div className="dialog-header">
          <h3>Export Audio</h3>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        <div className="dialog-content">
          {/* Format Selection */}
          <div className="setting-group">
            <label>Audio Format</label>
            <div className="format-options">
              {formatOptions.map(format => (
                <div 
                  key={format.value}
                  className={`format-option ${exportSettings.format === format.value ? 'selected' : ''}`}
                  onClick={() => handleSettingChange('format', format.value)}
                >
                  <div className="format-label">{format.label}</div>
                  <div className="format-description">{format.description}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Quality Selection */}
          <div className="setting-group">
            <label>Quality</label>
            <div className="quality-options">
              {qualityOptions.map(quality => (
                <div 
                  key={quality.value}
                  className={`quality-option ${exportSettings.quality === quality.value ? 'selected' : ''}`}
                  onClick={() => handleQualityChange(quality.value)}
                >
                  <div className="quality-label">{quality.label}</div>
                  <div className="quality-specs">
                    {quality.sampleRate / 1000}kHz / {quality.bitDepth}-bit
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Advanced Options */}
          <div className="setting-group">
            <label>Advanced Options</label>
            <div className="advanced-options">
              <div className="option-item">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={exportSettings.includeStems}
                    onChange={(e) => handleSettingChange('includeStems', e.target.checked)}
                  />
                  Export Individual Stems
                </label>
                <div className="option-description">
                  Export each track as a separate file
                </div>
              </div>
              
              <div className="option-item">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={exportSettings.normalizeAudio}
                    onChange={(e) => handleSettingChange('normalizeAudio', e.target.checked)}
                  />
                  Normalize Audio
                </label>
                <div className="option-description">
                  Optimize volume levels for consistent output
                </div>
              </div>
            </div>
          </div>

          {/* Export Info */}
          <div className="export-info">
            <div className="info-item">
              <span className="info-label">Estimated File Size:</span>
              <span className="info-value">{getEstimatedFileSize()} MB</span>
            </div>
            <div className="info-item">
              <span className="info-label">Sample Rate:</span>
              <span className="info-value">{exportSettings.sampleRate / 1000}kHz</span>
            </div>
            <div className="info-item">
              <span className="info-label">Bit Depth:</span>
              <span className="info-value">{exportSettings.bitDepth}-bit</span>
            </div>
          </div>
        </div>
        
        <div className="dialog-footer">
          <button 
            className="btn-secondary" 
            onClick={onClose}
            disabled={isExporting}
          >
            Cancel
          </button>
          <button 
            className="btn-primary export-btn"
            onClick={handleExport}
            disabled={isExporting}
          >
            {isExporting ? (
              <>
                <span className="spinner"></span>
                Exporting...
              </>
            ) : (
              'Export Audio'
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ExportDialog;
