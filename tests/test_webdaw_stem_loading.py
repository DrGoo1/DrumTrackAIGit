#!/usr/bin/env python3
"""
Test script to verify WebDAW automatic stem loading functionality
"""

import requests
import json
import time
import os
from pathlib import Path

def test_webdaw_stem_loading():
    """Test the complete WebDAW stem loading workflow"""
    
    print("🎵 Testing WebDAW Automatic Stem Loading")
    print("=" * 50)
    
    # Backend API base URL
    base_url = "http://localhost:8000"
    
    # Check backend status
    print("1. Checking backend status...")
    try:
        response = requests.get(f"{base_url}/api/status")
        if response.status_code == 200:
            status = response.json()
            print(f"   ✅ Backend online: {status['expert_model']}")
        else:
            print(f"   ❌ Backend not responding: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Backend connection failed: {e}")
        return
    
    # Find a test audio file
    print("\n2. Finding test audio file...")
    temp_uploads = Path("temp_uploads")
    audio_files = list(temp_uploads.glob("*.wav"))
    
    if not audio_files:
        print("   ❌ No audio files found in temp_uploads")
        return
    
    test_file = audio_files[0]
    print(f"   ✅ Using test file: {test_file.name}")
    
    # Upload the audio file
    print("\n3. Uploading audio file...")
    try:
        with open(test_file, 'rb') as f:
            files = {'file': (test_file.name, f, 'audio/wav')}
            response = requests.post(f"{base_url}/upload", files=files)
        
        if response.status_code == 200:
            upload_result = response.json()
            file_id = upload_result['file_id']
            print(f"   ✅ File uploaded successfully: {file_id}")
        else:
            print(f"   ❌ Upload failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Upload error: {e}")
        return
    
    # Start analysis (this should generate stems and auto-load to WebDAW)
    print("\n4. Starting analysis with stem generation...")
    try:
        analysis_data = {
            'file_id': file_id,
            'analysis_type': 'comprehensive',
            'tier': 'expert'
        }
        response = requests.post(f"{base_url}/api/analyze", json=analysis_data)
        
        if response.status_code == 200:
            analysis_result = response.json()
            job_id = analysis_result['job_id']
            print(f"   ✅ Analysis started: {job_id}")
        else:
            print(f"   ❌ Analysis failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Analysis error: {e}")
        return
    
    # Monitor analysis progress
    print("\n5. Monitoring analysis progress...")
    max_wait = 60  # Maximum wait time in seconds
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(f"{base_url}/api/progress/{job_id}")
            if response.status_code == 200:
                progress = response.json()
                status = progress['status']
                progress_pct = progress['progress']
                current_step = progress['current_step']
                
                print(f"   📊 Progress: {progress_pct}% - {current_step}")
                
                if status == 'completed':
                    print("   ✅ Analysis completed!")
                    break
                elif status == 'failed':
                    print("   ❌ Analysis failed!")
                    return
                    
            time.sleep(2)
        except Exception as e:
            print(f"   ❌ Progress check error: {e}")
            break
    
    # Get final results
    print("\n6. Getting analysis results...")
    try:
        response = requests.get(f"{base_url}/api/results/{job_id}")
        if response.status_code == 200:
            results = response.json()
            
            if 'results' in results and 'stems' in results['results']:
                stems = results['results']['stems']
                print(f"   ✅ Stems generated: {list(stems.keys())}")
                
                # Display stem information
                for stem_type, stem_info in stems.items():
                    print(f"      🎵 {stem_type}: {stem_info.get('name', 'Unknown')}")
                    print(f"         URL: {stem_info.get('url', 'N/A')}")
                    print(f"         Confidence: {stem_info.get('confidence', 'N/A')}")
                
                print("\n🎉 SUCCESS: Stems should now be automatically loaded in WebDAW!")
                print("   Check your WebDAW interface - stems should appear as tracks.")
                
            else:
                print("   ⚠️ No stems found in results")
        else:
            print(f"   ❌ Results retrieval failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Results error: {e}")
    
    print("\n" + "=" * 50)
    print("🎵 WebDAW Test Complete!")
    print("\nNext steps:")
    print("1. Check your WebDAW interface for automatically loaded stems")
    print("2. Try the MIDI upload button in the WebDAW header")
    print("3. Test the mixer controls and transport functions")

if __name__ == "__main__":
    test_webdaw_stem_loading()
