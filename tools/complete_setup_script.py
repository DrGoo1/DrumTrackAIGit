#!/usr/bin/env python3
"""
DrumTracKAI Complete Setup & Configuration Script
Comprehensive setup, validation, and launch system
"""

import os
import sys
import subprocess
import json
import time
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DrumTracKAISetup:
    """Complete setup and configuration manager"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.config = {}
        self.requirements_checked = False
        self.services_status = {}
    
    def print_banner(self):
        """Print startup banner"""
        banner = """
🥁 DrumTracKAI Backend Setup & Configuration
═══════════════════════════════════════════════════════════════════════════════
🎯 Expert Model: 88.7% Sophistication
🔥 Real-time Analysis: Enabled  
🎵 MVSep Integration: Available
🎸 Advanced Audio Engine: Active
💾 Database: SQLite/PostgreSQL
🔐 Authentication: JWT Enabled
📡 WebSocket: Real-time Updates
🐳 Docker: Production Ready
═══════════════════════════════════════════════════════════════════════════════
        """
        print(banner)
    
    def check_python_version(self) -> bool:
        """Check Python version compatibility"""
        version = sys.version_info
        if version < (3, 8):
            logger.error(f"❌ Python 3.8+ required. Current: {version.major}.{version.minor}")
            return False
        
        logger.info(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    
    def check_system_dependencies(self) -> Dict[str, bool]:
        """Check system dependencies"""
        dependencies = {
            'git': self._check_command('git --version'),
            'curl': self._check_command('curl --version'),
            'ffmpeg': self._check_command('ffmpeg -version'),
        }
        
        for dep, available in dependencies.items():
            if available:
                logger.info(f"✅ {dep}: Available")
            else:
                logger.warning(f"⚠️  {dep}: Not available (optional)")
        
        return dependencies
    
    def _check_command(self, command: str) -> bool:
        """Check if a command is available"""
        try:
            subprocess.run(command.split(), capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def setup_virtual_environment(self) -> bool:
        """Setup Python virtual environment"""
        venv_path = self.project_root / 'venv'
        
        if venv_path.exists():
            logger.info("✅ Virtual environment already exists")
            return True
        
        try:
            logger.info("📦 Creating virtual environment...")
            subprocess.check_call([sys.executable, '-m', 'venv', str(venv_path)])
            logger.info("✅ Virtual environment created")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to create virtual environment: {e}")
            return False
    
    def install_dependencies(self) -> bool:
        """Install Python dependencies"""
        if self.requirements_checked:
            return True
        
        venv_python = self._get_venv_python()
        if not venv_python:
            logger.error("❌ Virtual environment not found")
            return False
        
        try:
            logger.info("📥 Installing dependencies...")
            
            # Upgrade pip first
            subprocess.check_call([venv_python, '-m', 'pip', 'install', '--upgrade', 'pip'])
            
            # Install core requirements
            core_deps = [
                'fastapi>=0.104.0',
                'uvicorn[standard]>=0.24.0',
                'python-multipart>=0.0.6',
                'pydantic>=2.5.0',
                'python-jose[cryptography]>=3.3.0',
                'passlib[bcrypt]>=1.7.4',
                'PyJWT>=2.8.0',
                'websockets>=12.0',
                'requests>=2.25.0',
                'aiofiles>=23.2.0'
            ]
            
            subprocess.check_call([venv_python, '-m', 'pip', 'install'] + core_deps)
            
            # Install optional audio processing
            try:
                audio_deps = ['numpy>=1.21.0', 'scipy>=1.7.0', 'librosa>=0.9.0', 'soundfile>=0.10.0']
                subprocess.check_call([venv_python, '-m', 'pip', 'install'] + audio_deps)
                logger.info("✅ Audio processing libraries installed")
            except subprocess.CalledProcessError:
                logger.warning("⚠️  Audio processing libraries not installed (will use mock mode)")
            
            self.requirements_checked = True
            logger.info("✅ Dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install dependencies: {e}")
            return False
    
    def _get_venv_python(self) -> Optional[str]:
        """Get path to virtual environment Python"""
        venv_path = self.project_root / 'venv'
        
        if os.name == 'nt':  # Windows
            python_path = venv_path / 'Scripts' / 'python.exe'
        else:  # Unix-like
            python_path = venv_path / 'bin' / 'python'
        
        return str(python_path) if python_path.exists() else None
    
    def setup_configuration(self) -> bool:
        """Setup configuration files"""
        logger.info("⚙️  Setting up configuration...")
        
        # Create .env file if it doesn't exist
        env_file = self.project_root / '.env'
        env_example = self.project_root / '.env.example'
        
        if not env_file.exists():
            if env_example.exists():
                shutil.copy2(env_example, env_file)
                logger.info("📝 Created .env from example")
            else:
                self._create_default_env(env_file)
        
        # Load configuration
        self.config = self._load_env_config(env_file)
        
        # Create directories
        directories = [
            'drumtrackai_cache',
            'drumtrackai_cache/audio',
            'drumtrackai_cache/uploads',
            'logs',
            'backups'
        ]
        
        for dir_name in directories:
            dir_path = self.project_root / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 Created directory: {dir_name}")
        
        logger.info("✅ Configuration setup complete")
        return True
    
    def _create_default_env(self, env_file: Path):
        """Create default .env file"""
        default_config = """# DrumTracKAI Configuration

