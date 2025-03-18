import os
import sys
import json
from drumtrackkit.services.youtube_service import YouTubeService

def test_youtube_download():
    print("Testing YouTube download functionality...")
    
    service = YouTubeService()
    try:
        # Test with a short drum video
        audio_path = service.download_audio(
            "https://www.youtube.com/watch?v=XZd9n373vf4",
            start_time=0,
            duration=10  # Just get 10 seconds for the test
        )
        print(f"SUCCESS: Downloaded audio to: {audio_path}")
        print(f"File exists: {os.path.exists(audio_path)}")
        print(f"File size: {os.path.getsize(audio_path)} bytes")
        
        # Test mock analysis
        analysis = service.generate_mock_analysis(audio_path, "performance")
        print(f"Mock analysis generated:")
        print(json.dumps(analysis, indent=2))
        
        return True
    except Exception as e:
        print(f"ERROR: Failed to download: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_youtube_download()
    sys.exit(0 if success else 1)
