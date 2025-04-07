# DrumTracKAI Latest Builds Reference

This document provides a definitive reference for the latest builds of all DrumTracKAI components. Use this as a guide to ensure you're running the most up-to-date versions of each component.

Last updated: April 6, 2025

## Current Version: 1.0

The current stable version is **1.0**, which includes the complete testing and deployment framework. This version provides a comprehensive system for testing and deploying DrumTracKAI components.

## IMPORTANT: FASTAPI REQUIRED

**DrumTracKAI now EXCLUSIVELY uses FastAPI for all backend components, including the training dashboard. The Flask-based legacy code should NOT be used under any circumstances.**

To ensure you're using the correct environment:
1. Use the `fastapi_env` conda environment
2. Always launch with `run_fastapi.bat` for the backend and `run_fastapi_dashboard.bat` for the dashboard
3. Do NOT use any Flask-based scripts like the legacy `training_dashboard.py`

The validation system in v1.0 specifically checks for and enforces FastAPI usage.

## Testing and Deployment Framework (v1.0)

The v1.0 release includes a comprehensive testing and deployment framework:

| Component | Latest Build Location | Description |
|-----------|------------------------|-------------|
| **Configuration Management** | `config/app_config.json` and `config/config_manager.py` | Central configuration system |
| **Validation Pipeline** | `validation_pipeline.py` | Component validation system |
| **Component Tests** | `tests/test_fastapi_backend.py`, `tests/test_modern_ui.py`, `tests/test_system_integration.py` | Component-specific test scripts |
| **Master Testing Script** | `run_all_tests.py` | Comprehensive testing orchestration |
| **Deployment System** | `deploy_app.py` | Application deployment script |
| **Framework Documentation** | `TESTING_DEPLOYMENT_FRAMEWORK.md` | Usage guide for the framework |
| **Version References** | `VERSION` and `VERSION_1.0_INFO.md` | Version indicators |

## Backend Components

### FastAPI Backend

The FastAPI backend provides the API endpoints for all DrumTracKAI functionality.

| Component | Latest Build Location | Launch Command |
|-----------|------------------------|---------------|
| **FastAPI Backend** | `/backend/app/main.py` | `run_fastapi.bat` or `run_fastapi.sh` |
| **API Endpoints** | `/backend/app/api/v1/` | (Part of the FastAPI backend) |
| **Database Models** | `/backend/app/models/` | (Part of the FastAPI backend) |
| **Services** | `/backend/app/services/` | (Part of the FastAPI backend) |

**Launch Instructions:**
```bash
cd C:\Users\goldw\DrumTracKAI
run_fastapi.bat
```

The FastAPI backend will start on port 8008. You can verify it's running by navigating to `http://localhost:8008/docs` in your browser to see the Swagger API documentation.

## Frontend Components

### Modern UI

The modern UI is a React-based frontend that connects to the FastAPI backend.

| Component | Latest Build Location | Launch Command |
|-----------|------------------------|---------------|
| **Modern UI** | `/frontend/modern-ui/` | `run_modern_ui.bat` or `run_modern_ui.sh` |

**Launch Instructions:**
```bash
cd C:\Users\goldw\DrumTracKAI
run_modern_ui.bat
```

The modern UI will start on port 3000 and can be accessed at `http://localhost:3000`.

### Training Dashboard

The training dashboard provides visualization and control for the training process.

| Component | Latest Build Location | Launch Command |
|-----------|------------------------|---------------|
| **Training Dashboard** | `/training_dashboard.py` | Direct Python execution |

**Launch Instructions:**
```bash
cd C:\Users\goldw\DrumTracKAI
python training_dashboard.py --host 0.0.0.0 --port 5000
```

The training dashboard will be available at `http://localhost:5000`.

## Training Components

### Core Training System

The core training system provides the neural network training functionality.

| Component | Latest Build Location | Launch Command |
|-----------|------------------------|---------------|
| **Training Controller** | `/unified_training_controller.py` | Various component-specific batch files |
| **Component Models** | `/train_models/` | (Part of the training system) |
| **Training Pipeline** | `/training/` | (Part of the training system) |
| **MDLib Integration** | `/implementation_plan/dataset-integration/mdlib/` | `run_multi_dataset_integration.bat` |

**Launch Instructions for MDLib Integration:**
```bash
cd C:\Users\goldw\DrumTracKAI\implementation_plan\dataset-integration\mdlib
run_multi_dataset_integration.bat --component snare --datasets mdlib,soundtracks
```

**Launch Instructions for Component Training:**
```bash
cd C:\Users\goldw\DrumTracKAI
run_training_kick.bat  # For kick drum
run_training_snare.bat  # For snare drum
run_training_hihat.bat  # For hi-hat
# etc. for other components
```

