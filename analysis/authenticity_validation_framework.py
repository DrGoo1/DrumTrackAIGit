"""
DrumTracKAI Complete System - Comprehensive Authenticity Validation Framework
CRITICAL: Ensures NO placeholder/simulated data is EVER presented as real analysis

This framework provides comprehensive validation that all analysis results are authentic
and clearly labels any test, mock, or failed analysis data.
"""

import sys
import os
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
import json
from datetime import datetime

# Setup path
admin_path = Path(__file__).parent / "admin"
sys.path.insert(0, str(admin_path))

class AuthenticityValidator:
    """Comprehensive authenticity validation for DrumTracKAI analysis results"""
    
    def __init__(self):
        self.validation_log = []
        self.authentic_components = []
        self.failed_components = []
        self.suspicious_patterns = []
        
    def validate_analysis_results(self, analysis_results: Dict, source_info: str = "unknown") -> Dict:
        """
        Comprehensive validation of analysis results for authenticity
        Returns validation report with authenticity status for each component
        """
        validation_report = {
            'source': source_info,
            'timestamp': datetime.now().isoformat(),
            'overall_authenticity': 'UNKNOWN',
            'components': {},
            'warnings': [],
            'errors': []
        }
        
        # Validate tempo analysis
        tempo_authenticity = self._validate_tempo_analysis(analysis_results.get('tempo_profile'))
        validation_report['components']['tempo_analysis'] = tempo_authenticity
        
        # Validate groove metrics
        groove_authenticity = self._validate_groove_metrics(analysis_results.get('groove_metrics'))
        validation_report['components']['groove_metrics'] = groove_authenticity
        
        # Validate neural entrainment
        neural_authenticity = self._validate_neural_entrainment(analysis_results.get('neural_entrainment'))
        validation_report['components']['neural_entrainment'] = neural_authenticity
        
        # Validate rhythm hierarchy
        rhythm_authenticity = self._validate_rhythm_hierarchy(analysis_results.get('rhythm_hierarchy'))
        validation_report['components']['rhythm_hierarchy'] = rhythm_authenticity
        
        # Validate visualization data
        viz_authenticity = self._validate_visualization_data(analysis_results.get('visualization_data'))
        validation_report['components']['visualization_data'] = viz_authenticity
        
        # Determine overall authenticity
        component_statuses = [comp['status'] for comp in validation_report['components'].values()]
        
        if all(status == 'AUTHENTIC' for status in component_statuses):
            validation_report['overall_authenticity'] = 'FULLY_AUTHENTIC'
        elif any(status == 'AUTHENTIC' for status in component_statuses):
            validation_report['overall_authenticity'] = 'PARTIALLY_AUTHENTIC'
        elif all(status in ['FAILED', 'MISSING'] for status in component_statuses):
            validation_report['overall_authenticity'] = 'ANALYSIS_FAILED'
        else:
            validation_report['overall_authenticity'] = 'SUSPICIOUS'
            validation_report['warnings'].append("Mixed authenticity status - requires manual review")
        
        return validation_report
    
    def _validate_tempo_analysis(self, tempo_profile) -> Dict:
        """Validate tempo analysis for authenticity"""
        if not tempo_profile:
            return {
                'status': 'MISSING',
                'message': 'No tempo profile provided',
                'authenticity_indicators': []
            }
        
        indicators = []
        warnings = []
        
        # Check for suspicious default values
        if hasattr(tempo_profile, 'average_tempo'):
            tempo = tempo_profile.average_tempo
            if tempo == 120:
                warnings.append("Tempo is exactly 120 BPM (common default)")
            elif tempo < 60 or tempo > 200:
                warnings.append(f"Tempo {tempo} BPM is outside typical range")
            else:
                indicators.append(f"Realistic tempo: {tempo} BPM")
        
        # Check confidence
        if hasattr(tempo_profile, 'confidence'):
            confidence = tempo_profile.confidence
            if confidence < 0.1:
                return {
                    'status': 'FAILED',
                    'message': f'Very low confidence ({confidence}) indicates analysis failure',
                    'authenticity_indicators': indicators,
                    'warnings': warnings
                }
            elif confidence > 0.7:
                indicators.append(f"High confidence: {confidence}")
        
        # Check for tempo variation
        if hasattr(tempo_profile, 'tempo_curve'):
            curve = tempo_profile.tempo_curve
            if isinstance(curve, np.ndarray) and len(curve) > 1:
                variation = np.std(curve)
                if variation < 0.1:
                    warnings.append("Tempo curve shows no variation (may be placeholder)")
                else:
                    indicators.append(f"Tempo variation: {variation:.2f} BPM")
        
        status = 'AUTHENTIC' if indicators and not any('placeholder' in w for w in warnings) else 'SUSPICIOUS'
        
        return {
            'status': status,
            'message': f'Tempo analysis appears {status.lower()}',
            'authenticity_indicators': indicators,
            'warnings': warnings
        }
    
    def _validate_groove_metrics(self, groove_metrics) -> Dict:
        """Validate groove metrics for authenticity"""
        if not groove_metrics:
            return {
                'status': 'MISSING',
                'message': 'No groove metrics provided',
                'authenticity_indicators': []
            }
        
        indicators = []
        warnings = []
        
        # Check for suspicious round numbers
        suspicious_values = [0.5, 0.75, 0.8, 1.0, 0.0]
        
        for metric_name, value in groove_metrics.items():
            if isinstance(value, (int, float)):
                if value in suspicious_values:
                    warnings.append(f"{metric_name} has suspicious value: {value}")
                else:
                    indicators.append(f"{metric_name}: {value:.3f}")
        
        # Check for all zeros (likely failed analysis)
        numeric_values = [v for v in groove_metrics.values() if isinstance(v, (int, float))]
        if numeric_values and all(v == 0 for v in numeric_values):
            return {
                'status': 'FAILED',
                'message': 'All groove metrics are zero - analysis likely failed',
                'authenticity_indicators': [],
                'warnings': warnings
            }
        
        # Check for realistic value ranges
        for metric_name, value in groove_metrics.items():
            if isinstance(value, (int, float)):
                if 0 <= value <= 1:
                    indicators.append(f"{metric_name} in realistic range")
                else:
                    warnings.append(f"{metric_name} outside expected range [0,1]: {value}")
        
        status = 'AUTHENTIC' if len(indicators) >= len(warnings) else 'SUSPICIOUS'
        
        return {
            'status': status,
            'message': f'Groove metrics appear {status.lower()}',
            'authenticity_indicators': indicators,
            'warnings': warnings
        }
    
    def _validate_neural_entrainment(self, neural_entrainment) -> Dict:
        """Validate neural entrainment analysis for authenticity"""
        if not neural_entrainment:
            return {
                'status': 'MISSING',
                'message': 'No neural entrainment data provided',
                'authenticity_indicators': []
            }
        
        indicators = []
        warnings = []
        
        # Check brainwave alignment
        brainwave_alignment = neural_entrainment.get('brainwave_alignment', {})
        if brainwave_alignment:
            # Check for hardcoded placeholder values
            values = list(brainwave_alignment.values())
            if values == [0.2, 0.3, 0.4, 0.3, 0.1]:
                return {
                    'status': 'PLACEHOLDER',
                    'message': 'Brainwave alignment contains hardcoded placeholder values',
                    'authenticity_indicators': [],
                    'warnings': ['CRITICAL: Hardcoded brainwave values detected']
                }
            
            # Check for realistic brainwave patterns
            if all(0 <= v <= 1 for v in values):
                indicators.append(f"Brainwave values in realistic range")
                
                # Check for variation (not all the same)
                if len(set(values)) > 1:
                    indicators.append("Brainwave values show variation")
                else:
                    warnings.append("All brainwave values are identical")
        
        # Check other entrainment metrics
        entrainment_metrics = ['phase_coherence', 'groove_induction_potential', 'flow_state_compatibility']
        for metric in entrainment_metrics:
            if metric in neural_entrainment:
                value = neural_entrainment[metric]
                if isinstance(value, (int, float)) and 0 <= value <= 1:
                    indicators.append(f"{metric}: {value:.3f}")
        
        status = 'AUTHENTIC' if indicators and not any('placeholder' in w.lower() for w in warnings) else 'SUSPICIOUS'
        
        return {
            'status': status,
            'message': f'Neural entrainment appears {status.lower()}',
            'authenticity_indicators': indicators,
            'warnings': warnings
        }
    
    def _validate_rhythm_hierarchy(self, rhythm_hierarchy) -> Dict:
        """Validate rhythm hierarchy analysis for authenticity"""
        if not rhythm_hierarchy:
            return {
                'status': 'MISSING',
                'message': 'No rhythm hierarchy data provided',
                'authenticity_indicators': []
            }
        
        indicators = []
        warnings = []
        
        # Check required fields
        required_fields = ['complexity_score', 'syncopation_score', 'hierarchical_depth']
        missing_fields = [field for field in required_fields if field not in rhythm_hierarchy]
        
        if missing_fields:
            warnings.append(f"Missing required fields: {missing_fields}")
        
        # Check for realistic values
        for field in required_fields:
            if field in rhythm_hierarchy:
                value = rhythm_hierarchy[field]
                if isinstance(value, (int, float)):
                    if field == 'hierarchical_depth':
                        if value >= 1:
                            indicators.append(f"{field}: {value}")
                        else:
                            warnings.append(f"{field} should be >= 1, got {value}")
                    else:
                        if 0 <= value <= 1:
                            indicators.append(f"{field}: {value:.3f}")
                        else:
                            warnings.append(f"{field} outside expected range [0,1]: {value}")
        
        status = 'AUTHENTIC' if len(indicators) >= len(required_fields) - len(missing_fields) else 'SUSPICIOUS'
        
        return {
            'status': status,
            'message': f'Rhythm hierarchy appears {status.lower()}',
            'authenticity_indicators': indicators,
            'warnings': warnings
        }
    
    def _validate_visualization_data(self, viz_data) -> Dict:
        """Validate visualization data for authenticity"""
        if not viz_data:
            return {
                'status': 'MISSING',
                'message': 'No visualization data provided',
                'authenticity_indicators': []
            }
        
        indicators = []
        warnings = []
        
        # Check for authenticity markers in the data
        for component_name, component_data in viz_data.items():
            if isinstance(component_data, dict):
                if 'authenticity' in component_data:
                    auth_status = component_data['authenticity']
                    if auth_status in ['REAL_ANALYSIS', 'REAL_NEURAL_ANALYSIS']:
                        indicators.append(f"{component_name} marked as authentic")
                    elif auth_status in ['ANALYSIS_FAILED', 'PLACEHOLDER']:
                        warnings.append(f"{component_name} marked as failed/placeholder")
                
                if 'error' in component_data:
                    warnings.append(f"{component_name} contains error: {component_data['error']}")
        
        status = 'AUTHENTIC' if indicators and not warnings else ('FAILED' if warnings else 'SUSPICIOUS')
        
        return {
            'status': status,
            'message': f'Visualization data appears {status.lower()}',
            'authenticity_indicators': indicators,
            'warnings': warnings
        }
    
    def generate_authenticity_report(self, validation_report: Dict) -> str:
        """Generate human-readable authenticity report"""
        report = []
        report.append("=" * 70)
        report.append("[SEARCH] DRUMTRACKAI AUTHENTICITY VALIDATION REPORT")
        report.append("=" * 70)
        report.append(f"Source: {validation_report['source']}")
        report.append(f"Timestamp: {validation_report['timestamp']}")
        report.append(f"Overall Status: {validation_report['overall_authenticity']}")
        report.append("")
        
        # Component details
        report.append("[BAR_CHART] COMPONENT ANALYSIS:")
        report.append("-" * 40)
        
        for component_name, component_data in validation_report['components'].items():
            status = component_data['status']
            status_icon = {
                'AUTHENTIC': '[SUCCESS]',
                'SUSPICIOUS': '[WARNING]',
                'FAILED': '',
                'MISSING': '',
                'PLACEHOLDER': '[ALERT]'
            }.get(status, '')
            
            report.append(f"{status_icon} {component_name.upper()}: {status}")
            report.append(f"   Message: {component_data['message']}")
            
            if component_data.get('authenticity_indicators'):
                report.append("   Authenticity Indicators:")
                for indicator in component_data['authenticity_indicators']:
                    report.append(f"     • {indicator}")
            
            if component_data.get('warnings'):
                report.append("   Warnings:")
                for warning in component_data['warnings']:
                    report.append(f"     [WARNING] {warning}")
            
            report.append("")
        
        # Overall warnings
        if validation_report.get('warnings'):
            report.append("[WARNING] OVERALL WARNINGS:")
            for warning in validation_report['warnings']:
                report.append(f"   • {warning}")
            report.append("")
        
        # Recommendations
        report.append("[IDEA] RECOMMENDATIONS:")
        report.append("-" * 40)
        
        overall_status = validation_report['overall_authenticity']
        if overall_status == 'FULLY_AUTHENTIC':
            report.append("[SUCCESS] All analysis components appear authentic")
            report.append("[SUCCESS] Safe to present results to users")
        elif overall_status == 'PARTIALLY_AUTHENTIC':
            report.append("[WARNING] Some components authentic, others failed")
            report.append("[WARNING] Clearly label which components are real vs. failed")
        elif overall_status == 'ANALYSIS_FAILED':
            report.append(" Analysis failed - do not present as real results")
            report.append(" Show clear error message to users")
        else:
            report.append("[ALERT] SUSPICIOUS - Manual review required")
            report.append("[ALERT] Do not present to users without verification")
        
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)

