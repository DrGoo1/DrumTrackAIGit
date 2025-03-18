#!/usr/bin/env python3
# drum_analysis/purpose/purpose_based.py - Enhanced Purpose-Based Analyzer

from typing import Dict, List, Any, Optional
import numpy as np
from drumtrackkit.drum_analysis.instruments.kick import KickAnalyzer
from drumtrackkit.drum_analysis.instruments.snare import SnareAnalyzer
from drumtrackkit.drum_analysis.instruments.cymbal import CymbalAnalyzer
from drumtrackkit.drum_analysis.instruments.tom import TomAnalyzer


class PurposeBasedAnalyzer:
    """
    Enhanced Purpose-Based Analyzer for DrumTracKAI

    Analyzes drum performances based on their musical purpose (grooves, fills, etc.)
    by integrating results from the specialized instrument analyzers.
    """

    def __init__(self):
        """Initialize the purpose-based analyzer with specialized instrument analyzers"""
        self.kick_analyzer = KickAnalyzer()
        self.snare_analyzer = SnareAnalyzer()
        self.cymbal_analyzer = CymbalAnalyzer()
        self.tom_analyzer = TomAnalyzer()

    def _get_individual_analyses(self, data):
        """
        Run individual analyses for each instrument

        Args:
            data (dict): Dictionary containing audio data for each instrument
                         and sample rate (sr)

        Returns:
            dict: Dictionary of analysis results for each instrument
        """
        analyses = {}

        # Extract sample rate from data
        sr = data.get('sr', 44100)  # Default to 44.1 kHz if not provided

        # For each instrument, check if data is provided and run the appropriate analyzer
        if 'kick' in data:
            if isinstance(data['kick'], np.ndarray):
                # Raw audio data
                analyses['kick'] = self.kick_analyzer.analyze(data['kick'], sr=sr)
            else:
                # Feature dictionary (for backwards compatibility)
                analyses['kick'] = self.kick_analyzer.analyze(np.zeros(1000), sr=sr)  # Placeholder

        if 'snare' in data:
            if isinstance(data['snare'], np.ndarray):
                # Raw audio data
                analyses['snare'] = self.snare_analyzer.analyze(data['snare'], sr=sr)
            else:
                # Feature dictionary (for backwards compatibility)
                analyses['snare'] = self.snare_analyzer.analyze(np.zeros(1000), sr=sr)  # Placeholder

        if 'cymbal' in data:
            if isinstance(data['cymbal'], np.ndarray):
                # Raw audio data
                analyses['cymbal'] = self.cymbal_analyzer.analyze(data['cymbal'], sr=sr)
            else:
                # Feature dictionary (for backwards compatibility)
                analyses['cymbal'] = self.cymbal_analyzer.analyze(np.zeros(1000), sr=sr)  # Placeholder

        if 'tom' in data:
            if isinstance(data['tom'], np.ndarray):
                # Raw audio data
                analyses['tom'] = self.tom_analyzer.analyze(data['tom'], sr=sr)
            else:
                # Feature dictionary (for backwards compatibility)
                analyses['tom'] = self.tom_analyzer.analyze(np.zeros(1000), sr=sr)  # Placeholder

        return analyses

    def analyze_groove(self, data):
        """
        Analyze a drum groove using enhanced instrument analyzers

        Args:
            data (dict): Dictionary containing audio data for each instrument

        Returns:
            dict: Analysis results for the groove
        """
        # Get individual instrument analyses
        instrument_analyses = self._get_individual_analyses(data)

        # Calculate groove metrics
        groove_consistency = self._calculate_groove_consistency(data, instrument_analyses)
        timing_quality = self._calculate_timing_quality(data, instrument_analyses)
        dynamic_balance = self._calculate_dynamic_balance(data, instrument_analyses)

        # Integrate features from specialized analyzers
        kick_technique = instrument_analyses.get('kick', {}).get('playing_technique', 'N/A')

        # Create ghost_notes dictionary based on hit_strength (lower hit_strength indicates ghost notes)
        snare_hit_strength = instrument_analyses.get('snare', {}).get('hit_strength', 1.0)
        snare_ghost_notes = {
            'detected': snare_hit_strength < 0.5,
            'quality': 1.0 - snare_hit_strength if snare_hit_strength < 0.5 else 0.0
        }

        # Extract cymbal type directly
        cymbal_type = instrument_analyses.get('cymbal', {}).get('cymbal_type', 'N/A')

        # Create comprehensive groove analysis
        groove_analysis = {
            'groove_consistency': groove_consistency,
            'timing_quality': timing_quality,
            'dynamic_balance': dynamic_balance,
            'kick_technique': kick_technique,
            'ghost_notes': snare_ghost_notes,
            'cymbal_type': cymbal_type
        }

        return groove_analysis

    def analyze_fill(self, data):
        """
        Analyze a drum fill using enhanced instrument analyzers

        Args:
            data (dict): Dictionary containing audio data for each instrument

        Returns:
            dict: Analysis results for the fill
        """
        # Get individual instrument analyses
        instrument_analyses = self._get_individual_analyses(data)

        # Calculate fill metrics
        complexity = self._calculate_fill_complexity(data, instrument_analyses)
        execution_quality = self._calculate_execution_quality(data, instrument_analyses)
        creativity_score = self._calculate_creativity_score(data, instrument_analyses)

        # Integrate features from specialized analyzers
        tom_resonance = instrument_analyses.get('tom', {}).get('resonance', 0.5)

        # Create rimshot detection based on snare hit_strength and tone_quality
        snare_hit_strength = instrument_analyses.get('snare', {}).get('hit_strength', 0.5)
        snare_tone_quality = instrument_analyses.get('snare', {}).get('tone_quality', 0.5)
        snare_rimshot = {
            'detected': snare_hit_strength > 0.8 and snare_tone_quality > 0.7,
            'consistency': min(snare_hit_strength, snare_tone_quality) if snare_hit_strength > 0.8 else 0.0
        }

        # Extract cymbal features
        cymbal_keys = list(instrument_analyses.get('cymbal', {}).keys())
        cymbal_sustain = 0.5  # Default value
        if 'spectral_rolloff' in cymbal_keys:
            # Approximate sustain quality from spectral rolloff (higher = better sustain)
            cymbal_sustain = min(1.0, instrument_analyses['cymbal']['spectral_rolloff'] / 5000.0)

        # Create comprehensive fill analysis
        fill_analysis = {
            'complexity': complexity,
            'execution_quality': execution_quality,
            'creativity_score': creativity_score,
            'tom_resonance': tom_resonance,
            'snare_rimshot': snare_rimshot,
            'cymbal_sustain': cymbal_sustain
        }

        return fill_analysis

    def comprehensive_analysis(self, data):
        """
        Perform a comprehensive analysis of a drum performance

        Args:
            data (dict): Dictionary containing audio data for each instrument

        Returns:
            dict: Comprehensive analysis results
        """
        # Get individual instrument analyses
        instrument_analyses = self._get_individual_analyses(data)

        # Perform purpose-based analyses
        groove_analysis = self.analyze_groove(data)
        fill_analysis = self.analyze_fill(data)

        # Generate learning suggestions
        learning_suggestions = self.generate_learning_suggestions(data)

        # Compile comprehensive results
        comprehensive_results = {
            'kick_analysis': instrument_analyses.get('kick', {}),
            'snare_analysis': instrument_analyses.get('snare', {}),
            'cymbal_analysis': instrument_analyses.get('cymbal', {}),
            'tom_analysis': instrument_analyses.get('tom', {}),
            'groove_analysis': groove_analysis,
            'fill_analysis': fill_analysis,
            'learning_suggestions': learning_suggestions
        }

        return comprehensive_results

    def generate_learning_suggestions(self, data):
        """
        Generate personalized learning suggestions based on analysis results

        Args:
            data (dict): Dictionary containing audio data for each instrument

        Returns:
            list: Personalized learning suggestions
        """
        # Get comprehensive analysis
        instrument_analyses = self._get_individual_analyses(data)

        suggestions = []

        # Generate kick drum suggestions
        if 'kick' in instrument_analyses:
            kick_analysis = instrument_analyses['kick']

            # Use technique_confidence for consistency assessment
            if kick_analysis.get('technique_confidence', 0) < 0.7:
                suggestions.append("Practice kick drum consistency with metronome exercises")

            # Check if rebound quality or power distribution is available
            if 'rebound_quality' in kick_analysis and kick_analysis['rebound_quality'] < 0.6:
                suggestions.append("Work on improving your kick drum rebound for better control")
            elif 'power_distribution' in kick_analysis and kick_analysis['power_distribution'] < 0.6:
                suggestions.append("Work on even power distribution in your kick technique")

            # Enhanced suggestion based on specific kick technique
            technique = kick_analysis.get('playing_technique', '')
            if technique == 'heel_down':
                suggestions.append("Consider practicing heel-toe technique for more power while maintaining control")
            elif technique == 'rebound':
                suggestions.append("Focus on controlled rebound exercises to improve dynamic range")

        # Generate snare drum suggestions
        if 'snare' in instrument_analyses:
            snare_analysis = instrument_analyses['snare']

            # Ghost note suggestions based on hit_strength
            hit_strength = snare_analysis.get('hit_strength', 0.8)
            if hit_strength < 0.5:
                suggestions.append("Work on consistency in your ghost notes for better grooves")
            elif hit_strength > 0.8:
                suggestions.append("Experiment with adding ghost notes to enhance your grooves")

            # Tone quality suggestions
            tone_quality = snare_analysis.get('tone_quality', 0.5)
            if tone_quality < 0.6:
                suggestions.append("Focus on strike technique for cleaner snare tone")

            # Technique suggestions
            technique = snare_analysis.get('playing_technique', '')
            if technique == 'center_hit':
                suggestions.append("Try rimshots for more powerful backbeats")

        # Generate cymbal suggestions
        if 'cymbal' in instrument_analyses:
            cymbal_analysis = instrument_analyses['cymbal']

            # Cymbal type suggestions
            cymbal_type = cymbal_analysis.get('cymbal_type', '')
            if cymbal_type == 'ride':
                suggestions.append("Practice ride cymbal patterns with varying dynamics to add interest")
            elif cymbal_type == 'crash':
                suggestions.append("Work on crash cymbal timing to enhance your accents")

                # Crash articulation suggestions
                crash_articulation = cymbal_analysis.get('crash_articulation', '')
                if crash_articulation == 'wash':
                    suggestions.append("Try more controlled crash hits for cleaner articulation")
                elif crash_articulation == 'choke':
                    suggestions.append("Experiment with letting your crashes ring out for more sustain")
            elif cymbal_type == 'hi_hat':
                suggestions.append("Experiment with different hi-hat openings for textural variety")

            # Sustain suggestions based on sustain_length
            sustain_length = cymbal_analysis.get('sustain_length', 0)
            if sustain_length < 0.0001:  # Arbitrary threshold, adjust as needed
                suggestions.append("Allow your cymbals to ring longer for better sustain and tone")

        # Generate tom suggestions
        if 'tom' in instrument_analyses:
            tom_analysis = instrument_analyses['tom']

            # Resonance suggestions
            resonance = tom_analysis.get('resonance', 0.5)
            if resonance < 0.6:
                suggestions.append("Check tom tuning for optimal resonance and practice clean striking technique")

            # Tom size suggestions
            tom_size = tom_analysis.get('tom_size', '')
            if tom_size:
                suggestions.append(f"Work on developing fills that emphasize the tonal quality of your {tom_size} toms")

        return suggestions

    def _calculate_groove_consistency(self, data, instrument_analyses):
        """Calculate groove consistency score based on timing and dynamics"""
        # For raw audio analysis, we rely on the instrument analyzers results
        instrument_consistency_scores = []

        if 'kick' in instrument_analyses and 'technique_confidence' in instrument_analyses['kick']:
            instrument_consistency_scores.append(instrument_analyses['kick']['technique_confidence'])

        if 'snare' in instrument_analyses and 'technique_confidence' in instrument_analyses['snare']:
            instrument_consistency_scores.append(instrument_analyses['snare']['technique_confidence'])

        # Average instrument consistency scores if available
        if instrument_consistency_scores:
            return sum(instrument_consistency_scores) / len(instrument_consistency_scores)

        # Default fallback if no useful data is available
        return 0.75

    def _calculate_timing_quality(self, data, instrument_analyses):
        """Calculate timing quality score based on precise hit timing"""
        # For raw audio analysis, estimate timing quality from available metrics

        # We can estimate timing quality based on technique confidence across instruments
        timing_scores = []

        if 'kick' in instrument_analyses and 'technique_confidence' in instrument_analyses['kick']:
            timing_scores.append(instrument_analyses['kick']['technique_confidence'])

        if 'snare' in instrument_analyses and 'technique_confidence' in instrument_analyses['snare']:
            timing_scores.append(instrument_analyses['snare']['technique_confidence'])

        if 'tom' in instrument_analyses and 'technique_confidence' in instrument_analyses['tom']:
            timing_scores.append(instrument_analyses['tom']['technique_confidence'])

        # Average timing scores if available
        if timing_scores:
            return sum(timing_scores) / len(timing_scores)

        # Default fallback if no useful data is available
        return 0.8

    def _calculate_dynamic_balance(self, data, instrument_analyses):
        """Calculate dynamic balance between instruments"""
        # Extract intensity/volume data for each instrument from the analyses
        instrument_intensities = {}

        if 'kick' in instrument_analyses and 'rms_energy' in instrument_analyses['kick']:
            instrument_intensities['kick'] = instrument_analyses['kick']['rms_energy']

        if 'snare' in instrument_analyses and 'rms_energy' in instrument_analyses['snare']:
            instrument_intensities['snare'] = instrument_analyses['snare']['rms_energy']

        if 'cymbal' in instrument_analyses and 'rms_energy' in instrument_analyses['cymbal']:
            instrument_intensities['cymbal'] = instrument_analyses['cymbal']['rms_energy']

        if 'tom' in instrument_analyses and 'rms_energy' in instrument_analyses['tom']:
            instrument_intensities['tom'] = instrument_analyses['tom']['rms_energy']

        # Need at least two instruments to calculate balance
        if len(instrument_intensities) >= 2:
            # Calculate standard deviation of instrument intensities
            values = list(instrument_intensities.values())
            mean_intensity = sum(values) / len(values)
            variance = sum((x - mean_intensity) ** 2 for x in values) / len(values)
            std_dev = variance ** 0.5

            # Calculate a balance score based on the standard deviation
            # A perfect balance would have std_dev = 0
            max_std_dev = 0.3  # Reasonable maximum for normalization
            std_dev_limited = min(max_std_dev, std_dev)
            balance_score = 1.0 - (std_dev_limited / max_std_dev)

            return balance_score

        # Default fallback if no useful data is available
        return 0.7

    def _calculate_fill_complexity(self, data, instrument_analyses):
        """Calculate complexity score for drum fills"""
        # For raw audio analysis, we estimate complexity from available metrics

        complexity_factors = []

        # Check for tom usage
        if 'tom' in instrument_analyses:
            tom_usage = 0.8  # Assume significant tom usage in fills
            complexity_factors.append(tom_usage)

        # Check for snare complexity based on technique confidence and hit strength
        if 'snare' in instrument_analyses:
            snare_complexity = (
                                       instrument_analyses['snare'].get('technique_confidence', 0.5) +
                                       instrument_analyses['snare'].get('hit_strength', 0.5)
                               ) / 2.0
            complexity_factors.append(snare_complexity)

        # Check for spectral variety in cymbals
        if 'cymbal' in instrument_analyses and 'spectral_bandwidth' in instrument_analyses['cymbal']:
            # Normalize spectral bandwidth to a 0-1 scale (assuming 5000 is a high value)
            cymbal_complexity = min(1.0, instrument_analyses['cymbal']['spectral_bandwidth'] / 5000.0)
            complexity_factors.append(cymbal_complexity)

        # Average complexity factors if available
        if complexity_factors:
            return sum(complexity_factors) / len(complexity_factors)

        # Default fallback if no useful data is available
        return 0.65

    def _calculate_execution_quality(self, data, instrument_analyses):
        """Calculate execution quality score for drum fills"""
        # Gather technique scores from instrument analyzers
        technique_scores = []

        if 'kick' in instrument_analyses and 'technique_confidence' in instrument_analyses['kick']:
            technique_scores.append(instrument_analyses['kick']['technique_confidence'])

        if 'snare' in instrument_analyses and 'technique_confidence' in instrument_analyses['snare']:
            technique_scores.append(instrument_analyses['snare']['technique_confidence'])

        if 'tom' in instrument_analyses and 'technique_confidence' in instrument_analyses['tom']:
            technique_scores.append(instrument_analyses['tom']['technique_confidence'])

        # Calculate average technique score if available
        if technique_scores:
            execution_score = sum(technique_scores) / len(technique_scores)
            return execution_score

        # Default fallback if no useful data is available
        return 0.75

    # Updates for the purpose-based analyzer to handle hi-hat vs crash cymbals

    # Update the _calculate_creativity_score method
    def _calculate_creativity_score(self, data, instrument_analyses):
        """Calculate creativity score for drum fills"""
        # For raw audio analysis, rely on specific creativity indicators

        creativity_factors = []

        # Count unique techniques used
        techniques_used = set()
        if 'kick' in instrument_analyses and 'playing_technique' in instrument_analyses['kick']:
            techniques_used.add(f"kick_{instrument_analyses['kick']['playing_technique']}")

        if 'snare' in instrument_analyses and 'playing_technique' in instrument_analyses['snare']:
            techniques_used.add(f"snare_{instrument_analyses['snare']['playing_technique']}")

        # Use cymbal_type and either crash_articulation or hihat_state
        if 'cymbal' in instrument_analyses:
            if 'cymbal_type' in instrument_analyses['cymbal']:
                cymbal_type = instrument_analyses['cymbal']['cymbal_type']
                techniques_used.add(f"cymbal_{cymbal_type}")

                # Add articulation/state based on cymbal type
                if cymbal_type == 'crash' and 'crash_articulation' in instrument_analyses['cymbal']:
                    techniques_used.add(f"cymbal_articulation_{instrument_analyses['cymbal']['crash_articulation']}")
                elif cymbal_type == 'hihat' and 'hihat_state' in instrument_analyses['cymbal']:
                    techniques_used.add(f"hihat_state_{instrument_analyses['cymbal']['hihat_state']}")

        if 'tom' in instrument_analyses and 'playing_technique' in instrument_analyses['tom']:
            techniques_used.add(f"tom_{instrument_analyses['tom']['playing_technique']}")

        # Normalize by a reasonable maximum number of techniques (8 is reasonable with the additional cymbal articulations)
        technique_variety = min(1.0, len(techniques_used) / 8)
        creativity_factors.append(technique_variety)

        # Check for spectral variety as an indicator of creative timbre usage
        spectral_variety = []
        for instrument in ['kick', 'snare', 'cymbal', 'tom']:
            if instrument in instrument_analyses and 'spectral_centroid' in instrument_analyses[instrument]:
                spectral_variety.append(instrument_analyses[instrument]['spectral_centroid'])

        # If we have spectral data for multiple instruments, calculate variety
        if len(spectral_variety) >= 2:
            # Calculate standard deviation of spectral centroids
            mean_sc = sum(spectral_variety) / len(spectral_variety)
            variance = sum((x - mean_sc) ** 2 for x in spectral_variety) / len(spectral_variety)
            std_dev = variance ** 0.5

            # Higher std_dev means more timbral variety (normalize to 0-1)
            timbre_creativity = min(1.0, std_dev / 1000.0)
            creativity_factors.append(timbre_creativity)

        # Average creativity factors if available
        if creativity_factors:
            return sum(creativity_factors) / len(creativity_factors)

        # Default fallback if no useful data is available
        return 0.7

    # Update the generate_learning_suggestions method
    def generate_learning_suggestions(self, data):
        """
        Generate personalized learning suggestions based on analysis results

        Args:
            data (dict): Dictionary containing audio data for each instrument

        Returns:
            list: Personalized learning suggestions
        """
        # Get comprehensive analysis
        instrument_analyses = self._get_individual_analyses(data)

        suggestions = []

        # Generate kick drum suggestions
        if 'kick' in instrument_analyses:
            kick_analysis = instrument_analyses['kick']

            # Use technique_confidence for consistency assessment
            if kick_analysis.get('technique_confidence', 0) < 0.7:
                suggestions.append("Practice kick drum consistency with metronome exercises")

            # Check if rebound quality or power distribution is available
            if 'rebound_quality' in kick_analysis and kick_analysis['rebound_quality'] < 0.6:
                suggestions.append("Work on improving your kick drum rebound for better control")
            elif 'power_distribution' in kick_analysis and kick_analysis['power_distribution'] < 0.6:
                suggestions.append("Work on even power distribution in your kick technique")

            # Enhanced suggestion based on specific kick technique
            technique = kick_analysis.get('playing_technique', '')
            if technique == 'heel_down':
                suggestions.append("Consider practicing heel-toe technique for more power while maintaining control")
            elif technique == 'rebound':
                suggestions.append("Focus on controlled rebound exercises to improve dynamic range")

        # Generate snare drum suggestions
        if 'snare' in instrument_analyses:
            snare_analysis = instrument_analyses['snare']

            # Ghost note suggestions based on hit_strength
            hit_strength = snare_analysis.get('hit_strength', 0.8)
            if hit_strength < 0.5:
                suggestions.append("Work on consistency in your ghost notes for better grooves")
            elif hit_strength > 0.8:
                suggestions.append("Experiment with adding ghost notes to enhance your grooves")

            # Tone quality suggestions
            tone_quality = snare_analysis.get('tone_quality', 0.5)
            if tone_quality < 0.6:
                suggestions.append("Focus on strike technique for cleaner snare tone")

            # Technique suggestions
            technique = snare_analysis.get('playing_technique', '')
            if technique == 'center_hit':
                suggestions.append("Try rimshots for more powerful backbeats")

        # Generate cymbal suggestions
        if 'cymbal' in instrument_analyses:
            cymbal_analysis = instrument_analyses['cymbal']

            # Cymbal type suggestions
            cymbal_type = cymbal_analysis.get('cymbal_type', '')
            if cymbal_type == 'ride':
                suggestions.append("Practice ride cymbal patterns with varying dynamics to add interest")
            elif cymbal_type == 'crash':
                suggestions.append("Work on crash cymbal timing to enhance your accents")

                # Crash articulation suggestions
                crash_articulation = cymbal_analysis.get('crash_articulation', '')
                if crash_articulation == 'wash':
                    suggestions.append("Try more controlled crash hits for cleaner articulation")
                elif crash_articulation == 'choke':
                    suggestions.append("Experiment with letting your crashes ring out for more sustain")
            elif cymbal_type == 'hihat':
                suggestions.append("Experiment with different hi-hat openings for textural variety")

                # Hi-hat state suggestions
                hihat_state = cymbal_analysis.get('hihat_state', '')
                if hihat_state == 'closed':
                    suggestions.append("Try incorporating some open hi-hat sounds for more dynamic grooves")
                elif hihat_state == 'open':
                    suggestions.append("Practice smooth transitions between open and closed hi-hat sounds")
                elif hihat_state == 'half-open':
                    suggestions.append("Work on consistent half-open hi-hat techniques for funk and R&B grooves")

            # Sustain suggestions based on sustain_length
            sustain_length = cymbal_analysis.get('sustain_length', 0)
            if sustain_length < 0.0001:  # Arbitrary threshold, adjust as needed
                suggestions.append("Allow your cymbals to ring longer for better sustain and tone")

        # Generate tom suggestions
        if 'tom' in instrument_analyses:
            tom_analysis = instrument_analyses['tom']

            # Resonance suggestions
            resonance = tom_analysis.get('resonance', 0.5)
            if resonance < 0.6:
                suggestions.append("Check tom tuning for optimal resonance and practice clean striking technique")

            # Tom size suggestions
            tom_size = tom_analysis.get('tom_size', '')
            if tom_size:
                suggestions.append(f"Work on developing fills that emphasize the tonal quality of your {tom_size} toms")

        return suggestions

    def _calculate_groove_consistency(self, data, instrument_analyses):
        """Calculate groove consistency score based on timing and dynamics"""
        # For raw audio analysis, we rely on the instrument analyzers results
        instrument_consistency_scores = []

        if 'kick' in instrument_analyses and 'technique_confidence' in instrument_analyses['kick']:
            instrument_consistency_scores.append(instrument_analyses['kick']['technique_confidence'])

        if 'snare' in instrument_analyses and 'technique_confidence' in instrument_analyses['snare']:
            instrument_consistency_scores.append(instrument_analyses['snare']['technique_confidence'])

        # Average instrument consistency scores if available
        if instrument_consistency_scores:
            return sum(instrument_consistency_scores) / len(instrument_consistency_scores)

        # Default fallback if no useful data is available
        return 0.75

    def _calculate_timing_quality(self, data, instrument_analyses):
        """Calculate timing quality score based on precise hit timing"""
        # For raw audio analysis, estimate timing quality from available metrics

        # We can estimate timing quality based on technique confidence across instruments
        timing_scores = []

        if 'kick' in instrument_analyses and 'technique_confidence' in instrument_analyses['kick']:
            timing_scores.append(instrument_analyses['kick']['technique_confidence'])

        if 'snare' in instrument_analyses and 'technique_confidence' in instrument_analyses['snare']:
            timing_scores.append(instrument_analyses['snare']['technique_confidence'])

        if 'tom' in instrument_analyses and 'technique_confidence' in instrument_analyses['tom']:
            timing_scores.append(instrument_analyses['tom']['technique_confidence'])

        # Average timing scores if available
        if timing_scores:
            return sum(timing_scores) / len(timing_scores)

        # Default fallback if no useful data is available
        return 0.8

    def _calculate_dynamic_balance(self, data, instrument_analyses):
        """Calculate dynamic balance between instruments"""
        # Extract intensity/volume data for each instrument from the analyses
        instrument_intensities = {}

        if 'kick' in instrument_analyses and 'rms_energy' in instrument_analyses['kick']:
            instrument_intensities['kick'] = instrument_analyses['kick']['rms_energy']

        if 'snare' in instrument_analyses and 'rms_energy' in instrument_analyses['snare']:
            instrument_intensities['snare'] = instrument_analyses['snare']['rms_energy']

        if 'cymbal' in instrument_analyses and 'rms_energy' in instrument_analyses['cymbal']:
            instrument_intensities['cymbal'] = instrument_analyses['cymbal']['rms_energy']

        if 'tom' in instrument_analyses and 'rms_energy' in instrument_analyses['tom']:
            instrument_intensities['tom'] = instrument_analyses['tom']['rms_energy']

        # Need at least two instruments to calculate balance
        if len(instrument_intensities) >= 2:
            # Calculate standard deviation of instrument intensities
            values = list(instrument_intensities.values())
            mean_intensity = sum(values) / len(values)
            variance = sum((x - mean_intensity) ** 2 for x in values) / len(values)
            std_dev = variance ** 0.5

            # Calculate a balance score based on the standard deviation
            # A perfect balance would have std_dev = 0
            max_std_dev = 0.3  # Reasonable maximum for normalization
            std_dev_limited = min(max_std_dev, std_dev)
            balance_score = 1.0 - (std_dev_limited / max_std_dev)

            return balance_score

        # Default fallback if no useful data is available
        return 0.7

    def _calculate_fill_complexity(self, data, instrument_analyses):
        """Calculate complexity score for drum fills"""
        # For raw audio analysis, we estimate complexity from available metrics

        complexity_factors = []

        # Check for tom usage
        if 'tom' in instrument_analyses:
            tom_usage = 0.8  # Assume significant tom usage in fills
            complexity_factors.append(tom_usage)

        # Check for snare complexity based on technique confidence and hit strength
        if 'snare' in instrument_analyses:
            snare_complexity = (
                                       instrument_analyses['snare'].get('technique_confidence', 0.5) +
                                       instrument_analyses['snare'].get('hit_strength', 0.5)
                               ) / 2.0
            complexity_factors.append(snare_complexity)

        # Check for spectral variety in cymbals
        if 'cymbal' in instrument_analyses and 'spectral_bandwidth' in instrument_analyses['cymbal']:
            # Normalize spectral bandwidth to a 0-1 scale (assuming 5000 is a high value)
            cymbal_complexity = min(1.0, instrument_analyses['cymbal']['spectral_bandwidth'] / 5000.0)
            complexity_factors.append(cymbal_complexity)

        # Average complexity factors if available
        if complexity_factors:
            return sum(complexity_factors) / len(complexity_factors)

        # Default fallback if no useful data is available
        return 0.65

    def _calculate_execution_quality(self, data, instrument_analyses):
        """Calculate execution quality score for drum fills"""
        # Gather technique scores from instrument analyzers
        technique_scores = []

        if 'kick' in instrument_analyses and 'technique_confidence' in instrument_analyses['kick']:
            technique_scores.append(instrument_analyses['kick']['technique_confidence'])

        if 'snare' in instrument_analyses and 'technique_confidence' in instrument_analyses['snare']:
            technique_scores.append(instrument_analyses['snare']['technique_confidence'])

        if 'tom' in instrument_analyses and 'technique_confidence' in instrument_analyses['tom']:
            technique_scores.append(instrument_analyses['tom']['technique_confidence'])

        # Calculate average technique score if available
        if technique_scores:
            execution_score = sum(technique_scores) / len(technique_scores)
            return execution_score

        # Default fallback if no useful data is available
        return 0.75

    # Updates for the purpose-based analyzer to handle hi-hat vs crash cymbals

    # Update the _calculate_creativity_score method
    def _calculate_creativity_score(self, data, instrument_analyses):
        """Calculate creativity score for drum fills"""
        # For raw audio analysis, rely on specific creativity indicators

        creativity_factors = []

        # Count unique techniques used
        techniques_used = set()
        if 'kick' in instrument_analyses and 'playing_technique' in instrument_analyses['kick']:
            techniques_used.add(f"kick_{instrument_analyses['kick']['playing_technique']}")

        if 'snare' in instrument_analyses and 'playing_technique' in instrument_analyses['snare']:
            techniques_used.add(f"snare_{instrument_analyses['snare']['playing_technique']}")

        # Use cymbal_type and either crash_articulation or hihat_state
        if 'cymbal' in instrument_analyses:
            if 'cymbal_type' in instrument_analyses['cymbal']:
                cymbal_type = instrument_analyses['cymbal']['cymbal_type']
                techniques_used.add(f"cymbal_{cymbal_type}")

                # Add articulation/state based on cymbal type
                if cymbal_type == 'crash' and 'crash_articulation' in instrument_analyses['cymbal']:
                    techniques_used.add(f"cymbal_articulation_{instrument_analyses['cymbal']['crash_articulation']}")
                elif cymbal_type == 'hihat' and 'hihat_state' in instrument_analyses['cymbal']:
                    techniques_used.add(f"hihat_state_{instrument_analyses['cymbal']['hihat_state']}")

        if 'tom' in instrument_analyses and 'playing_technique' in instrument_analyses['tom']:
            techniques_used.add(f"tom_{instrument_analyses['tom']['playing_technique']}")

        # Normalize by a reasonable maximum number of techniques (8 is reasonable with the additional cymbal articulations)
        technique_variety = min(1.0, len(techniques_used) / 8)
        creativity_factors.append(technique_variety)

        # Check for spectral variety as an indicator of creative timbre usage
        spectral_variety = []
        for instrument in ['kick', 'snare', 'cymbal', 'tom']:
            if instrument in instrument_analyses and 'spectral_centroid' in instrument_analyses[instrument]:
                spectral_variety.append(instrument_analyses[instrument]['spectral_centroid'])

        # If we have spectral data for multiple instruments, calculate variety
        if len(spectral_variety) >= 2:
            # Calculate standard deviation of spectral centroids
            mean_sc = sum(spectral_variety) / len(spectral_variety)
            variance = sum((x - mean_sc) ** 2 for x in spectral_variety) / len(spectral_variety)
            std_dev = variance ** 0.5

            # Higher std_dev means more timbral variety (normalize to 0-1)
            timbre_creativity = min(1.0, std_dev / 1000.0)
            creativity_factors.append(timbre_creativity)

        # Average creativity factors if available
        if creativity_factors:
            return sum(creativity_factors) / len(creativity_factors)

        # Default fallback if no useful data is available
        return 0.7