# JWT Configuration
JWT_SECRET_KEY=drumtrackai-change-this-secret-key-in-production

# MVSep API Configuration (get from https://mvsep.com)
MVSEP_API_KEY=MfPdUMwxmFDCcDJj0Z4kmb9SCOLKPh

# Database Configuration
DATABASE_URL=sqlite:///drumtrackai.db

# Server Configuration
HOST=127.0.0.1
PORT=8000
DEBUG=false

# File Upload Limits (MB)
MAX_UPLOAD_SIZE_BASIC=10
MAX_UPLOAD_SIZE_PROFESSIONAL=100
MAX_UPLOAD_SIZE_EXPERT=500

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/drumtrackai.log

# CORS Origins
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
"""
        
        with open(env_file, 'w') as f:
            f.write(default_config)
        
        logger.info("📝 Created default .env file")
    
    def _load_env_config(self, env_file: Path) -> Dict[str, str]:
        """Load environment configuration"""
        config = {}
        
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()
        
        return config
    
    def validate_configuration(self) -> bool:
        """Validate configuration"""
        logger.info("🔍 Validating configuration...")
        
        issues = []
        
        # Check JWT secret
        jwt_secret = self.config.get('JWT_SECRET_KEY', '')
        if not jwt_secret or jwt_secret == 'drumtrackai-change-this-secret-key-in-production':
            issues.append("⚠️  JWT_SECRET_KEY should be changed for production")
        
        # Check MVSep API key
        mvsep_key = self.config.get('MVSEP_API_KEY', '')
        if not mvsep_key or mvsep_key == 'your-mvsep-api-key':
            issues.append("⚠️  MVSEP_API_KEY not configured (stem separation will use demo mode)")
        
        # Check port availability
        port = int(self.config.get('PORT', 8000))
        if not self._check_port_available(port):
            issues.append(f"⚠️  Port {port} is already in use")
        
        if issues:
            logger.warning("Configuration issues found:")
            for issue in issues:
                logger.warning(f"  {issue}")
        else:
            logger.info("✅ Configuration validation passed")
        
        return len(issues) == 0
    
    def _check_port_available(self, port: int) -> bool:
        """Check if port is available"""
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return True
        except OSError:
            return False
    
    def test_services(self) -> Dict[str, bool]:
        """Test all services"""
        logger.info("🧪 Testing services...")
        
        services = {
            'database': self._test_database(),
            'audio_processing': self._test_audio_processing(),
            'mvsep': self._test_mvsep(),
            'file_system': self._test_file_system()
        }
        
        for service, status in services.items():
            if status:
                logger.info(f"✅ {service}: Working")
            else:
                logger.warning(f"⚠️  {service}: Issues detected")
        
        self.services_status = services
        return services
    
    def _test_database(self) -> bool:
        """Test database connectivity"""
        try:
            import sqlite3
            db_path = self.project_root / 'drumtrackai_cache' / 'test.db'
            
            with sqlite3.connect(str(db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute('CREATE TABLE IF NOT EXISTS test (id INTEGER)')
                cursor.execute('INSERT INTO test (id) VALUES (1)')
                cursor.execute('SELECT COUNT(*) FROM test')
                count = cursor.fetchone()[0]
                cursor.execute('DROP TABLE test')
            
            db_path.unlink(missing_ok=True)
            return count > 0
            
        except Exception as e:
            logger.error(f"Database test failed: {e}")
            return False
    
    def _test_audio_processing(self) -> bool:
        """Test audio processing capabilities"""
        try:
            import numpy as np
            
            # Test basic numpy operations
            data = np.random.random(1000)
            result = np.mean(data)
            
            # Try to import librosa (optional)
            try:
                import librosa
                return True
            except ImportError:
                logger.info("Librosa not available - using mock audio processing")
                return True
                
        except Exception as e:
            logger.error(f"Audio processing test failed: {e}")
            return False
    
    def _test_mvsep(self) -> bool:
        """Test MVSep service availability"""
        api_key = self.config.get('MVSEP_API_KEY', '')
        if not api_key or api_key in ['your-mvsep-api-key', 'MfPdUMwxmFDCcDJj0Z4kmb9SCOLKPh']:
            return False
        
        try:
            import requests
            # Test MVSep API connectivity (basic check)
            response = requests.get('https://mvsep.com', timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def _test_file_system(self) -> bool:
        """Test file system operations"""
        try:
            test_dir = self.project_root / 'drumtrackai_cache' / 'test'
            test_dir.mkdir(exist_ok=True)
            
            test_file = test_dir / 'test.txt'
            test_file.write_text('test')
            
            content = test_file.read_text()
            
            test_file.unlink()
            test_dir.rmdir()
            
            return content == 'test'
            
        except Exception as e:
            logger.error(f"File system test failed: {e}")
            return False
    
    def start_server(self, development: bool = True) -> bool:
        """Start the DrumTracKAI server"""
        venv_python = self._get_venv_python()
        if not venv_python:
            logger.error("❌ Virtual environment not found")
            return False
        
        try:
            if development:
                logger.info("🚀 Starting development server...")
                subprocess.check_call([
                    venv_python, 
                    'drumtrackai_fastapi_server.py'
                ])
            else:
                logger.info("🚀 Starting production server...")
                subprocess.check_call([
                    venv_python, '-m', 'uvicorn',
                    'drumtrackai_fastapi_server:app',
                    '--host', self.config.get('HOST', '127.0.0.1'),
                    '--port', self.config.get('PORT', '8000'),
                    '--workers', '4',
                    '--log-level', 'info'
                ])
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to start server: {e}")
            return False
        except KeyboardInterrupt:
            logger.info("🛑 Server stopped by user")
            return True
    
    def run_tests(self) -> bool:
        """Run API tests"""
        venv_python = self._get_venv_python()
        if not venv_python:
            logger.error("❌ Virtual environment not found")
            return False
        
        try:
            logger.info("🧪 Running API tests...")
            
            # Install test dependencies
            test_deps = ['pytest', 'httpx', 'websocket-client']
            subprocess.check_call([venv_python, '-m', 'pip', 'install'] + test_deps)
            
            # Run tests
            result = subprocess.run([
                venv_python, '-m', 'pytest', 
                'api_testing.py', '-v'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ All tests passed")
                return True
            else:
                logger.error("❌ Some tests failed")
                logger.error(result.stdout)
                logger.error(result.stderr)
                return False
                
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Test execution failed: {e}")
            return False
    
    def generate_documentation(self):
        """Generate comprehensive documentation"""
        logger.info("📚 Generating documentation...")
        
        venv_python = self._get_venv_python()
        if venv_python:
            try:
                subprocess.check_call([venv_python, 'api_documentation.py', '--generate-docs'])
                logger.info("✅ API documentation generated")
            except subprocess.CalledProcessError:
                logger.warning("⚠️  Could not generate API documentation")
        
        # Generate README
        readme_content = self._generate_readme()
        with open('README.md', 'w') as f:
            f.write(readme_content)
        logger.info("✅ README.md generated")
    
    def _generate_readme(self) -> str:
        """Generate README content"""
        return f"""# DrumTracKAI Backend

