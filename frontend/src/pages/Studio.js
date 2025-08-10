import React, { useState, useEffect, useRef } from 'react';
import { 
  Upload, Play, Pause, Download, Settings, Share, Eye, 
  Brain, AudioWaveform, Database, Crown, Star, Zap,
  CheckCircle, AlertCircle, Clock, FileAudio, Mic, Target,
  ArrowRight, Lock, Users, TrendingUp, X, Plus, Trash2
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

const Studio = ({ navigateTo }) => {
  const { 
    user, 
    tier, 
    tierConfig, 
    usage, 
    updateUsage, 
    canUseFeature, 
    hasUsageRemaining,
    getUpgradeTarget,
    isAuthenticated 
  } = useAuth();

  // State Management
  const [currentStep, setCurrentStep] = useState('upload'); // upload, analyzing, results
  const [uploadMethod, setUploadMethod] = useState('file');
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [analysisType, setAnalysisType] = useState('pattern');
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [currentJobId, setCurrentJobId] = useState(null);
  const [results, setResults] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  
  const fileInputRef = useRef(null);
  const progressSubscription = useRef(null);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      // Show login modal or redirect
      setError('Please log in to access the Studio');
    }
  }, [isAuthenticated]);

  // Upload Methods based on tier
  const getUploadMethods = () => {
    const methods = [
      {
        id: 'file',
        name: 'Upload Audio Files',
        icon: Upload,
        description: `Upload your drum tracks${tierConfig?.features.batchProcessing ? ' (batch supported)' : ''}`,
        available: true
      },
      {
        id: 'sample',
        name: 'Sample Tracks',
        icon: Database,
        description: 'Try our curated sample tracks',
        available: true
      }
    ];

    if (canUseFeature('signatureSongs')) {
      methods.push({
        id: 'signature',
        name: 'Signature Songs',
        icon: Star,
        description: 'Analyze legendary drummer performances',
        available: true,
        locked: !canUseFeature('signatureSongs')
      });
    }

    if (tier === 'expert') {
      methods.push({
        id: 'record',
        name: 'Live Recording',
        icon: Mic,
        description: 'Record drums directly in browser',
        available: true
      });
    }

    return methods;
  };

  // Analysis Types based on tier
  const getAnalysisTypes = () => {
    const types = [
      {
        id: 'pattern',
        name: 'Pattern Analysis',
        icon: Target,
        description: 'Drum pattern and rhythm recognition',
        available: true,
        sophistication: tierConfig?.sophistication || '65%'
      },
      {
        id: 'tempo',
        name: 'Tempo Analysis',
        icon: Clock,
        description: 'BPM detection and timing analysis',
        available: true,
        sophistication: tierConfig?.sophistication || '65%'
      }
    ];

    if (tier !== 'basic') {
      types.push({
        id: 'style',
        name: 'Style Classification',
        icon: Users,
        description: 'Genre and drummer style recognition',
        available: true,
        sophistication: tierConfig?.sophistication || '82%'
      });
    }

    if (tier === 'expert') {
      types.push({
        id: 'signature',
        name: 'Signature Analysis',
        icon: Crown,
        description: 'Advanced drummer recognition & MVSep',
        available: true,
        sophistication: '88.7%'
      });
    }

    return types;
  };

  // File validation and handling
  const validateFiles = (files) => {
    const errors = [];
    
    for (const file of files) {
      try {
        api.validateUpload(file, tier);
      } catch (error) {
        errors.push(`${file.name}: ${error.message}`);
      }
    }

    // Check usage limits
    if (!hasUsageRemaining()) {
      errors.push('Monthly usage limit reached. Upgrade for unlimited analyses.');
    }

    return errors;
  };

  const handleFileSelect = (event) => {
    const files = Array.from(event.target.files);
    const maxFiles = tierConfig?.features.batchProcessing ? 
      (tierConfig.features.batchLimit === -1 ? 50 : tierConfig.features.batchLimit) : 1;
    
    const selectedFiles = files.slice(0, maxFiles);
    const validationErrors = validateFiles(selectedFiles);
    
    if (validationErrors.length > 0) {
      setError(validationErrors.join('\n'));
      return;
    }
    
    setSelectedFiles(selectedFiles);
    setError(null);
  };

  const removeFile = (index) => {
    const newFiles = selectedFiles.filter((_, i) => i !== index);
    setSelectedFiles(newFiles);
  };

  // Analysis process
  const startAnalysis = async () => {
    if (selectedFiles.length === 0 || !hasUsageRemaining()) return;
    
    try {
      setIsProcessing(true);
      setCurrentStep('analyzing');
      setAnalysisProgress(0);
      setUploadProgress(0);
      setError(null);

      // Upload files with progress tracking
      const uploadPromises = selectedFiles.map(file => 
        api.uploadFile(file, tier, (progress) => {
          setUploadProgress(progress);
        })
      );
      
      const uploadResults = await Promise.all(uploadPromises);
      
      // Start analysis
      const fileIds = uploadResults.map(result => result.file_id);
      
      const jobResult = selectedFiles.length > 1 && canUseFeature('batchProcessing') ?
        await api.startBatchAnalysis(fileIds, analysisType, tier) :
        await api.startAnalysis(fileIds[0], analysisType, tier);

      setCurrentJobId(jobResult.job_id);
      setUploadProgress(100);

      // Subscribe to progress updates
      progressSubscription.current = api.subscribeToProgress(jobResult.job_id, (progressData) => {
        setAnalysisProgress(progressData.progress || 0);
        
        if (progressData.status === 'completed') {
          handleAnalysisComplete(jobResult.job_id);
        } else if (progressData.status === 'failed') {
          setError(progressData.error || 'Analysis failed');
          setIsProcessing(false);
          setCurrentStep('upload');
        }
      });

    } catch (error) {
      setError(error.message);
      setIsProcessing(false);
      setCurrentStep('upload');
    }
  };

  const handleAnalysisComplete = async (jobId) => {
    try {
      const results = await api.getResults(jobId);
      setResults(results);
      setCurrentStep('results');
      setIsProcessing(false);
      
      // Update usage
      await updateUsage();
      
      // Cleanup progress subscription
      if (progressSubscription.current) {
        progressSubscription.current();
        progressSubscription.current = null;
      }
    } catch (error) {
      setError('Failed to retrieve results: ' + error.message);
      setIsProcessing(false);
    }
  };

  const resetStudio = () => {
    setCurrentStep('upload');
    setSelectedFiles([]);
    setResults(null);
    setAnalysisProgress(0);
    setUploadProgress(0);
    setCurrentJobId(null);
    setError(null);
    
    if (progressSubscription.current) {
      progressSubscription.current();
      progressSubscription.current = null;
    }
  };

  // Component: Tier Badge
  const TierBadge = () => (
    <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-semibold ${
      tier === 'expert' ? 'bg-gradient-to-r from-yellow-500 to-orange-500' :
      tier === 'professional' ? 'bg-gradient-to-r from-purple-500 to-purple-600' :
      'bg-gradient-to-r from-blue-500 to-blue-600'
    } text-white`}>
      {tier === 'expert' ? <Crown className="h-4 w-4" /> :
       tier === 'professional' ? <Zap className="h-4 w-4" /> :
       <Star className="h-4 w-4" />}
      {tierConfig?.name} - {tierConfig?.sophistication} AI
    </div>
  );

  // Component: Upgrade Prompt
  const UpgradePrompt = ({ feature, description }) => {
    const targetTier = getUpgradeTarget(feature);
    if (!targetTier) return null;

    return (
      <div className="bg-gradient-to-r from-purple-500/10 to-blue-500/10 border border-purple-500/30 rounded-lg p-4 mb-4">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-white font-semibold mb-1">Unlock {feature}</h4>
            <p className="text-gray-400 text-sm">{description}</p>
          </div>
          <button 
            onClick={() => navigateTo(targetTier)}
            className="px-4 py-2 bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-lg hover:from-purple-600 hover:to-purple-700 transition-colors text-sm flex items-center gap-2"
          >
            Upgrade Now
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      </div>
    );
  };

  // Component: Upload Interface
  const UploadInterface = () => {
    const sampleTracks = [
      { name: 'Basic Rock Beat', bpm: '120', style: 'Rock', duration: '0:30', tier: 'basic' },
      { name: 'Simple Funk Groove', bpm: '95', style: 'Funk', duration: '0:45', tier: 'basic' },
      { name: 'Jazz Swing Pattern', bpm: '140', style: 'Jazz', duration: '0:35', tier: 'basic' },
      { name: 'Complex Fill Pattern', bpm: '130', style: 'Rock', duration: '0:25', tier: 'professional' },
      { name: 'Latin Polyrhythm', bpm: '110', style: 'Latin', duration: '0:40', tier: 'professional' },
      { name: 'Jeff Porcaro Style', bpm: '93', style: 'Pop/Rock', duration: '1:20', tier: 'expert' }
    ];

    const signatureSongs = [
      { name: 'Rosanna', artist: 'Toto', drummer: 'Jeff Porcaro', complexity: 'Expert', duration: '5:30' },
      { name: 'Tom Sawyer', artist: 'Rush', drummer: 'Neil Peart', complexity: 'Master', duration: '4:33' },
      { name: 'Roxanne', artist: 'The Police', drummer: 'Stewart Copeland', complexity: 'Professional', duration: '3:12' }
    ];

    const renderUploadMethod = () => {
      switch (uploadMethod) {
        case 'file':
          return (
            <div className="space-y-6">
              <div 
                className="border-2 border-dashed border-purple-500/50 rounded-xl p-8 text-center hover:border-purple-500 transition-colors cursor-pointer group"
                onClick={() => fileInputRef.current?.click()}
              >
                <Upload className="h-12 w-12 text-purple-400 mx-auto mb-4 group-hover:scale-110 transition-transform" />
                <h3 className="text-xl font-semibold text-white mb-2">
                  {canUseFeature('batchProcessing') ? 'Upload Multiple Files' : 'Upload Audio File'}
                </h3>
                <p className="text-gray-400 mb-4">
                  {canUseFeature('batchProcessing') && tierConfig?.features.batchLimit !== 1
                    ? `Upload up to ${tierConfig.features.batchLimit === -1 ? '50' : tierConfig.features.batchLimit} files for batch processing`
                    : 'Upload your drum track or full song for analysis'
                  }
                </p>
                <div className="text-sm text-gray-500 mb-4">
                  <div>Supported: {tierConfig?.features.supportedFormats.length === 0 ? 'All formats' : 
                    tierConfig.features.supportedFormats.map(f => f.split('/')[1].toUpperCase()).join(', ')}</div>
                  <div>Max size: {tierConfig?.features.maxFileSize === -1 ? 'Unlimited' : 
                    `${tierConfig.features.maxFileSize / 1024 / 1024}MB`}</div>
                </div>
                <button className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors">
                  Choose Files
                </button>
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple={canUseFeature('batchProcessing')}
                  accept={tierConfig?.features.supportedFormats.join(',')}
                  onChange={handleFileSelect}
                  className="hidden"
                />
              </div>
              
              {selectedFiles.length > 0 && (
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <h4 className="text-white font-semibold">
                      Selected Files ({selectedFiles.length})
                    </h4>
                    <span className="text-purple-400 text-sm">
                      Total: {(selectedFiles.reduce((acc, file) => acc + file.size, 0) / 1024 / 1024).toFixed(1)} MB
                    </span>
                  </div>
                  <div className="max-h-60 overflow-y-auto space-y-2">
                    {selectedFiles.map((file, index) => (
                      <div key={index} className="flex items-center justify-between bg-white/5 rounded-lg p-3">
                        <div className="flex items-center gap-3">
                          <FileAudio className="h-5 w-5 text-purple-400" />
                          <span className="text-white">{file.name}</span>
                          <span className="text-gray-400 text-sm">
                            ({(file.size / 1024 / 1024).toFixed(1)} MB)
                          </span>
                        </div>
                        <button 
                          onClick={() => removeFile(index)}
                          className="text-red-400 hover:text-red-300 p-1"
                        >
                          <X className="h-4 w-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );

        case 'sample':
          return (
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-white mb-4">Sample Tracks</h3>
              {sampleTracks.map((track, index) => {
                const tierOrder = { basic: 0, professional: 1, expert: 2 };
                const userTierOrder = tierOrder[tier];
                const trackTierOrder = tierOrder[track.tier];
                const isAvailable = userTierOrder >= trackTierOrder;
                
                return (
                  <div key={index} className={`rounded-lg p-4 ${
                    isAvailable ? 'bg-white/5 hover:bg-white/10 cursor-pointer' : 'bg-gray-800/50 cursor-not-allowed'
                  } transition-colors`}>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                          isAvailable 
                            ? 'bg-gradient-to-r from-blue-500 to-purple-500' 
                            : 'bg-gray-600'
                        }`}>
                          {isAvailable ? (
                            <Database className="h-6 w-6 text-white" />
                          ) : (
                            <Lock className="h-6 w-6 text-gray-400" />
                          )}
                        </div>
                        <div>
                          <h4 className={`font-semibold ${isAvailable ? 'text-white' : 'text-gray-500'}`}>
                            {track.name}
                          </h4>
                          <div className="flex items-center gap-4 text-sm mt-1">
                            <span className={isAvailable ? 'text-gray-400' : 'text-gray-600'}>
                              BPM: {track.bpm}
                            </span>
                            <span className={isAvailable ? 'text-gray-400' : 'text-gray-600'}>
                              Style: {track.style}
                            </span>
                            <span className={isAvailable ? 'text-gray-400' : 'text-gray-600'}>
                              Duration: {track.duration}
                            </span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {isAvailable ? (
                          <>
                            <button className="p-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors">
                              <Play className="h-4 w-4 text-white" />
                            </button>
                            <button 
                              onClick={() => {
                                setSelectedFiles([{ name: track.name, size: 1024 * 1024 }]);
                                setError(null);
                              }}
                              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                            >
                              Select
                            </button>
                          </>
                        ) : (
                          <div className="flex items-center gap-2 text-gray-500 text-sm">
                            <Lock className="h-4 w-4" />
                            <span>{track.tier.charAt(0).toUpperCase() + track.tier.slice(1)} Only</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          );

        case 'signature':
          return (
            <div className="space-y-4">
              {tier === 'professional' && (
                <UpgradePrompt 
                  feature="Full Signature Songs Access" 
                  description="Upgrade to Expert for complete access to all signature songs"
                />
              )}
              
              <h3 className="text-xl font-semibold text-white mb-4">Signature Songs Database</h3>
              {signatureSongs.map((song, index) => {
                const isAvailable = tier === 'expert' || (tier === 'professional' && index === 0);
                
                return (
                  <div key={index} className={`rounded-lg p-4 ${
                    isAvailable ? 'bg-white/5 hover:bg-white/10 cursor-pointer' : 'bg-gray-800/50 cursor-not-allowed'
                  } transition-colors`}>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                          isAvailable 
                            ? 'bg-gradient-to-r from-yellow-500 to-orange-500' 
                            : 'bg-gray-600'
                        }`}>
                          {isAvailable ? (
                            <Star className="h-6 w-6 text-white" />
                          ) : (
                            <Lock className="h-6 w-6 text-gray-400" />
                          )}
                        </div>
                        <div>
                          <h4 className={`font-semibold ${isAvailable ? 'text-white' : 'text-gray-500'}`}>
                            {song.name}
                          </h4>
                          <p className={isAvailable ? 'text-gray-400' : 'text-gray-600'}>
                            {song.artist} • {song.drummer}
                          </p>
                          <div className="flex items-center gap-4 text-sm mt-1">
                            <span className={isAvailable ? 'text-gray-400' : 'text-gray-600'}>
                              Complexity: {song.complexity}
                            </span>
                            <span className={isAvailable ? 'text-gray-400' : 'text-gray-600'}>
                              Duration: {song.duration}
                            </span>
                          </div>
                        </div>
                      </div>
                      <div>
                        {isAvailable ? (
                          <button 
                            onClick={() => {
                              setSelectedFiles([{ name: song.name, size: 5 * 1024 * 1024 }]);
                              setError(null);
                            }}
                            className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors"
                          >
                            Analyze
                          </button>
                        ) : (
                          <div className="flex items-center gap-2 text-gray-500 text-sm">
                            <Lock className="h-4 w-4" />
                            <span>Expert Only</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          );

        case 'record':
          return (
            <div className="text-center space-y-6">
              {tier !== 'expert' && (
                <UpgradePrompt 
                  feature="Live Recording" 
                  description="Upgrade to Expert for live recording capabilities"
                />
              )}
              
              <div className="w-32 h-32 bg-gradient-to-r from-red-500 to-pink-500 rounded-full flex items-center justify-center mx-auto">
                <Mic className="h-16 w-16 text-white" />
              </div>
              <h3 className="text-2xl font-semibold text-white">Live Recording</h3>
              <p className="text-gray-400 max-w-md mx-auto">
                Record your drum performance directly in the browser using your microphone or audio interface.
              </p>
              <div className="flex justify-center gap-4">
                <button 
                  disabled={tier !== 'expert'}
                  className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <div className="w-3 h-3 bg-white rounded-full"></div>
                  Start Recording
                </button>
                <button 
                  disabled={tier !== 'expert'}
                  className="px-6 py-3 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Test Audio
                </button>
              </div>
            </div>
          );

        default:
          return null;
      }
    };

    return (
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Upload Method Selection */}
        <div className="lg:col-span-1">
          <h2 className="text-2xl font-bold text-white mb-6">Input Method</h2>
          <div className="space-y-3">
            {getUploadMethods().map((method) => {
              const Icon = method.icon;
              return (
                <button
                  key={method.id}
                  onClick={() => setUploadMethod(method.id)}
                  disabled={!method.available}
                  className={`w-full p-4 rounded-xl text-left transition-all ${
                    uploadMethod === method.id
                      ? 'bg-gradient-to-r from-purple-500/20 to-blue-500/20 border-2 border-purple-500/50'
                      : 'bg-white/5 hover:bg-white/10 border-2 border-transparent'
                  } ${!method.available ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  <div className="flex items-center gap-3 mb-2">
                    <Icon className={`h-5 w-5 ${uploadMethod === method.id ? 'text-purple-400' : 'text-gray-400'}`} />
                    <span className="text-white font-semibold">{method.name}</span>
                    {method.locked && <Lock className="h-4 w-4 text-gray-500" />}
                  </div>
                  <p className="text-gray-400 text-sm">{method.description}</p>
                </button>
              );
            })}
          </div>

          {/* Analysis Type Selection */}
          <h2 className="text-2xl font-bold text-white mb-6 mt-8">Analysis Type</h2>
          <div className="space-y-3">
            {getAnalysisTypes().map((type) => {
              const Icon = type.icon;
              return (
                <button
                  key={type.id}
                  onClick={() => setAnalysisType(type.id)}
                  className={`w-full p-4 rounded-xl text-left transition-all ${
                    analysisType === type.id
                      ? 'bg-gradient-to-r from-blue-500/20 to-indigo-500/20 border-2 border-blue-500/50'
                      : 'bg-white/5 hover:bg-white/10 border-2 border-transparent'
                  }`}
                >
                  <div className="flex items-center gap-3 mb-2">
                    <Icon className={`h-5 w-5 ${analysisType === type.id ? 'text-blue-400' : 'text-gray-400'}`} />
                    <span className="text-white font-semibold">{type.name}</span>
                  </div>
                  <p className="text-gray-400 text-sm mb-2">{type.description}</p>
                  <div className="text-xs text-blue-300">
                    Sophistication: {type.sophistication}
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Main Content Area */}
        <div className="lg:col-span-2">
          <div className="bg-white/5 backdrop-blur-md rounded-2xl p-8">
            <h2 className="text-2xl font-bold text-white mb-6">
              {getUploadMethods().find(m => m.id === uploadMethod)?.name}
            </h2>
            
            {renderUploadMethod()}

            {/* Analysis Controls */}
            {(selectedFiles.length > 0 || uploadMethod !== 'file') && uploadMethod !== 'record' && (
              <div className="mt-8 pt-8 border-t border-white/20">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Ready for Analysis</h3>
                    <p className="text-gray-400">
                      Using {tierConfig?.name} Model with {getAnalysisTypes().find(t => t.id === analysisType)?.name}
                    </p>
                  </div>
                  <button
                    onClick={startAnalysis}
                    disabled={isProcessing || !hasUsageRemaining() || selectedFiles.length === 0}
                    className="px-8 py-4 bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-xl font-semibold hover:from-purple-600 hover:to-purple-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                  >
                    {isProcessing ? (
                      <>
                        <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        Processing...
                      </>
                    ) : !hasUsageRemaining() ? (
                      <>
                        <Lock className="h-5 w-5" />
                        Limit Reached
                      </>
                    ) : (
                      <>
                        <Brain className="h-5 w-5" />
                        Start Analysis
                      </>
                    )}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  // Component: Analyzing Interface
  const AnalyzingInterface = () => (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white/5 backdrop-blur-md rounded-2xl p-8 text-center">
        <div className="w-20 h-20 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-6">
          <Brain className="h-10 w-10 text-white animate-pulse" />
        </div>
        
        <h2 className="text-3xl font-bold text-white mb-4">
          {tierConfig?.name} Model Processing
        </h2>
        
        <p className="text-gray-300 mb-8">
          Analyzing {selectedFiles.length} file{selectedFiles.length > 1 ? 's' : ''} with {tierConfig?.sophistication} AI sophistication
        </p>

        {/* Upload Progress */}
        {uploadProgress < 100 && (
          <div className="mb-6">
            <div className="flex justify-between text-sm text-gray-400 mb-2">
              <span>Uploading files...</span>
              <span>{uploadProgress.toFixed(1)}%</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-3">
              <div 
                className="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
          </div>
        )}

        {/* Analysis Progress */}
        {uploadProgress >= 100 && (
          <div className="mb-6">
            <div className="flex justify-between text-sm text-gray-400 mb-2">
              <span>{tierConfig?.name} Model Analysis</span>
              <span>{analysisProgress.toFixed(1)}%</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-3">
              <div 
                className="bg-gradient-to-r from-purple-500 to-yellow-500 h-3 rounded-full transition-all duration-300"
                style={{ width: `${analysisProgress}%` }}
              ></div>
            </div>
          </div>
        )}

        {/* Processing Steps */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
          <div className={`p-4 rounded-lg ${uploadProgress >= 100 ? 'bg-green-500/20 border border-green-500/50' : 'bg-white/5'}`}>
            <CheckCircle className={`h-6 w-6 mx-auto mb-2 ${uploadProgress >= 100 ? 'text-green-400' : 'text-gray-500'}`} />
            <p className="text-sm text-white">Upload Complete</p>
          </div>
          <div className={`p-4 rounded-lg ${analysisProgress > 50 ? 'bg-blue-500/20 border border-blue-500/50' : 'bg-white/5'}`}>
            <Brain className={`h-6 w-6 mx-auto mb-2 ${analysisProgress > 50 ? 'text-blue-400 animate-pulse' : 'text-gray-500'}`} />
            <p className="text-sm text-white">AI Analysis</p>
          </div>
          <div className={`p-4 rounded-lg ${analysisProgress >= 100 ? 'bg-purple-500/20 border border-purple-500/50' : 'bg-white/5'}`}>
            <Target className={`h-6 w-6 mx-auto mb-2 ${analysisProgress >= 100 ? 'text-purple-400' : 'text-gray-500'}`} />
            <p className="text-sm text-white">Results Ready</p>
          </div>
        </div>

        <button
          onClick={resetStudio}
          className="mt-8 px-6 py-3 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors"
        >
          Cancel Analysis
        </button>
      </div>
    </div>
  );

  // Component: Results Interface
  const ResultsInterface = () => (
    <div className="max-w-6xl mx-auto">
      <div className="bg-white/5 backdrop-blur-md rounded-2xl p-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
              <CheckCircle className="h-8 w-8 text-green-400" />
              Analysis Complete
            </h2>
            <p className="text-gray-400">
              Processed {selectedFiles.length} file{selectedFiles.length > 1 ? 's' : ''} with {tierConfig?.name} Model
            </p>
          </div>
          <button
            onClick={resetStudio}
            className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            New Analysis
          </button>
        </div>

        {/* Results Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="text-center p-4 bg-white/5 rounded-lg">
            <div className="text-2xl font-bold text-purple-400">{results?.sophistication || '88.7%'}</div>
            <div className="text-gray-400 text-sm">Sophistication</div>
          </div>
          <div className="text-center p-4 bg-white/5 rounded-lg">
            <div className="text-2xl font-bold text-green-400">{results?.accuracy || '94.2%'}</div>
            <div className="text-gray-400 text-sm">Accuracy</div>
          </div>
          <div className="text-center p-4 bg-white/5 rounded-lg">
            <div className="text-2xl font-bold text-blue-400">{results?.tempo || '120 BPM'}</div>
            <div className="text-gray-400 text-sm">Tempo</div>
          </div>
          <div className="text-center p-4 bg-white/5 rounded-lg">
            <div className="text-2xl font-bold text-yellow-400">{results?.confidence || '96.8%'}</div>
            <div className="text-gray-400 text-sm">Confidence</div>
          </div>
        </div>

        {/* Detailed Results */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
          <div>
            <h3 className="text-xl font-semibold text-white mb-4">Analysis Results</h3>
            <div className="space-y-3 bg-black/20 rounded-lg p-4">
              <div className="flex justify-between">
                <span className="text-gray-400">Style:</span>
                <span className="text-white">{results?.drummerStyle || 'Jeff Porcaro Style'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Complexity:</span>
                <span className="text-white">{results?.complexity || 'Expert Level'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Time Signature:</span>
                <span className="text-white">{results?.timeSignature || '4/4'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Fills Detected:</span>
                <span className="text-white">{results?.fills || 12}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Processing Time:</span>
                <span className="text-white">{results?.processingTime || '2m 15s'}</span>
              </div>
            </div>
          </div>
          
          <div>
            <h3 className="text-xl font-semibold text-white mb-4">Detected Patterns</h3>
            <div className="space-y-2 bg-black/20 rounded-lg p-4">
              {(results?.patterns || ['Linear Fill', 'Ghost Notes', 'Hi-hat Work', 'Cross-stick']).map((pattern, index) => (
                <div key={index} className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-400" />
                  <span className="text-gray-300 text-sm">{pattern}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Primary Action - Open WebDAW */}
        <div className="mb-8">
          <button 
            onClick={() => {
              // Navigate to WebDAW with analysis results and audio data
              navigateTo('webdaw', null, { 
                audioAnalysis: results, 
                stemData: selectedFiles,
                analysisType: analysisType 
              });
            }}
            className="w-full px-8 py-4 bg-gradient-to-r from-purple-600 to-purple-700 text-white rounded-xl font-semibold hover:from-purple-700 hover:to-purple-800 transition-all transform hover:scale-105 flex items-center justify-center gap-3 text-lg"
          >
            <AudioWaveform className="h-6 w-6" />
            Open in Professional WebDAW
            <ArrowRight className="h-5 w-5" />
          </button>
          <p className="text-center text-gray-400 text-sm mt-2">
            Edit, enhance, and create with your analyzed drum tracks
          </p>
        </div>

        {/* Export Options */}
        <div className="flex flex-wrap gap-4 mb-8">
          <button className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2">
            <Download className="h-4 w-4" />
            Export JSON
          </button>
          
          {tier !== 'basic' && (
            <button className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2">
              <Eye className="h-4 w-4" />
              View Visualizations
            </button>
          )}
          
          {canUseFeature('apiAccess') && (
            <button className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2">
              <Settings className="h-4 w-4" />
              API Export
            </button>
          )}
          
          <button className="px-6 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors flex items-center gap-2">
            <Share className="h-4 w-4" />
            Share Results
          </button>
        </div>

        {/* Upgrade Prompts for Additional Features */}
        {tier === 'basic' && (
          <div className="space-y-4">
            <UpgradePrompt 
              feature="Advanced Visualizations" 
              description="Upgrade to Professional for 3D waveform analysis and advanced pattern visualization"
            />
          </div>
        )}

        {tier === 'professional' && (
          <div className="space-y-4">
            <UpgradePrompt 
              feature="MVSep Stem Separation" 
              description="Upgrade to Expert for professional stem separation and signature drummer analysis"
            />
          </div>
        )}
      </div>
    </div>
  );

  // Main Render
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen py-20 flex items-center justify-center">
        <div className="text-center max-w-md mx-auto px-4">
          <Lock className="h-16 w-16 text-gray-400 mx-auto mb-6" />
          <h2 className="text-2xl font-bold text-white mb-4">Authentication Required</h2>
          <p className="text-gray-400 mb-6">
            Please log in to access the DrumTracKAI Studio and start analyzing your drum tracks.
          </p>
          <button 
            onClick={() => navigateTo('login')}
            className="px-6 py-3 bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-lg hover:from-purple-600 hover:to-purple-700 transition-colors"
          >
            Log In to Continue
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-20">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-4 mb-6">
            <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-blue-500 rounded-2xl flex items-center justify-center">
              <Brain className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-4xl font-bold text-white">DrumTracKAI Studio</h1>
              <div className="mt-2">
                <TierBadge />
              </div>
            </div>
          </div>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Professional AI-powered drum analysis and pattern recognition. 
            Upload, analyze, and export with {tierConfig?.sophistication} sophistication.
          </p>
          
          {/* Advanced Studio Access Button */}
          {(tier === 'professional' || tier === 'expert') && (
            <div className="mt-6">
              <button
                onClick={() => navigateTo('prostudio')}
                className="px-6 py-3 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-xl font-semibold hover:from-amber-600 hover:to-orange-600 transition-all flex items-center gap-2 mx-auto shadow-lg"
              >
                <Crown className="h-5 w-5" />
                Access Pro Studio Advanced
                <ArrowRight className="h-4 w-4" />
              </button>
              <p className="text-sm text-amber-300 mt-2">
                Advanced DAW-style arrangement editor with comprehensive analysis
              </p>
            </div>
          )}
        </div>

        {/* Usage Indicator for Basic Tier */}
        {tier === 'basic' && (
          <div className="max-w-2xl mx-auto mb-8">
            <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-blue-400 font-semibold">Monthly Usage</span>
                <span className="text-blue-300">{usage?.current || 0}/{usage?.limit || 10} analyses</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-blue-500 to-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${Math.min(((usage?.current || 0) / (usage?.limit || 10)) * 100, 100)}%` }}
                ></div>
              </div>
              {!hasUsageRemaining() && (
                <div className="mt-2 text-yellow-400 text-sm">
                  Monthly limit reached. Upgrade for unlimited analyses.
                </div>
              )}
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="max-w-2xl mx-auto mb-8">
            <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 flex items-center gap-3">
              <AlertCircle className="h-5 w-5 text-red-400 flex-shrink-0" />
              <div>
                <h4 className="text-red-400 font-semibold">Error</h4>
                <p className="text-red-300 text-sm whitespace-pre-line">{error}</p>
              </div>
              <button 
                onClick={() => setError(null)}
                className="ml-auto text-red-400 hover:text-red-300"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
          </div>
        )}

        {/* Main Content Area */}
        <div className="max-w-7xl mx-auto">
          {currentStep === 'upload' && <UploadInterface />}
          {currentStep === 'analyzing' && <AnalyzingInterface />}
          {currentStep === 'results' && <ResultsInterface />}
        </div>

        {/* Feature Showcase */}
        {currentStep === 'upload' && (
          <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            <div className="bg-white/5 backdrop-blur-md rounded-xl p-6 text-center">
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center mx-auto mb-4 ${
                tier === 'expert' ? 'bg-gradient-to-r from-yellow-500 to-orange-500' :
                tier === 'professional' ? 'bg-gradient-to-r from-purple-500 to-purple-600' :
                'bg-gradient-to-r from-blue-500 to-blue-600'
              }`}>
                <Brain className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-3">{tierConfig?.name} AI Model</h3>
              <p className="text-gray-400">
                {tierConfig?.sophistication} sophistication with advanced pattern recognition and analysis capabilities.
              </p>
            </div>
            
            <div className="bg-white/5 backdrop-blur-md rounded-xl p-6 text-center">
              <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-teal-500 rounded-xl flex items-center justify-center mx-auto mb-4">
                <AudioWaveform className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-3">Real-Time Processing</h3>
              <p className="text-gray-400">
                {canUseFeature('realTimeMonitoring') ? 'Live progress monitoring with WebSocket updates' : 'Basic progress tracking with regular updates'}.
              </p>
            </div>
            
            <div className="bg-white/5 backdrop-blur-md rounded-xl p-6 text-center">
              <div className="w-12 h-12 bg-gradient-to-r from-orange-500 to-red-500 rounded-xl flex items-center justify-center mx-auto mb-4">
                <Target className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-3">
                {canUseFeature('batchProcessing') ? 'Batch Processing' : 'Single File Analysis'}
              </h3>
              <p className="text-gray-400">
                {canUseFeature('batchProcessing') 
                  ? `Process up to ${tierConfig?.features.batchLimit === -1 ? 'unlimited' : tierConfig?.features.batchLimit} files simultaneously`
                  : 'Upload and analyze individual drum tracks with precision'
                }.
              </p>
            </div>
          </div>
        )}

        {/* Upgrade CTA */}
        {tier !== 'expert' && currentStep === 'upload' && (
          <div className="mt-16 bg-gradient-to-r from-purple-500/10 to-yellow-500/10 border border-purple-500/30 rounded-2xl p-8 text-center max-w-4xl mx-auto">
            <h2 className="text-2xl font-bold text-white mb-4">
              {tier === 'basic' ? 'Unlock Professional Features' : 'Experience Expert-Level Analysis'}
            </h2>
            <p className="text-gray-300 mb-6">
              {tier === 'basic' 
                ? 'Upgrade to Professional for batch processing, real-time monitoring, and 82% AI sophistication.'
                : 'Upgrade to Expert for 88.7% AI sophistication, MVSep integration, and unlimited processing.'
              }
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              {tier === 'basic' && (
                <button 
                  onClick={() => navigateTo('professional')}
                  className="px-8 py-4 bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-xl font-semibold hover:from-purple-600 hover:to-purple-700 transition-all transform hover:scale-105 flex items-center justify-center gap-2"
                >
                  <Zap className="h-5 w-5" />
                  Upgrade to Professional
                </button>
              )}
              <button 
                onClick={() => navigateTo('expert')}
                className="px-8 py-4 bg-gradient-to-r from-yellow-500 to-orange-500 text-white rounded-xl font-semibold hover:from-yellow-600 hover:to-orange-600 transition-all transform hover:scale-105 flex items-center justify-center gap-2"
              >
                <Crown className="h-5 w-5" />
                {tier === 'basic' ? 'Go Expert' : 'Upgrade to Expert'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Studio; 