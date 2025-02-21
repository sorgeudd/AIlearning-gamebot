from typing import Dict, List
import random
import numpy as np

class FishingManager:
    def __init__(self):
        self.fishing_patterns = {
            'common': {'success_rate': 0.7, 'avg_time': 5},
            'rare': {'success_rate': 0.4, 'avg_time': 8},
            'exotic': {'success_rate': 0.2, 'avg_time': 12}
        }
        self.fish_values = {
            'common': 1,
            'rare': 3,
            'exotic': 5
        }

    def evaluate_fishing_spot(self, fishing_spot: Dict) -> float:
        """Calculate the value of a fishing spot"""
        fish_type = fishing_spot.properties['fish_type']
        base_value = self.fish_values[fish_type]
        pattern_data = self.fishing_patterns[fish_type]
        
        # Calculate expected value per time unit
        expected_value = (base_value * pattern_data['success_rate'] / 
                        pattern_data['avg_time'])
        
        return expected_value

    def fish(self, fishing_spot: Dict) -> Dict:
        """Attempt to fish at a spot"""
        fish_type = fishing_spot.properties['fish_type']
        pattern = self.fishing_patterns[fish_type]
        
        # Simulate fishing attempt
        success = random.random() < pattern['success_rate']
        time_taken = pattern['avg_time'] * (0.9 + random.random() * 0.2)
        
        return {
            'success': success,
            'time_taken': time_taken,
            'fish_type': fish_type,
            'amount': 1 if success else 0
        }

    def update_fishing_patterns(self, fish_type: str, outcome: Dict) -> None:
        """Update fishing patterns based on outcomes"""
        if fish_type in self.fishing_patterns:
            pattern = self.fishing_patterns[fish_type]
            # Update success rate with moving average
            pattern['success_rate'] = (pattern['success_rate'] * 0.9 +
                                     (0.1 if outcome['success'] else 0))
            # Update average time
            pattern['avg_time'] = (pattern['avg_time'] * 0.9 +
                                 outcome['time_taken'] * 0.1)
