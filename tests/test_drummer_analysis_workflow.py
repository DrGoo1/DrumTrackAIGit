"""
Test the complete drummer analysis workflow from stems to personality profile
"""

import os
import sys
import json
import logging
from pathlib import Path

# Add admin directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'admin'))

from services.advanced_drummer_analysis import AdvancedDrummerAnalysis, DrummerProfile

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_drummer_analysis_workflow():
    """Test the complete drummer analysis workflow"""
    
    print("=" * 80)
    print("ADVANCED DRUMMER ANALYSIS WORKFLOW TEST")
    print("=" * 80)
    
    # Test configuration
    test_config = {
        "tempo": 140.0,
        "style": "rock",
        "key": "E",
        "test_name": "Jeff Porcaro - Rosanna Style Analysis"
    }
    
    print(f"\n[AUDIO] Testing: {test_config['test_name']}")
    print(f"Context: {test_config['tempo']} BPM, {test_config['style']}, Key of {test_config['key']}")
    print("-" * 60)
    
    try:
        # Initialize the advanced drummer analysis system
        analyzer = AdvancedDrummerAnalysis(sample_rate=22050)
        
        # For demonstration, we'll create mock stem files
        # In the real workflow, these would come from MVSep DrumSep processing
        mock_stem_files = create_mock_drum_stems(test_config)
        
        print("[FOLDER] Mock Drum Stems Created:")
        for component, file_path in mock_stem_files.items():
            print(f"  {component}: {file_path}")
        
        # Perform comprehensive drummer analysis
        print("\n[SEARCH] Performing Advanced Drummer Analysis...")
        drummer_profile = analyzer.analyze_drummer_performance(
            stem_files=mock_stem_files,
            tempo=test_config["tempo"],
            style=test_config["style"],
            key=test_config["key"]
        )
        
        # Display comprehensive results
        display_drummer_analysis_results(drummer_profile)
        
        # Save the profile
        output_file = "test_drummer_profile.json"
        success = analyzer.save_profile(drummer_profile, output_file)
        
        if success:
            print(f"\n[SAVE] Drummer profile saved to: {output_file}")
            
            # Load and display saved profile structure
            with open(output_file, 'r') as f:
                saved_profile = json.load(f)
            
            print("\n[BAR_CHART] Saved Profile Structure:")
            display_profile_structure(saved_profile)
        else:
            print("\n Failed to save drummer profile")
        
        # Demonstrate how this integrates with the admin app workflow
        print("\n" + "=" * 60)
        print("INTEGRATION WITH ADMIN APP WORKFLOW")
        print("=" * 60)
        
        print("""
[REFRESH] Complete Workflow Integration:

1. USER SELECTS DRUMMER & SONG
    Drummers Tab → Jeff Porcaro → "Rosanna"

2. ARRANGEMENT ANALYSIS PHASE
    Download YouTube audio
    Analyze tempo, key, musical sections
    Results: tempo=140 BPM, key=E, sections detected

3. MVSEP PROCESSING PHASE
    Send audio to MVSep API
    HTDemucs: separate vocals, drums, bass, other
    DrumSep: separate kick, snare, toms, hihat, crash, ride

4. ADVANCED DRUMMER ANALYSIS PHASE [STAR] (NEW!)
    Analyze each drum component for hits, timing, dynamics
    Extract groove characteristics and human nuances
    Identify signature patterns and playing style
    Calculate personality traits and technical metrics
    Generate comprehensive drummer profile

5. RESULTS & PROFILING
    Save detailed drummer profile JSON
    Display humanness score, timing characteristics
    Show personality traits (aggressiveness, precision, creativity)
    Ready for AI drummer reproduction and training
        """)
        
        print("\n[SUCCESS] WORKFLOW TEST COMPLETED SUCCESSFULLY")
        
    except Exception as e:
        print(f"\n Error in drummer analysis workflow: {e}")
        import traceback
        traceback.print_exc()

