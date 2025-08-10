# DrumTracKAI v1.1.7 - Analysis Methods Setup Guide

## [DRUMS] Advanced Drummer Analysis System

This guide covers the setup and usage of both standard and GPU-accelerated TFR (Time-Frequency Reassignment) analysis methods in DrumTracKAI v1.1.7.

---

## [CLIPBOARD] Table of Contents

1. [System Overview](#system-overview)
2. [Environment Setup](#environment-setup)
3. [Standard Analysis Method](#standard-analysis-method)
4. [GPU-Accelerated TFR Analysis](#gpu-accelerated-tfr-analysis)
5. [Analysis Comparison Tools](#analysis-comparison-tools)
6. [Troubleshooting](#troubleshooting)
7. [File Structure](#file-structure)
8. [Usage Examples](#usage-examples)

---

## [TARGET] System Overview

DrumTracKAI v1.1.7 provides two sophisticated analysis methods:

### **Standard Analysis**
- **Technology**: librosa-based onset detection and tempo analysis
- **Precision**: Millisecond-level timing accuracy
- **Environment**: Standard Python environment with audio processing libraries
- **Use Case**: General drummer analysis and profiling

### **GPU-Accelerated TFR Analysis**
- **Technology**: Time-Frequency Reassignment with GPU acceleration
- **Precision**: Sub-millisecond timing accuracy
- **Environment**: Specialized `testgpu` conda environment with LLVM-safe configuration
- **Use Case**: High-precision drummer analysis and research applications

---

## [TOOLS] Environment Setup

### Prerequisites

1. **Hardware Requirements**:
   - CUDA-compatible GPU (recommended: NVIDIA GeForce RTX 3070 or better)
   - 16GB+ RAM
   - 50GB+ free disk space

2. **Software Requirements**:
   - Anaconda or Miniconda
   - Python 3.8+
   - CUDA Toolkit (for GPU acceleration)

### Standard Environment Setup

```bash
# Create standard environment
conda create -n drumtrackai python=3.8
conda activate drumtrackai

# Install core dependencies
pip install librosa soundfile numpy scipy matplotlib seaborn pandas
pip install PySide6 requests aiohttp python-dotenv
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### GPU-Accelerated TFR Environment Setup

```bash
# Create specialized testgpu environment
conda create -n testgpu python=3.8
conda activate testgpu

# Install GPU-accelerated dependencies
pip install librosa soundfile numpy scipy matplotlib seaborn pandas
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install numba cupy-cuda11x

# Set LLVM-safe environment variables (CRITICAL)
conda env config vars set NUMBA_DISABLE_INTEL_SVML=1
conda env config vars set OMP_NUM_THREADS=1
conda env config vars set MKL_NUM_THREADS=1

# Reactivate environment to apply variables
conda deactivate
conda activate testgpu

# Verify GPU availability
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
python -c "import torch; print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')"
```

### Environment Variables Verification

```bash
# In testgpu environment, verify LLVM-safe settings
echo $NUMBA_DISABLE_INTEL_SVML  # Should output: 1
echo $OMP_NUM_THREADS           # Should output: 1
echo $MKL_NUM_THREADS           # Should output: 1
```

---

## [BAR_CHART] Standard Analysis Method

### Setup and Usage

1. **Activate Environment**:
   ```bash
   conda activate drumtrackai
   ```

2. **Run Standard Analysis**:
   ```python
   # Example: Standard drummer analysis
   from admin.services.drumtrackai_complete_system import DrumTracKAICompleteSystem
   
   analyzer = DrumTracKAICompleteSystem()
   results = analyzer.analyze_drummer_performance(
       drummer_name="Jeff Porcaro",
       song_title="Rosanna",
       audio_files={
           'kick': 'path/to/kick.wav',
           'snare': 'path/to/snare.wav',
           # ... other stems
       }
   )
   ```

3. **Expected Output**:
   - Timing precision: ~0.863
   - Bass integration: ~0.079
   - Dynamic consistency: ~0.807
   - Pattern complexity: ~1.000
   - Overall groove score: ~0.82

### Features
- [SUCCESS] Real-time analysis capability
- [SUCCESS] Standard librosa-based processing
- [SUCCESS] Compatible with most systems
- [SUCCESS] Integrated with DrumTracKAI UI

---

## [LAUNCH] GPU-Accelerated TFR Analysis

### Setup and Usage

1. **Activate TFR Environment**:
   ```bash
   conda activate testgpu
   
   # Verify environment variables are set
   python -c "import os; print('LLVM Safe:', os.getenv('NUMBA_DISABLE_INTEL_SVML'))"
   ```

2. **Prepare Audio Files**:
   ```bash
   # Ensure drum stems are available
   ls -la *.wav  # Should show kick.wav, snare.wav, etc.
   ```

3. **Run TFR Analysis**:
   ```bash
   python run_tfr_analysis.py
   ```

4. **Expected Output**:
   ```
   [LAUNCH] Starting GPU-Accelerated TFR Analysis...
   GPU Device: NVIDIA GeForce RTX 3070
   Analysis Time: ~65 seconds
   Output: gpu_tfr_rosanna_results.json
   ```

### TFR Analysis Features
- [SUCCESS] Sub-millisecond timing precision
- [SUCCESS] GPU acceleration (65s analysis time)
- [SUCCESS] Enhanced onset detection
- [SUCCESS] Spectral evolution analysis
- [SUCCESS] Comprehensive frequency content analysis
- [SUCCESS] Authenticity validation (no placeholder data)

### TFR Output Structure
```json
{
  "drummer": "Jeff Porcaro",
  "song": "Rosanna",
  "analysis_type": "GPU_Accelerated_TFR_Enhanced",
  "timestamp": "2025-07-20T21:14:54.317249",
  "gpu_info": {
    "gpu_used": true,
    "gpu_name": "NVIDIA GeForce RTX 3070",
    "analysis_time_seconds": 65.17
  },
  "tfr_enhanced_results": {
    "kick": {
      "enhanced_hits": [
        {
          "timestamp": 0.6501587301587302,
          "velocity": 0.18365290760993958,
          "drum_type": "kick",
          "frequency_content": [3.94, 16.32, ...]
        }
      ]
    }
  }
}
```

---

## [TRENDING_UP] Analysis Comparison Tools

### 1. Results Analyzer and Visualizer

```bash
# Run comprehensive analysis comparison
python tfr_results_analyzer_and_visualizer.py
```

**Output**:
- `tfr_visualizations/tfr_comprehensive_analysis.png` - Publication-quality charts
- `tfr_visualizations/tfr_analysis_report.txt` - Detailed text report

### 2. Comparison Interpreter

```bash
# Run detailed interpretation
python tfr_comparison_interpretation.py
```

**Features**:
- Technical insights into TFR enhancements
- Drummer profile insights
- Comprehensive conclusion and assessment
- Human-readable interpretation

### Visualization Components

1. **Metrics Comparison Bar Chart**: Side-by-side metric comparison
2. **Improvement Percentage Chart**: Shows percentage improvements
3. **Analysis Quality Dashboard**: GPU info and summary statistics
4. **Drum Stem Analysis Overview**: Hit detection by stem
5. **Timing Precision Analysis**: Distribution analysis
6. **Overall Performance Radar Chart**: 360° comparison view

---

## [CONFIG] Troubleshooting

### Common Issues and Solutions

#### 1. LLVM Runtime Errors
```
Symbol not found: __svml_cosf8_ha
```
**Solution**:
```bash
conda activate testgpu
conda env config vars set NUMBA_DISABLE_INTEL_SVML=1
conda env config vars set OMP_NUM_THREADS=1
conda env config vars set MKL_NUM_THREADS=1
conda deactivate
conda activate testgpu
```

#### 2. GPU Not Detected
```python
# Check GPU availability
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU count: {torch.cuda.device_count()}")
```
**Solution**: Install CUDA Toolkit and compatible PyTorch version

#### 3. Audio File Issues
```
FileNotFoundError: Audio file not found
```
**Solution**: Ensure drum stems are in the correct directory with proper naming

#### 4. Memory Issues
```
CUDA out of memory
```
**Solution**: Reduce batch size or use CPU fallback for large files

### Environment Validation Script

```python
#!/usr/bin/env python3
"""Environment validation script"""

import os
import torch
import librosa
import numpy as np

def validate_environment():
    print("[SEARCH] Environment Validation")
    print("=" * 40)
    
    # Check LLVM settings
    llvm_safe = os.getenv('NUMBA_DISABLE_INTEL_SVML') == '1'
    omp_threads = os.getenv('OMP_NUM_THREADS') == '1'
    mkl_threads = os.getenv('MKL_NUM_THREADS') == '1'
    
    print(f"LLVM Safe: {'[SUCCESS]' if llvm_safe else ''}")
    print(f"OMP Threads: {'[SUCCESS]' if omp_threads else ''}")
    print(f"MKL Threads: {'[SUCCESS]' if mkl_threads else ''}")
    
    # Check GPU
    cuda_available = torch.cuda.is_available()
    print(f"CUDA Available: {'[SUCCESS]' if cuda_available else ''}")
    
    if cuda_available:
        gpu_name = torch.cuda.get_device_name(0)
        print(f"GPU: {gpu_name}")
    
    # Test librosa import
    try:
        y, sr = librosa.load(librosa.ex('choice'), duration=1)
        print("Librosa: [SUCCESS]")
    except Exception as e:
        print(f"Librosa:  {e}")
    
    print("=" * 40)
    return llvm_safe and omp_threads and mkl_threads

if __name__ == "__main__":
    validate_environment()
```

---

## [FOLDER] File Structure

```
D:/DrumTracKAI_v1.1.10\
 README_Analysis_Methods.md              # This guide
 docs/
    Memories.md                         # System memory and insights
 run_tfr_analysis.py                     # Main TFR analysis script
 tfr_results_analyzer_and_visualizer.py # Results analysis tool
 tfr_comparison_interpretation.py        # Interpretation system
 gpu_tfr_rosanna_results.json           # TFR analysis results
 tfr_visualizations/                     # Generated visualizations
    tfr_comprehensive_analysis.png      # Main visualization
    tfr_analysis_report.txt            # Detailed report
 admin/
    services/
       drumtrackai_complete_system.py  # Standard analysis
       mvsep_service.py               # Stem separation
    ui/
        main_window.py                 # Main application
        drummers_widget.py             # Drummer management
 test_scripts/                          # Validation scripts
     validate_environment.py            # Environment checker
     test_complete_system_integration.py # Integration tests
```

---

## [IDEA] Usage Examples

### Example 1: Complete Analysis Workflow

```bash
# 1. Setup environment
conda activate testgpu

# 2. Validate environment
python validate_environment.py

# 3. Run TFR analysis
python run_tfr_analysis.py

# 4. Generate comparison
python tfr_results_analyzer_and_visualizer.py

# 5. Get interpretation
python tfr_comparison_interpretation.py
```

### Example 2: Quick Standard Analysis

```bash
# 1. Activate standard environment
conda activate drumtrackai

# 2. Run DrumTracKAI application
python admin/ui/main_window.py

# 3. Use UI for drummer analysis
# - Select drummer (e.g., Jeff Porcaro)
# - Choose signature song (e.g., Rosanna)
# - Run analysis through UI
```

### Example 3: Batch Processing

```python
# Batch analysis of multiple drummers
drummers = ["Jeff Porcaro", "John Bonham", "Neil Peart"]

for drummer in drummers:
    # Run TFR analysis
    results = run_tfr_analysis(drummer)
    
    # Generate comparison
    comparison = analyze_and_visualize(results)
    
    # Save results
    save_analysis_results(drummer, comparison)
```

---

## [TARGET] Performance Benchmarks

### Standard Analysis
- **Analysis Time**: ~30-60 seconds per song
- **Precision**: Millisecond-level timing
- **Memory Usage**: ~2-4GB RAM
- **CPU Usage**: High during analysis

### TFR Analysis
- **Analysis Time**: ~65 seconds per song (GPU-accelerated)
- **Precision**: Sub-millisecond timing
- **Memory Usage**: ~4-8GB RAM + 2-4GB GPU
- **GPU Usage**: High during analysis

### Comparison Results (Jeff Porcaro - "Rosanna")
| Metric | Standard | TFR Enhanced | Improvement |
|--------|----------|--------------|-------------|
| Timing Precision | 0.863 | Enhanced | Sub-ms accuracy |
| Bass Integration | 0.079 | Enhanced | Frequency analysis |
| Dynamic Consistency | 0.807 | Enhanced | Amplitude tracking |
| Pattern Complexity | 1.000 | Enhanced | Spectral entropy |
| Overall Groove | 0.82 | Enhanced | Weighted combination |

---

##  Future Enhancements

### Planned Features
1. **Real-time TFR Analysis**: Live drummer analysis during performance
2. **Multi-GPU Support**: Distributed analysis across multiple GPUs
3. **Cloud Integration**: Remote GPU processing capabilities
4. **Interactive Visualizations**: Web-based analysis dashboards
5. **ML Integration**: Machine learning-based pattern recognition

### Research Directions
1. **Neural Entrainment**: Brainwave analysis integration
2. **Style Transfer**: AI-based drummer style transfer
3. **Performance Prediction**: Predictive modeling of drummer behavior
4. **Genre Classification**: Automatic genre detection from drum patterns

---

## [CALL] Support and Documentation

### Getting Help
1. **Check Troubleshooting Section**: Common issues and solutions
2. **Validate Environment**: Run validation scripts
3. **Check Logs**: Review analysis logs for error details
4. **Memory Documentation**: Refer to `docs/Memories.md` for insights

### Contributing
1. **Code Standards**: Follow existing code structure and documentation
2. **Testing**: Validate all changes with both analysis methods
3. **Documentation**: Update this README for any new features
4. **Memory Updates**: Document significant changes in `docs/Memories.md`

---

## [NOTE] Version History

### v1.1.7 (January 2025)
- [SUCCESS] GPU-accelerated TFR analysis integration
- [SUCCESS] Comprehensive comparison tools
- [SUCCESS] LLVM-safe environment configuration
- [SUCCESS] Publication-quality visualizations
- [SUCCESS] Authenticity validation framework

### Previous Versions
- v1.1.6: Standard analysis with librosa
- v1.1.5: Basic drummer profiling
- v1.1.4: UI improvements and batch processing

---

*This README provides comprehensive setup and usage instructions for both standard and GPU-accelerated TFR analysis methods in DrumTracKAI v1.1.7. For additional technical details, refer to the memory documentation in `docs/Memories.md`.*