Advanced AI-powered drum analysis and generation API.

## Features

- 🎯 **Expert Model**: 88.7% Sophistication
- 🔥 **Real-time Analysis**: WebSocket support
- 🎵 **MVSep Integration**: Professional stem separation
- 🎸 **Advanced Audio Engine**: Multi-format support
- 💾 **Database**: SQLite/PostgreSQL support
- 🔐 **Authentication**: JWT-based security
- 📡 **WebSocket**: Real-time progress updates
- 🐳 **Docker**: Production-ready containers

## Quick Start

1. **Setup Environment**
   ```bash
   python setup.py --setup
   ```

2. **Configure API Keys**
   Edit `.env` file with your MVSep API key:
   ```
   MVSEP_API_KEY=your_api_key_here
   ```

3. **Start Server**
   ```bash
   python setup.py --start
   ```

4. **Test API**
   ```bash
   python setup.py --test
   ```

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration

### Analysis
- `POST /api/upload` - Upload audio file
- `POST /api/analyze` - Start analysis
- `GET /api/progress/{{job_id}}` - Get progress
- `GET /api/results/{{job_id}}` - Get results

### Studio
- `POST /api/studio/generate` - Generate drum track
- `GET /api/studio/drummers` - Get drummer styles
- `GET /api/studio/samples` - Get sample patterns

