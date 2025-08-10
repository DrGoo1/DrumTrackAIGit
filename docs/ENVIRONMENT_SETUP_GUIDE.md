# DrumTracKAI Environment Setup Guide

This guide will help you set up a compatible environment to resolve the LLVM crash issue that prevents drum analysis from working.

## Problem Summary

Your current environment has incompatible versions:
- **Python 3.13.2** (too new, causes compatibility issues)
- **numpy 2.1.3** (incompatible with librosa, causes LLVM crashes)
- **librosa 0.11.0** (has numpy 2.0+ compatibility issues)

## Solution: Python 3.11 with Compatible Dependencies

## Method 1: Using Python.org Installer (Recommended)

### Step 1: Install Python 3.11

1. **Download Python 3.11.x** from [python.org](https://www.python.org/downloads/)
   - Choose the latest Python 3.11.x version (e.g., 3.11.8)
   - Download the Windows x86-64 installer

2. **Install Python 3.11**
   - Run the installer
   - [SUCCESS] **IMPORTANT**: Check "Add Python 3.11 to PATH"
   - Choose "Customize installation"
   - [SUCCESS] Check "pip" and "py launcher"
   - Install for all users (recommended)

3. **Verify installation**
   ```cmd
   python3.11 --version
   # Should show: Python 3.11.x
   ```

### Step 2: Create Virtual Environment

1. **Navigate to DrumTracKAI directory**
   ```cmd
   cd H:\DrumTracKAI_v1.1.7
   ```

2. **Create virtual environment**
   ```cmd
   python3.11 -m venv drumtrackai_env
   ```

3. **Activate the environment**
   ```cmd
   # Windows Command Prompt:
   drumtrackai_env\Scripts\activate
   
   # Windows PowerShell:
   drumtrackai_env\Scripts\Activate.ps1
   ```

4. **Verify you're in the virtual environment**
   ```cmd
   python --version
   # Should show: Python 3.11.x
   ```

### Step 3: Install Compatible Dependencies

1. **Upgrade pip first**
   ```cmd
   python -m pip install --upgrade pip
   ```

2. **Install compatible audio analysis libraries**
   ```cmd
   pip install numpy==1.24.3
   pip install scipy==1.10.1
   pip install librosa==0.10.1
   pip install soundfile==0.12.1
   ```

3. **Install other DrumTracKAI dependencies**
   ```cmd
   pip install PySide6
   pip install requests
   pip install python-dotenv
   pip install Pillow
   ```

4. **Verify installations**
   ```cmd
   python -c "import numpy; print('numpy:', numpy.__version__)"
   python -c "import librosa; print('librosa:', librosa.__version__)"
   python -c "import soundfile; print('soundfile:', soundfile.__version__)"
   ```

## Method 2: Using Conda (Alternative)

### Step 1: Install Miniconda

1. **Download Miniconda** from [conda.io](https://docs.conda.io/en/latest/miniconda.html)
2. **Install Miniconda** (follow installer instructions)

### Step 2: Create Conda Environment

```cmd
# Create environment with Python 3.11
conda create -n drumtrackai python=3.11

# Activate environment
conda activate drumtrackai

# Install compatible packages
conda install numpy=1.24 scipy=1.10 librosa=0.10 soundfile

# Install additional dependencies
pip install PySide6 requests python-dotenv Pillow
```

## Method 3: Using pyenv (Advanced Users)

If you frequently work with different Python versions:

```cmd
# Install pyenv-win (Windows)
git clone https://github.com/pyenv-win/pyenv-win.git %USERPROFILE%\.pyenv

# Add to PATH (restart terminal after)
# Install Python 3.11
pyenv install 3.11.8
pyenv local 3.11.8

# Create virtual environment
python -m venv drumtrackai_env
drumtrackai_env\Scripts\activate

# Install dependencies (same as Method 1, Step 3)
```

## Testing the Setup

### Step 1: Run Compatibility Checker

```cmd
# Make sure you're in the virtual environment
python setup_compatible_environment.py
```

You should see:
```
[OK] Python version is compatible
[OK] No compatibility issues detected
```

### Step 2: Run Analysis Test Suite

```cmd
python test_drum_analysis_fix.py
```

You should see:
```
[SUCCESS] ALL TESTS PASSED!
The drum analysis fix is working correctly.
```

### Step 3: Test DrumTracKAI Application

```cmd
cd admin
python main.py
```

The application should:
- [SUCCESS] Launch without errors
- [SUCCESS] Allow you to run drum analysis workflow
- [SUCCESS] Complete analysis without LLVM crashes
- [SUCCESS] Show real detected tempo, key, and musical sections

## Troubleshooting

### Issue: "python3.11 not found"
**Solution**: Make sure Python 3.11 is installed and added to PATH. Try:
```cmd
py -3.11 --version
```

### Issue: Virtual environment activation fails
**Solution**: 
- For PowerShell: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- Or use Command Prompt instead

### Issue: Package installation fails
**Solution**:
```cmd
# Update pip and try again
python -m pip install --upgrade pip setuptools wheel
# Then retry package installation
```

### Issue: Still getting LLVM crashes
**Solution**: 
1. Verify you're in the correct virtual environment
2. Check versions: `pip list | findstr "numpy librosa scipy"`
3. Ensure numpy is 1.24.x (not 2.x)

## Environment Management

### Activating the Environment (Daily Use)

```cmd
cd H:\DrumTracKAI_v1.1.7
drumtrackai_env\Scripts\activate
cd admin
python main.py
```

### Deactivating the Environment

```cmd
deactivate
```

### Updating Dependencies (If Needed)

```cmd
# Activate environment first
drumtrackai_env\Scripts\activate

# Update specific packages
pip install --upgrade soundfile
# But keep numpy/librosa at compatible versions
```

## Summary

After following this guide, you'll have:
- [SUCCESS] Python 3.11.x (stable, compatible version)
- [SUCCESS] numpy 1.24.3 (no LLVM crashes)
- [SUCCESS] librosa 0.10.1 (fully compatible)
- [SUCCESS] Isolated environment (won't affect other projects)
- [SUCCESS] Working drum analysis with real musical detection

The drum analysis workflow will then provide genuine tempo, key, and musical section detection without crashes or fallback values.
