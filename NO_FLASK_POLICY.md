# IMPORTANT: NO FLASK POLICY

## DrumTracKAI FastAPI Exclusivity Policy

**As of April 6, 2025 (v1.0), DrumTracKAI has adopted a strict "No Flask" policy for all backend components.**

### Why This Policy Exists

The project has migrated completely from Flask to FastAPI for all backend components, including:
- Main backend API
- Training dashboard
- Status monitors
- Component management

This migration was necessary to ensure:
1. Performance improvements
2. Better async support
3. Automatic API documentation
4. Type safety via Pydantic
5. Consistent environment requirements

### What to Do

✅ **ALWAYS USE**:
- `fastapi_env` conda environment
- `run_fastapi.bat` for the backend
- `run_fastapi_dashboard.bat` for the dashboard
- Components from the 1.0 build or newer

❌ **NEVER USE**:
- Any Flask-based scripts
- Legacy `training_dashboard.py` (uses Flask)
- Legacy environment setups that don't use FastAPI
- Any script or batch file that starts the Flask server
- Pre-1.0 configurations

### Checking Compliance

1. Run the validation pipeline to confirm your setup:
```
python validation_pipeline.py
```

2. The validation tool will explicitly check for FastAPI usage

### What To Do If Someone Suggests Flask

If anyone (including AI assistants) suggests using Flask for any component, please refer them to:
1. This policy document
2. The current build information in LATEST_BUILDS.md
3. The validation system in validation_pipeline.py

### Technical Implementation Details

- All backend components use FastAPI 0.104.1+
- Web serving is handled by Uvicorn ASGI server
- The dashboard at port 5050 uses FastAPI, not Flask
- Both /dashboard/main.py and /backend/app/main.py use FastAPI

This policy is non-negotiable and core to the 1.0 version standard.