### TensorBoard Integration

TensorBoard provides detailed visualization of training metrics.

| Component | Latest Build Location | Launch Command |
|-----------|------------------------|---------------|
| **TensorBoard** | `/tensorboard_logs/` | `run_tensorboard.bat` or `run_tensorboard.sh` |

**Launch Instructions:**
```bash
cd C:\Users\goldw\DrumTracKAI
run_tensorboard.bat
```

TensorBoard will be available at `http://localhost:6006`.

## Extraction Components

### Neural Extraction System

The neural extraction system provides the drum extraction functionality.

| Component | Latest Build Location | Launch Command |
|-----------|------------------------|---------------|
| **Extraction API** | `/backend/app/api/v1/extraction.py` | (Part of the FastAPI backend) |
| **Extraction Service** | `/backend/app/services/extraction_service.py` | (Part of the FastAPI backend) |
| **Neural Models** | `/models/` | (Part of the extraction system) |

**Direct Testing Command:**
```bash
cd C:\Users\goldw\DrumTracKAI
run_test_extraction.bat
```

## Combined Startup

To start the complete system, you can now use the deployment script (v1.0):

```bash
cd C:\Users\goldw\DrumTracKAI
python deploy_app.py
```

Or start individual components:

1. **Start the FastAPI Backend:**
   ```bash
   cd C:\Users\goldw\DrumTracKAI
   run_fastapi.bat
   ```

2. **Start the Modern UI:**
   ```bash
   cd C:\Users\goldw\DrumTracKAI
   run_modern_ui.bat
   ```

3. **Start the Training Dashboard (if needed):**
   ```bash
   cd C:\Users\goldw\DrumTracKAI
   python training_dashboard.py --host 0.0.0.0 --port 5000
   ```

4. **Start TensorBoard (if needed):**
   ```bash
   cd C:\Users\goldw\DrumTracKAI
   run_tensorboard.bat
   ```

## Dockerized Setup

The latest Dockerized setup is available in:

| Component | Latest Build Location | Launch Command |
|-----------|------------------------|---------------|
| **Docker Compose** | `/docker-compose.yml` | `docker-compose up` |
| **Docker Files** | `/Dockerfile`, `/Dockerfile.app`, `/Dockerfile.web` | (Part of Docker setup) |

**Launch Instructions for Docker (using the v1.0 framework):**
```bash
cd C:\Users\goldw\DrumTracKAI
python deploy_app.py --docker
```

Or using Docker directly:
```bash
cd C:\Users\goldw\DrumTracKAI
docker-compose up -d
```

## Testing the System

With the v1.0 testing framework, you can run comprehensive tests:

```bash
# Run all tests with a complete report
cd C:\Users\goldw\DrumTracKAI
python run_all_tests.py

# Validate components and start missing ones
python validation_pipeline.py --start

# Test specific components
python tests/test_fastapi_backend.py
python tests/test_modern_ui.py
python tests/test_system_integration.py
```

## Verifying Builds

To check that you're running the latest versions, verify these component versions:

1. **FastAPI Backend Version:** 
   - Check the version number in `http://localhost:8008/health`
   - Current version: 1.0.0

2. **React UI Version:**
   - Check package.json in `/frontend/modern-ui/`
   - Current version: 2.0.0

3. **Training Dashboard Version:**
   - The training dashboard displays its version in the footer
   - Current version: 3.5.0

4. **MDLib Integration Version:**
   - Check `/implementation_plan/dataset-integration/mdlib/MDLIB_IMPLEMENTATION_SUMMARY.md`
   - Current version: 2.2

5. **Framework Version:**
   - Check `/VERSION` file
   - Current version: 1.0

## Troubleshooting

If any component fails to start, please refer to the specific troubleshooting guides:

1. **FastAPI Backend Issues:** `FASTAPI_TROUBLESHOOTING.md`
2. **UI Issues:** `frontend/FRONTEND_TROUBLESHOOTING.md`
3. **Training Issues:** `TRAINING_TROUBLESHOOTING.md`
4. **Docker Issues:** `DOCKER_TROUBLESHOOTING.md`

## Best Practices

1. Always start the FastAPI backend before the frontend UI
2. For training runs, ensure TensorBoard is running to monitor progress
3. Use the latest MDLib integration for multi-dataset training
4. Check logs in the `/logs/` directory if you encounter issues
5. Ensure GPU support is properly configured for optimal performance
6. Use the validation pipeline to verify components before deployment
7. Run the full test suite before deploying to production

## Version History

### Version 1.0 (April 6, 2025)
- Initial release of the testing and deployment framework
- Implemented configuration management system
- Added validation pipeline
- Created component testing scripts
- Implemented comprehensive testing script
- Added deployment support for standard and Docker-based deployment