def create_mock_drum_stems(config):
    """Create mock drum stem files for testing"""
    import numpy as np
    import soundfile as sf
    
    # Create test directory
    test_dir = "test_stems"
    os.makedirs(test_dir, exist_ok=True)
    
    # Audio parameters
    sr = 22050
    duration = 10.0  # 10 seconds
    tempo = config["tempo"]
    beat_interval = 60.0 / tempo
    
    t = np.linspace(0, duration, int(sr * duration))
    stem_files = {}
    
    # Create kick drum stem (on beats 1 and 3)
    kick_audio = np.zeros_like(t)
    for beat_time in np.arange(0, duration, beat_interval * 2):  # Every 2 beats
        if beat_time < duration:
            beat_sample = int(beat_time * sr)
            if beat_sample < len(kick_audio):
                # Create kick sound (low frequency thump)
                kick_duration = 0.1
                kick_samples = int(kick_duration * sr)
                if beat_sample + kick_samples < len(kick_audio):
                    kick_t = np.linspace(0, kick_duration, kick_samples)
                    kick_sound = np.sin(2 * np.pi * 60 * kick_t) * np.exp(-kick_t * 15)
                    kick_audio[beat_sample:beat_sample + kick_samples] += kick_sound
    
    kick_file = os.path.join(test_dir, "kick.wav")
    sf.write(kick_file, kick_audio, sr)
    stem_files["kick"] = kick_file
    
    # Create snare drum stem (on beats 2 and 4)
    snare_audio = np.zeros_like(t)
    for beat_time in np.arange(beat_interval, duration, beat_interval * 2):  # Beats 2, 4, 6, 8...
        if beat_time < duration:
            beat_sample = int(beat_time * sr)
            if beat_sample < len(snare_audio):
                # Create snare sound (noise burst)
                snare_duration = 0.05
                snare_samples = int(snare_duration * sr)
                if beat_sample + snare_samples < len(snare_audio):
                    snare_sound = np.random.normal(0, 0.5, snare_samples) * np.exp(-np.linspace(0, snare_duration, snare_samples) * 20)
                    snare_audio[beat_sample:beat_sample + snare_samples] += snare_sound
    
    snare_file = os.path.join(test_dir, "snare.wav")
    sf.write(snare_file, snare_audio, sr)
    stem_files["snare"] = snare_file
    
    # Create hi-hat stem (8th notes with slight variations)
    hihat_audio = np.zeros_like(t)
    eighth_interval = beat_interval / 2
    for beat_time in np.arange(0, duration, eighth_interval):
        if beat_time < duration:
            # Add slight timing variations for humanness
            variation = np.random.normal(0, 0.01)  # ±10ms variation
            actual_time = beat_time + variation
            
            if 0 <= actual_time < duration:
                beat_sample = int(actual_time * sr)
                if beat_sample < len(hihat_audio):
                    # Create hi-hat sound (high frequency click)
                    hihat_duration = 0.02
                    hihat_samples = int(hihat_duration * sr)
                    if beat_sample + hihat_samples < len(hihat_audio):
                        hihat_t = np.linspace(0, hihat_duration, hihat_samples)
                        hihat_sound = np.random.normal(0, 0.2, hihat_samples) * np.exp(-hihat_t * 50)
                        # Add velocity variations
                        velocity = 0.7 + np.random.normal(0, 0.2)
                        velocity = max(0.3, min(1.0, velocity))
                        hihat_audio[beat_sample:beat_sample + hihat_samples] += hihat_sound * velocity
    
    hihat_file = os.path.join(test_dir, "hihat.wav")
    sf.write(hihat_file, hihat_audio, sr)
    stem_files["hihat"] = hihat_file
    
    return stem_files