### WebSocket
- `ws://localhost:8000/ws/progress/{{job_id}}` - Real-time updates

## User Tiers

| Feature | Basic | Professional | Expert |
|---------|-------|--------------|--------|
| Upload Limit | 10MB | 100MB | 500MB |
| Monthly Uploads | 10 | 100 | Unlimited |
| Sophistication | 65% | 82% | 88.7% |
| Stems | 2 | 4 | 8+ |
| Analysis | Basic | Advanced | Expert AI |

## Configuration

### Environment Variables
- `JWT_SECRET_KEY` - JWT signing key
- `MVSEP_API_KEY` - MVSep API key
- `DATABASE_URL` - Database connection
- `PORT` - Server port (default: 8000)

### Services Status
{self._format_services_status()}

## Development

### Setup Development Environment
```bash
python setup.py --dev-setup
```

### Run Tests
```bash
python setup.py --test
```

### Generate Documentation
```bash
python setup.py --docs
```

## Docker Deployment

```bash
docker-compose up -d
```

## Support

- API Documentation: `/docs` (when server is running)
- Issues: GitHub Issues
- Email: support@drumtrackai.com

## License

MIT License - See LICENSE file for details.
"""
    
    def _format_services_status(self) -> str:
        """Format services status for README"""
        if not self.services_status:
            return "Run `python setup.py --test-services` to check status"
        
        status_lines = []
        for service, status in self.services_status.items():
            emoji = "✅" if status else "❌"
            status_lines.append(f"- {emoji} {service.replace('_', ' ').title()}")
        
        return "\n".join(status_lines)
    
    def create_docker_files(self):
        """Create Docker configuration files"""
        logger.info("🐳 Creating Docker configuration...")
        
        # Dockerfile
        dockerfile_content = """FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \\
    build-essential \\
    libsndfile1-dev \\
    ffmpeg \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p drumtrackai_cache/audio drumtrackai_cache/uploads logs

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/api/status || exit 1

CMD ["python", "drumtrackai_fastapi_server.py"]
"""
        
        with open('Dockerfile', 'w') as f:
            f.write(dockerfile_content)
        
        # docker-compose.yml
        compose_content = """version: '3.8'

