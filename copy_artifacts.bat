@echo off
REM DrumTracKAI Artifacts Copy Script
REM This script helps copy the artifacts to the appropriate files

setlocal enabledelayedexpansion

echo DrumTracKAI Artifacts Copy Script
echo ================================
echo.
echo This script will help you copy the artifacts to the appropriate files.
echo.

set PROJECT_ROOT=C:\Users\goldw\DrumTracKAI
set ARTIFACTS_FOLDER=%PROJECT_ROOT%\artifacts

REM Check if artifacts folder exists
if not exist "%ARTIFACTS_FOLDER%" (
  echo Creating artifacts folder...
  mkdir "%ARTIFACTS_FOLDER%"
  echo.
  echo Please save all the artifacts from the Claude conversation into:
  echo %ARTIFACTS_FOLDER%
  echo.
  echo Artifact filenames should be:
  echo - api-specification.yaml
  echo - youtube-controller.py
  echo - youtube-service.py
  echo - task-service.py
  echo - task-model.py
  echo - database-utils.py
  echo - custom-exceptions.py
  echo - error-handler.py
  echo - config.py
  echo - init-file.py
  echo.
  echo After saving artifacts, run this script again.
  goto end
)

echo Checking for artifacts...
echo.

set missing=0

REM Check for necessary artifacts
call :check_file "api-specification.yaml" || set missing=1
call :check_file "youtube-controller.py" || set missing=1
call :check_file "youtube-service.py" || set missing=1
call :check_file "task-service.py" || set missing=1
call :check_file "task-model.py" || set missing=1
call :check_file "database-utils.py" || set missing=1
call :check_file "custom-exceptions.py" || set missing=1
call :check_file "error-handler.py" || set missing=1
call :check_file "config.py" || set missing=1
call :check_file "init-file.py" || set missing=1

if %missing%==1 (
  echo.
  echo Some artifacts are missing. Please save all artifacts and try again.
  goto end
)

echo All artifacts found.
echo.

REM Create directories if they don't exist
echo Creating directories...
if not exist "%PROJECT_ROOT%\backend\drumtrackkai\utils" mkdir "%PROJECT_ROOT%\backend\drumtrackkai\utils"
if not exist "%PROJECT_ROOT%\backend\drumtrackkai\static\swagger" mkdir "%PROJECT_ROOT%\backend\drumtrackkai\static\swagger"
if not exist "%PROJECT_ROOT%\backend\logs" mkdir "%PROJECT_ROOT%\backend\logs"
if not exist "%PROJECT_ROOT%\backend\uploads\audio" mkdir "%PROJECT_ROOT%\backend\uploads\audio"
if not exist "%PROJECT_ROOT%\backend\results" mkdir "%PROJECT_ROOT%\backend\results"

REM Create __init__.py files if they don't exist
echo Creating __init__.py files...
if not exist "%PROJECT_ROOT%\backend\drumtrackkai\utils\__init__.py" echo. > "%PROJECT_ROOT%\backend\drumtrackkai\utils\__init__.py"

REM Copy files
echo.
echo Copying artifact files to project...

REM Backup init file if it exists
if exist "%PROJECT_ROOT%\backend\drumtrackkai\__init__.py" (
  echo Backing up existing __init__.py...
  copy "%PROJECT_ROOT%\backend\drumtrackkai\__init__.py" "%PROJECT_ROOT%\backend\drumtrackkai\__init__.py.backup"
)

REM Copy each artifact to its destination
call :copy_file "api-specification.yaml" "%PROJECT_ROOT%\backend\drumtrackkai\static\swagger\swagger.json"
call :copy_file "youtube-controller.py" "%PROJECT_ROOT%\backend\drumtrackkai\api\youtube.py"
call :copy_file "youtube-service.py" "%PROJECT_ROOT%\backend\drumtrackkai\services\youtube_service.py"
call :copy_file "task-service.py" "%PROJECT_ROOT%\backend\drumtrackkai\services\task_service.py"
call :copy_file "task-model.py" "%PROJECT_ROOT%\backend\drumtrackkai\models\task.py"
call :copy_file "database-utils.py" "%PROJECT_ROOT%\backend\drumtrackkai\utils\db_utils.py"
call :copy_file "custom-exceptions.py" "%PROJECT_ROOT%\backend\drumtrackkai\utils\exceptions.py"
call :copy_file "error-handler.py" "%PROJECT_ROOT%\backend\drumtrackkai\utils\error_handler.py"
call :copy_file "config.py" "%PROJECT_ROOT%\backend\drumtrackkai\config.py"
call :copy_file "init-file.py" "%PROJECT_ROOT%\backend\drumtrackkai\__init__.py"

echo.
echo All artifacts copied successfully!
echo.
echo Next steps:
echo 1. Update your requirements.txt file with additional dependencies:
echo    - flask-swagger-ui
echo    - yt-dlp
echo    - google-api-python-client
echo    - validators
echo    - flask-limiter
echo.
echo 2. Install the dependencies:
echo    cd %PROJECT_ROOT%\backend
echo    pip install -r requirements.txt
echo.
echo 3. Create or update your .env file with:
echo    FLASK_APP=run.py
echo    FLASK_ENV=development
echo    SECRET_KEY=your-secret-key
echo    JWT_SECRET_KEY=your-jwt-secret-key
echo    YOUTUBE_API_KEY=your-youtube-api-key
echo.
echo 4. Run the application:
echo    flask run
echo.
echo Note: If you had an existing __init__.py, check __init__.py.backup
echo       to ensure you haven't lost any important functionality.

goto end

:check_file
if not exist "%ARTIFACTS_FOLDER%\%~1" (
  echo Missing artifact: %~1
  exit /b 1
)
echo Found artifact: %~1
exit /b 0

:copy_file
echo Copying %~1 to %~2...
copy "%ARTIFACTS_FOLDER%\%~1" "%~2"
if errorlevel 1 (
  echo Error copying %~1 to %~2
  exit /b 1
)
exit /b 0

:end
echo.
echo Press any key to exit...
pause > nul