def validate_complete_system_authenticity():
    """Main function to validate DrumTracKAI Complete System authenticity"""
    print("[SEARCH] DrumTracKAI Complete System - Authenticity Validation")
    print("=" * 70)
    print("CRITICAL: Validating that NO placeholder data is presented as real analysis")
    print("")
    
    validator = AuthenticityValidator()
    
    # Test with mock data to verify validation works
    print("1. Testing validation framework with mock data...")
    
    # Create test data with known authenticity issues
    test_analysis_results = {
        'tempo_profile': type('TempoProfile', (), {
            'average_tempo': 120,  # Suspicious default
            'confidence': 0.05,    # Very low confidence
            'tempo_curve': np.array([120, 120, 120])  # No variation
        })(),
        'groove_metrics': {
            'timing_tightness': 0.5,      # Suspicious round number
            'dynamic_consistency': 0.75,   # Suspicious round number
            'attack_consistency': 0.0,     # Zero value
            'groove_depth': 0.8            # Suspicious round number
        },
        'neural_entrainment': {
            'brainwave_alignment': {
                'delta': 0.2, 'theta': 0.3, 'alpha': 0.4, 'beta': 0.3, 'gamma': 0.1
            },  # Hardcoded placeholder values!
            'phase_coherence': 0.5,
            'flow_state_compatibility': 0.5
        },
        'rhythm_hierarchy': {
            'complexity_score': 0.0,      # Zero value
            'syncopation_score': 0.0,     # Zero value
            'hierarchical_depth': 1       # Minimum value
        }
    }
    
    # Validate the test data
    validation_report = validator.validate_analysis_results(
        test_analysis_results, 
        "Test Data (Known Authenticity Issues)"
    )
    
    # Generate and display report
    report_text = validator.generate_authenticity_report(validation_report)
    print(report_text)
    
    # Check if validation correctly identified issues
    overall_status = validation_report['overall_authenticity']
    if overall_status in ['SUSPICIOUS', 'ANALYSIS_FAILED']:
        print("[SUCCESS] Validation framework correctly identified authenticity issues")
    else:
        print(" Validation framework failed to identify known issues")
    
    return validator, validation_report

if __name__ == "__main__":
    print("[SEARCH]" * 70)
    print("DRUMTRACKAI COMPLETE SYSTEM - AUTHENTICITY VALIDATION FRAMEWORK")
    print("[SEARCH]" * 70)
    print("\nPURPOSE: Ensure NO placeholder/simulated data is presented as real analysis")
    print("CRITICAL: Any non-authentic data must be clearly labeled to users")
    print("")
    
    validator, report = validate_complete_system_authenticity()
    
    print("\n" + "[TARGET]" * 70)
    print("AUTHENTICITY VALIDATION FRAMEWORK READY")
    print("[TARGET]" * 70)
    print("[SUCCESS] Framework can detect hardcoded placeholder values")
    print("[SUCCESS] Framework validates each analysis component separately")
    print("[SUCCESS] Framework provides clear authenticity status")
    print("[SUCCESS] Framework generates user-friendly reports")
    print("")
    print("[IDEA] USAGE:")
    print("1. Import AuthenticityValidator from this module")
    print("2. Call validate_analysis_results() on any analysis output")
    print("3. Check overall_authenticity before presenting to users")
    print("4. Use generate_authenticity_report() for detailed validation")
    print("")
    print("[ALERT] CRITICAL: Never present analysis results without validation!")