def display_drummer_analysis_results(profile: DrummerProfile):
    """Display comprehensive drummer analysis results"""
    
    print("\n" + "=" * 60)
    print("[DRUMS] DRUMMER PERFORMANCE ANALYSIS RESULTS")
    print("=" * 60)
    
    # Basic info
    print(f"\n[BAR_CHART] BASIC INFORMATION")
    print(f"Tempo: {profile.tempo} BPM")
    print(f"Style: {profile.style}")
    print(f"Key: {profile.key}")
    print(f"Duration: {profile.duration:.1f} seconds")
    
    # Component analysis
    print(f"\n[AUDIO] COMPONENT ANALYSIS")
    print(f"Components Analyzed: {len(profile.components)}")
    for name, component in profile.components.items():
        print(f"  {name.upper()}:")
        print(f"    Hits Detected: {len(component.hits)}")
        print(f"    Avg Velocity: {np.mean(component.velocities):.3f}" if component.velocities else "    No velocity data")
        print(f"    Timing Variance: {np.std(component.timing_deviations):.1f}ms" if component.timing_deviations else "    No timing data")
    
    # Groove analysis
    print(f"\n[MUSIC] GROOVE CHARACTERISTICS")
    groove = profile.groove
    print(f"Swing Factor: {groove.swing_factor:.3f} (0=straight, 1=full swing)")
    print(f"Pocket Tightness: {groove.pocket_tightness:.3f} (0=loose, 1=tight)")
    print(f"Rhythmic Complexity: {groove.rhythmic_complexity:.3f} (0=simple, 1=complex)")
    print(f"Syncopation Level: {groove.syncopation_level:.3f} (0=on-beat, 1=syncopated)")
    print(f"Micro-timing Variance: {groove.micro_timing_variance:.1f}ms")
    print(f"Humanness Score: {groove.humanness_score:.3f} (0=machine, 1=human)")
    
    # Personality traits
    if profile.personality_traits:
        print(f"\n[AI] PERSONALITY TRAITS")
        for trait, value in profile.personality_traits.items():
            trait_name = trait.replace('_', ' ').title()
            print(f"{trait_name}: {value:.3f}")
    
    # Technical metrics
    if profile.technical_metrics:
        print(f"\n[SETTINGS] TECHNICAL METRICS")
        for metric, value in profile.technical_metrics.items():
            metric_name = metric.replace('_', ' ').title()
            print(f"{metric_name}: {value:.3f}")
    
    # Signature patterns
    if profile.signature_patterns:
        print(f"\n[ART] SIGNATURE PATTERNS ({len(profile.signature_patterns)} found)")
        for i, pattern in enumerate(profile.signature_patterns[:3]):  # Show first 3
            print(f"  Pattern {i+1}: {pattern.get('type', 'unknown')} - {pattern.get('description', 'N/A')}")
    
    # Component interactions
    if profile.interaction_matrix:
        print(f"\n[LINK] COMPONENT INTERACTIONS")
        components = list(profile.interaction_matrix.keys())
        for comp1 in components:
            interactions = []
            for comp2 in components:
                if comp1 != comp2:
                    interaction = profile.interaction_matrix[comp1].get(comp2, 0)
                    if interaction > 0.3:  # Only show significant interactions
                        interactions.append(f"{comp2}({interaction:.2f})")
            if interactions:
                print(f"  {comp1.upper()} interacts with: {', '.join(interactions)}")

def display_profile_structure(profile_dict):
    """Display the structure of the saved profile"""
    
    def print_dict_structure(d, indent=0):
        for key, value in d.items():
            if isinstance(value, dict):
                print("  " * indent + f"{key}: (dict with {len(value)} keys)")
                if indent < 2:  # Limit depth
                    print_dict_structure(value, indent + 1)
            elif isinstance(value, list):
                print("  " * indent + f"{key}: (list with {len(value)} items)")
            else:
                print("  " * indent + f"{key}: {type(value).__name__}")
    
    print_dict_structure(profile_dict)

if __name__ == "__main__":
    test_drummer_analysis_workflow()
