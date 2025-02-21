from typing import Dict, List
import random
import numpy as np

class ResourceGatherer:
    def __init__(self):
        self.gathering_patterns = {
            'wood': {'success_rate': 0.8, 'avg_time': 3},
            'ore': {'success_rate': 0.7, 'avg_time': 4},
            'herbs': {'success_rate': 0.9, 'avg_time': 2}
        }
        self.resource_values = {
            'wood': 1,
            'ore': 2,
            'herbs': 3
        }

    def evaluate_resource(self, resource_obj: Dict) -> float:
        """Calculate the value of a resource based on type and distance"""
        resource_type = resource_obj.properties['resource_type']
        base_value = self.resource_values[resource_type]
        pattern_data = self.gathering_patterns[resource_type]
        
        # Calculate efficiency score
        efficiency = (pattern_data['success_rate'] / pattern_data['avg_time'])
        
        return base_value * efficiency

    def gather_resource(self, resource_obj: Dict) -> Dict:
        """Attempt to gather a resource"""
        resource_type = resource_obj.properties['resource_type']
        pattern = self.gathering_patterns[resource_type]
        
        success = random.random() < pattern['success_rate']
        time_taken = pattern['avg_time'] * (0.8 + random.random() * 0.4)
        
        return {
            'success': success,
            'time_taken': time_taken,
            'amount': random.randint(1, 3) if success else 0,
            'resource_type': resource_type
        }

    def update_gathering_patterns(self, resource_type: str, outcome: Dict) -> None:
        """Update gathering patterns based on outcomes"""
        if resource_type in self.gathering_patterns:
            pattern = self.gathering_patterns[resource_type]
            # Update success rate with moving average
            pattern['success_rate'] = (pattern['success_rate'] * 0.9 +
                                     (0.1 if outcome['success'] else 0))
            # Update average time
            pattern['avg_time'] = (pattern['avg_time'] * 0.9 +
                                 outcome['time_taken'] * 0.1)
