"""
Test DrumTracKAI Complete System Integration
Tests the integration between MVSep batch processor and complete analysis system
"""

import sys
import os
import logging
from pathlib import Path

# Add admin directory to path
admin_dir = Path(__file__).parent / "admin"
if str(admin_dir) not in sys.path:
    sys.path.insert(0, str(admin_dir))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_complete_system_services():
    """Test that all complete system services can be imported and initialized"""
    print("=== Testing Complete System Services ===")
    
    # Test 1: DrumTracKAI Complete System
    try:
        from services.drumtrackai_complete_system import DrumTracKAICompleteSystem
        complete_system = DrumTracKAICompleteSystem()
        print("[SUCCESS] DrumTracKAI Complete System: OK")
    except Exception as e:
        print(f" DrumTracKAI Complete System: FAILED - {e}")
        return False
    
    # Test 2: Enhanced Visualization Service
    try:
        from services.enhanced_complete_visualization import get_enhanced_complete_visualization
        viz_service = get_enhanced_complete_visualization()
        print("[SUCCESS] Enhanced Visualization Service: OK")
    except Exception as e:
        print(f" Enhanced Visualization Service: FAILED - {e}")
        return False
    
    # Test 3: Batch Complete Integration
    try:
        from services.batch_complete_integration import get_batch_complete_integration
        integration_service = get_batch_complete_integration()
        print("[SUCCESS] Batch Complete Integration Service: OK")
    except Exception as e:
        print(f" Batch Complete Integration Service: FAILED - {e}")
        return False
    
    # Test 4: UI Integration Handler
    try:
        from ui.complete_system_integration_handler import get_complete_system_integration_handler
        ui_handler = get_complete_system_integration_handler()
        print("[SUCCESS] UI Integration Handler: OK")
    except Exception as e:
        print(f" UI Integration Handler: FAILED - {e}")
        return False
    
    return True

def test_integration_script():
    """Test the integration script"""
    print("\n=== Testing Integration Script ===")
    
    try:
        from integrate_complete_system import (
            integrate_complete_system_with_batch_processor,
            initialize_complete_system_services
        )
        
        # Test service initialization
        services_ok = initialize_complete_system_services()
        print(f"[SUCCESS] Service Initialization: {'OK' if services_ok else 'FAILED'}")
        
        # Test integration function loading
        integration_func = integrate_complete_system_with_batch_processor()
        integration_ok = integration_func is not None
        print(f"[SUCCESS] Integration Function: {'OK' if integration_ok else 'FAILED'}")
        
        return services_ok and integration_ok
        
    except Exception as e:
        print(f" Integration Script: FAILED - {e}")
        return False

def test_mock_mvsep_completion():
    """Test complete analysis with mock MVSep output"""
    print("\n=== Testing Mock MVSep Completion ===")
    
    try:
        from services.batch_complete_integration import get_batch_complete_integration
        
        # Initialize service
        integration_service = get_batch_complete_integration()
        if not integration_service.initialize():
            print(" Failed to initialize integration service")
            return False
        
        # Create mock MVSep result
        mock_result = {
            'source_file': 'test_song.wav',
            'output_files': {
                'drums': 'test_song_drums.wav',
                'bass': 'test_song_bass.wav',
                'vocals': 'test_song_vocals.wav',
                'other': 'test_song_other.wav'
            },
            'job_id': 'test_job_123',
            'metadata': {
                'tempo': 120,
                'style': 'rock',
                'drummer_id': 'test_drummer',
                'track_name': 'test_song'
            }
        }
        
        # Test processing (this will fail because files don't exist, but should not crash)
        success = integration_service.process_mvsep_output(mock_result)
        print(f"[SUCCESS] Mock Processing: {'OK' if success else 'EXPECTED FAILURE (files missing)'}")
        
        return True
        
    except Exception as e:
        print(f" Mock MVSep Completion: FAILED - {e}")
        return False

def test_visualization_generation():
    """Test visualization generation with mock data"""
    print("\n=== Testing Visualization Generation ===")
    
    try:
        from services.enhanced_complete_visualization import get_enhanced_complete_visualization
        
        viz_service = get_enhanced_complete_visualization()
        
        # Create mock analysis results
        mock_analysis = {
            'drummer_id': 'test_drummer',
            'track_name': 'test_song',
            'tempo_profile': {
                'average_tempo': 120,
                'tempo_stability': 0.85,
                'tempo_variations': 5
            },
            'groove_metrics': {
                'overall_groove_score': 0.78,
                'timing_tightness': 0.82,
                'dynamic_consistency': 0.75,
                'attack_consistency': 0.80,
                'groove_depth': 0.73
            },
            'rhythm_hierarchy': {
                'complexity_score': 0.65,
                'syncopation_score': 0.58,
                'hierarchical_depth': 3
            },
            'neural_entrainment': {
                'flow_state_compatibility': 0.72,
                'groove_induction_potential': 0.68,
                'phase_coherence': 0.81
            },
            'visualization_data': {
                'tempo_curve': {
                    'times': [0, 1, 2, 3, 4, 5],
                    'tempos': [118, 120, 122, 119, 121, 120]
                },
                'hit_timeline': {
                    'times': [0.5, 1.0, 1.5, 2.0, 2.5, 3.0],
                    'velocities': [0.8, 0.6, 0.9, 0.7, 0.85, 0.75],
                    'micro_timing': [-2, 1, -1, 3, 0, -1]
                },
                'style_radar': {
                    'categories': ['Complexity', 'Syncopation', 'Dynamics', 'Precision', 'Groove', 'Flow'],
                    'values': [0.65, 0.58, 0.75, 0.82, 0.78, 0.72]
                },
                'entrainment_spectrum': {
                    'frequencies': ['delta', 'theta', 'alpha', 'beta', 'gamma'],
                    'amplitudes': [0.2, 0.3, 0.4, 0.3, 0.1]
                }
            },
            'total_hits': 150,
            'analysis_duration': 45.2,
            'processing_method': 'Complete Integrated System'
        }
        
        # Generate visualization
        figure = viz_service.create_complete_analysis_visualization(mock_analysis)
        
        if figure:
            print("[SUCCESS] Visualization Generation: OK")
            return True
        else:
            print(" Visualization Generation: FAILED - No figure returned")
            return False
            
    except Exception as e:
        print(f" Visualization Generation: FAILED - {e}")
        return False

def main():
    """Run all integration tests"""
    print("DrumTracKAI Complete System Integration Test")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Test 1: Services
    services_ok = test_complete_system_services()
    all_tests_passed = all_tests_passed and services_ok
    
    # Test 2: Integration Script
    integration_ok = test_integration_script()
    all_tests_passed = all_tests_passed and integration_ok
    
    # Test 3: Mock Processing
    processing_ok = test_mock_mvsep_completion()
    all_tests_passed = all_tests_passed and processing_ok
    
    # Test 4: Visualization
    viz_ok = test_visualization_generation()
    all_tests_passed = all_tests_passed and viz_ok
    
    # Summary
    print("\n" + "=" * 50)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 50)
    print(f"Services: {'[SUCCESS] PASS' if services_ok else ' FAIL'}")
    print(f"Integration Script: {'[SUCCESS] PASS' if integration_ok else ' FAIL'}")
    print(f"Mock Processing: {'[SUCCESS] PASS' if processing_ok else ' FAIL'}")
    print(f"Visualization: {'[SUCCESS] PASS' if viz_ok else ' FAIL'}")
    print("-" * 50)
    print(f"OVERALL: {'[SUCCESS] ALL TESTS PASSED' if all_tests_passed else ' SOME TESTS FAILED'}")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