services:
  drumtrackai-backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - JWT_SECRET_KEY=${JWT_SECRET_KEY:-drumtrackai-development-key}
      - MVSEP_API_KEY=${MVSEP_API_KEY}
      - DATABASE_URL=${DATABASE_URL:-sqlite:///drumtrackai.db}
    volumes:
      - ./drumtrackai_cache:/app/drumtrackai_cache
      - ./logs:/app/logs
    restart: unless-stopped

volumes:
  drumtrackai_data:
"""
        
        with open('docker-compose.yml', 'w') as f:
            f.write(compose_content)
        
        logger.info("✅ Docker files created")
    
    def show_status_dashboard(self):
        """Show comprehensive status dashboard"""
        print("\n" + "="*80)
        print("🥁 DrumTracKAI Backend Status Dashboard")
        print("="*80)
        
        # System Information
        print("\n📊 System Information:")
        print(f"   Python Version: {sys.version.split()[0]}")
        print(f"   Project Root: {self.project_root}")
        print(f"   Virtual Environment: {'✅ Active' if self._get_venv_python() else '❌ Not Found'}")
        
        # Configuration
        print("\n⚙️  Configuration:")
        print(f"   Port: {self.config.get('PORT', '8000')}")
        print(f"   Host: {self.config.get('HOST', '127.0.0.1')}")
        print(f"   Database: {self.config.get('DATABASE_URL', 'sqlite:///drumtrackai.db')}")
        print(f"   MVSep API: {'✅ Configured' if self.config.get('MVSEP_API_KEY', '').startswith('MfP') else '❌ Not Configured'}")
        
        # Services Status
        print("\n🔧 Services Status:")
        for service, status in self.services_status.items():
            emoji = "✅" if status else "❌"
            print(f"   {emoji} {service.replace('_', ' ').title()}")
        
        # Directory Structure
        print("\n📁 Directory Structure:")
        important_dirs = ['drumtrackai_cache', 'logs', 'backups']
        for dir_name in important_dirs:
            dir_path = self.project_root / dir_name
            exists = "✅" if dir_path.exists() else "❌"
            print(f"   {exists} {dir_name}/")
        
        # Next Steps
        print("\n🚀 Quick Actions:")
        print("   python setup.py --start     # Start the server")
        print("   python setup.py --test      # Run tests")
        print("   python setup.py --docs      # Generate docs")
        print("   docker-compose up -d        # Start with Docker")
        
        print("="*80)

def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='DrumTracKAI Backend Setup & Management',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python setup.py --setup              # Complete setup
  python setup.py --start              # Start development server
  python setup.py --start --production # Start production server
  python setup.py --test               # Run tests
  python setup.py --status             # Show status dashboard
        """
    )
    
    parser.add_argument('--setup', action='store_true', help='Run complete setup')
    parser.add_argument('--dev-setup', action='store_true', help='Setup development environment only')
    parser.add_argument('--start', action='store_true', help='Start the server')
    parser.add_argument('--production', action='store_true', help='Use production mode')
    parser.add_argument('--test', action='store_true', help='Run API tests')
    parser.add_argument('--test-services', action='store_true', help='Test all services')
    parser.add_argument('--docs', action='store_true', help='Generate documentation')
    parser.add_argument('--docker', action='store_true', help='Create Docker files')
    parser.add_argument('--status', action='store_true', help='Show status dashboard')
    parser.add_argument('--validate', action='store_true', help='Validate configuration')
    
    args = parser.parse_args()
    
    setup = DrumTracKAISetup()
    setup.print_banner()
    
    # Check Python version first
    if not setup.check_python_version():
        return 1
    
    success = True
    
    try:
        if args.setup or args.dev_setup:
            logger.info("🚀 Starting setup process...")
            
            # System checks
            setup.check_system_dependencies()
            
            # Setup virtual environment
            if not setup.setup_virtual_environment():
                return 1
            
            # Install dependencies
            if not setup.install_dependencies():
                return 1
            
            # Setup configuration
            if not setup.setup_configuration():
                return 1
            
            # Test services
            setup.test_services()
            
            # Generate documentation
            setup.generate_documentation()
            
            # Create Docker files
            if not args.dev_setup:
                setup.create_docker_files()
            
            logger.info("✅ Setup completed successfully!")
            setup.show_status_dashboard()
        
        elif args.start:
            setup.setup_configuration()
            setup.validate_configuration()
            setup.test_services()
            success = setup.start_server(development=not args.production)
        
        elif args.test:
            success = setup.run_tests()
        
        elif args.test_services:
            setup.test_services()
            setup.show_status_dashboard()
        
        elif args.docs:
            setup.generate_documentation()
        
        elif args.docker:
            setup.create_docker_files()
        
        elif args.validate:
            setup.setup_configuration()
            success = setup.validate_configuration()
        
        elif args.status:
            setup.setup_configuration()
            setup.test_services()
            setup.show_status_dashboard()
        
        else:
            # Default action - show status
            setup.setup_configuration()
            setup.test_services()
            setup.show_status_dashboard()
            
            print("\nℹ️  Use --help for available commands")
    
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return 1
    
    return 0 if success else 1

if __name__ == '__main__':
    exit(main())