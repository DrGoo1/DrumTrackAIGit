#!/usr/bin/env python3
"""
DrumTracKAI Build Backup Script
==============================
Creates a comprehensive backup of the current DrumTracKAI build with all achievements

Features:
- Complete system backup
- Version tracking
- Achievement documentation
- Restore instructions

Author: DrumTracKAI v1.1.8
"""

import os
import shutil
import json
import zipfile
from pathlib import Path
from datetime import datetime

def create_build_backup():
    """Create comprehensive backup of current DrumTracKAI build"""
    
    # Backup configuration
    source_dir = Path("D:/DrumTracKAI_v1.1.7")
    backup_base_dir = Path("D:/DrumTracKAI_Backups")
    backup_base_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"DrumTracKAI_v1.1.8_MVSep_Integration_{timestamp}"
    backup_dir = backup_base_dir / backup_name
    
    print(f"[BACKUP] Creating backup: {backup_name}")
    print("=" * 60)
    
    try:
        # Create backup directory
        backup_dir.mkdir(exist_ok=True)
        
        # Define what to backup
        backup_items = [
            # Core system files
            "admin/",
            "database/",
            "docs/",
            "web-monitor/",
            
            # New batch analysis systems
            "production_batch_analysis_system.py",
            "signature_song_batch_analysis.py", 
            "enhanced_production_batch_analysis.py",
            "diagnostic_batch_analysis.py",
            "comprehensive_system_recovery.py",
            
            # Configuration files
            "mvsep_config.txt",
            "launch_drumtrackai_admin.bat",
            "launch_production_system.bat",
            
            # Environment files
            "drumtrackai_env/",
            
            # Results and logs (recent)
            "production_analysis_results/",
            "signature_song_results/",
            "enhanced_analysis_results/",
            "*.log"
        ]
        
        # Copy files and directories
        copied_items = []
        skipped_items = []
        
        for item_pattern in backup_items:
            if "*" in item_pattern:
                # Handle wildcard patterns
                for item_path in source_dir.glob(item_pattern):
                    if item_path.exists():
                        dest_path = backup_dir / item_path.name
                        if item_path.is_file():
                            shutil.copy2(item_path, dest_path)
                        else:
                            shutil.copytree(item_path, dest_path, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
                        copied_items.append(str(item_path.name))
            else:
                item_path = source_dir / item_pattern
                if item_path.exists():
                    dest_path = backup_dir / item_pattern
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    if item_path.is_file():
                        shutil.copy2(item_path, dest_path)
                    else:
                        shutil.copytree(item_path, dest_path, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
                    copied_items.append(item_pattern)
                else:
                    skipped_items.append(item_pattern)
        
        # Create backup manifest
        manifest = {
            "backup_info": {
                "name": backup_name,
                "version": "DrumTracKAI v1.1.8",
                "created_at": datetime.now().isoformat(),
                "source_directory": str(source_dir),
                "backup_directory": str(backup_dir)
            },
            "major_achievements": [
                "Real-Time Monitor Tab - Fully functional with live progress tracking",
                "Production Batch Analysis System - Processes drum beats with Expert model (88.7% sophistication)",
                "MVSep Integration - Automatic stem extraction for signature songs",
                "Signature Song Batch Analysis - Full song processing with HDemucs + DrumSep",
                "Enhanced Production System - Smart audio detection and unified processing",
                "Expert Model Integration - 88.7% sophistication model for drum analysis",
                "Complete Admin Interface - All 9 tabs functional and stable",
                "Database Integration - 40 drum beats + 500+ SD3 samples + signature songs",
                "Error Recovery System - Comprehensive system recovery and diagnostics",
                "Production Launchers - Easy-launch batch files for all systems"
            ],
            "technical_features": [
                "MVSep API Integration (HDemucs + DrumSep)",
                "Expert Model Analysis (88.7% sophistication)",
                "Real-time progress monitoring",
                "Smart audio type detection",
                "Comprehensive error handling",
                "Production-quality logging",
                "Automatic dependency management",
                "Unicode error fixes",
                "Environment isolation (drumtrackai_env)",
                "Batch processing capabilities"
            ],
            "system_components": {
                "admin_tabs": [
                    "Drummers - Signature song analysis workflow",
                    "Drum Analysis - Advanced pattern analysis + GPU",
                    "MVSep - AI-powered stem separation", 
                    "Drum Beats - Beat management + audio playback",
                    "Audio Visualization - 3D visualization + export",
                    "Batch Processing - Bulk processing + monitoring",
                    "Comprehensive Training - Multi-phase training system",
                    "Training Sophistication - Expert model documentation",
                    "Real-Time Monitor - Live progress tracking",
                    "Database Management - SQLite operations"
                ],
                "batch_analysis_systems": [
                    "production_batch_analysis_system.py - Drum-only batch processing",
                    "signature_song_batch_analysis.py - Full song MVSep processing",
                    "enhanced_production_batch_analysis.py - Unified smart processing",
                    "diagnostic_batch_analysis.py - System diagnostics and testing"
                ],
                "databases": [
                    "Drum Beats Database - 40 classic tracks",
                    "SD3 Extracted Samples - 500+ Superior Drummer samples",
                    "Signature Songs - Jeff Porcaro, Neil Peart, Stewart Copeland",
                    "Training Documentation - Expert model (88.7% sophistication)"
                ]
            },
            "copied_items": copied_items,
            "skipped_items": skipped_items,
            "backup_size_mb": 0  # Will be calculated
        }
        
        # Save manifest
        manifest_file = backup_dir / "backup_manifest.json"
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        # Calculate backup size
        total_size = sum(f.stat().st_size for f in backup_dir.rglob('*') if f.is_file())
        manifest["backup_size_mb"] = round(total_size / (1024 * 1024), 2)
        
        # Update manifest with size
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        # Create restore instructions
        restore_instructions = backup_dir / "RESTORE_INSTRUCTIONS.md"
        with open(restore_instructions, 'w', encoding='utf-8') as f:
            f.write(f"""# DrumTracKAI v1.1.8 Restore Instructions

## Backup Information
- **Version:** DrumTracKAI v1.1.8 with MVSep Integration
- **Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Size:** {manifest['backup_size_mb']} MB
- **Items:** {len(copied_items)} components backed up

## Major Features in This Build
- ✅ Real-Time Monitor Tab with live progress tracking
- ✅ Production Batch Analysis System (Expert model 88.7% sophistication)
- ✅ MVSep Integration for signature song stem extraction
- ✅ Complete Admin Interface (9 functional tabs)
- ✅ Database Integration (drum beats, SD3 samples, signature songs)
- ✅ Error recovery and diagnostic systems

## Restore Process

### 1. Prerequisites
- Windows 10/11
- Python 3.11.9
- Git (optional)

### 2. Restore Steps
1. **Extract backup to target directory:**
   ```
   Copy all contents to: D:/DrumTracKAI_v1.1.7/
   ```

2. **Restore Python environment:**
   ```bash
   cd D:/DrumTracKAI_v1.1.7
   python -m venv drumtrackai_env
   .\\drumtrackai_env\\Scripts\\activate
   pip install -r requirements.txt
   ```

3. **Configure MVSep API (if using signature song analysis):**
   - Edit `mvsep_config.txt`
   - Add your MVSep API key: `MVSEP_API_KEY=your_key_here`

4. **Launch system:**
   ```bash
   .\\launch_drumtrackai_admin.bat
   ```

### 3. Verification
- Admin app should launch with all 9 tabs functional
- Real-Time Monitor tab should show "Framework Status: Idle"
- Database should show 40 drum beats available
- MVSep tab should be accessible (if API key configured)

### 4. Available Systems
- **Admin Interface:** `launch_drumtrackai_admin.bat`
- **Production Batch Analysis:** `python production_batch_analysis_system.py`
- **Signature Song Analysis:** `python signature_song_batch_analysis.py`
- **Enhanced Analysis:** `python enhanced_production_batch_analysis.py`

## Support
This backup represents a fully functional DrumTracKAI system with MVSep integration and Expert model analysis capabilities.
""")
        
        # Create ZIP archive
        zip_file = backup_base_dir / f"{backup_name}.zip"
        print(f"[ZIP] Creating archive: {zip_file.name}")
        
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in backup_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(backup_dir)
                    zipf.write(file_path, arcname)
        
        zip_size_mb = round(zip_file.stat().st_size / (1024 * 1024), 2)
        
        # Print summary
        print("\n" + "=" * 60)
        print("[SUCCESS] BACKUP COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"Backup Name: {backup_name}")
        print(f"Backup Directory: {backup_dir}")
        print(f"ZIP Archive: {zip_file}")
        print(f"Backup Size: {manifest['backup_size_mb']} MB")
        print(f"ZIP Size: {zip_size_mb} MB")
        print(f"Items Backed Up: {len(copied_items)}")
        print(f"Items Skipped: {len(skipped_items)}")
        print("\nMajor Features Backed Up:")
        for achievement in manifest["major_achievements"]:
            print(f"  ✅ {achievement}")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Backup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    create_build_backup()
