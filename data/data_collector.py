import json
from typing import Dict, List
import time
import os

class DataCollector:
    def __init__(self, max_entries: int = 1000):
        self.max_entries = max_entries
        self.observations = []
        self.outcomes = []
        self.statistics = {
            'gathering_success': 0.0,  # Changed to float
            'fishing_success': 0.0,    # Changed to float
            'combat_success': 0.0,     # Changed to float
            'total_actions': 0
        }

    def store_observation(self, observation: Dict) -> None:
        """Store a new observation with timestamp"""
        observation_entry = {
            'timestamp': time.time(),
            'data': observation
        }

        self.observations.append(observation_entry)

        # Maintain maximum size
        if len(self.observations) > self.max_entries:
            self.observations = self.observations[-self.max_entries:]

        # Periodically save to file
        if len(self.observations) % 100 == 0:
            self._save_data()

    def store_outcome(self, action: Dict, outcome: Dict) -> None:
        """Store action outcome with statistics update"""
        outcome_entry = {
            'timestamp': time.time(),
            'action': action,
            'outcome': outcome
        }

        self.outcomes.append(outcome_entry)
        self._update_statistics(action, outcome)

        # Maintain maximum size
        if len(self.outcomes) > self.max_entries:
            self.outcomes = self.outcomes[-self.max_entries:]

    def _update_statistics(self, action: Dict, outcome: Dict) -> None:
        """Update success statistics for different activities"""
        self.statistics['total_actions'] += 1

        action_type = action.get('action')
        success = outcome.get('success', False)

        if action_type == 'gather':
            self.statistics['gathering_success'] = (
                self.statistics['gathering_success'] * 0.9 + (0.1 if success else 0.0)
            )
        elif action_type == 'fish':
            self.statistics['fishing_success'] = (
                self.statistics['fishing_success'] * 0.9 + (0.1 if success else 0.0)
            )
        elif action_type == 'combat':
            self.statistics['combat_success'] = (
                self.statistics['combat_success'] * 0.9 + (0.1 if success else 0.0)
            )

    def _save_data(self) -> None:
        """Save collected data to files"""
        data = {
            'statistics': self.statistics,
            'recent_observations': self.observations[-100:],
            'recent_outcomes': self.outcomes[-100:]
        }

        try:
            with open('collected_data.json', 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")

    def get_statistics(self) -> Dict:
        """Return current statistics"""
        return self.statistics

    def get_recent_observations(self, count: int = 10) -> List[Dict]:
        """Return recent observations"""
        return self.observations[-count:]

    def get_recent_outcomes(self, count: int = 10) -> List[Dict]:
        """Return recent outcomes"""
        return self.outcomes[-count:]