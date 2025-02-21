from typing import Dict
import random
from game_environment import GameObject

class CombatManager:
    def __init__(self):
        self.combat_patterns = {}
        self.enemy_difficulties = {
            1: {'risk': 0.1, 'reward': 1},
            2: {'risk': 0.2, 'reward': 2},
            3: {'risk': 0.3, 'reward': 3},
            4: {'risk': 0.4, 'reward': 4},
            5: {'risk': 0.5, 'reward': 5}
        }
        self.consecutive_failures = 0
        self.health_threshold = 50

    def evaluate_combat_target(self, enemy: GameObject, current_health: int = 100) -> float:
        """Calculate the value/risk ratio of engaging an enemy"""
        enemy_level = enemy.properties['level']
        enemy_health = enemy.properties['health']

        if current_health < self.health_threshold:
            return -1.0  # Negative score to avoid combat when low health

        if enemy_level not in self.combat_patterns:
            self.combat_patterns[enemy_level] = {
                'success_rate': 0.5,
                'avg_damage_taken': 20,
                'avg_time': 10
            }

        pattern = self.combat_patterns[enemy_level]
        difficulty = self.enemy_difficulties.get(enemy_level, 
                                               {'risk': 0.5, 'reward': enemy_level})

        # Penalize score if we've had consecutive failures
        failure_penalty = max(0, self.consecutive_failures * 0.2)

        # Calculate combat value based on success rate and rewards
        value = (difficulty['reward'] * pattern['success_rate'] / 
                (1 + pattern['avg_damage_taken'] * difficulty['risk']))

        return max(0, value - failure_penalty)

    def engage_combat(self, enemy: GameObject) -> Dict:
        """Simulate combat with an enemy"""
        enemy_level = enemy.properties['level']
        pattern = self.combat_patterns.get(enemy_level, {
            'success_rate': 0.5,
            'avg_damage_taken': 20,
            'avg_time': 10
        })

        # Adjust success chance based on consecutive failures
        adjusted_success_rate = pattern['success_rate'] * (0.8 ** self.consecutive_failures)
        success = random.random() < adjusted_success_rate

        damage_taken = pattern['avg_damage_taken'] * (0.8 + random.random() * 0.4)
        time_taken = pattern['avg_time'] * (0.9 + random.random() * 0.2)

        if success:
            self.consecutive_failures = 0
        else:
            self.consecutive_failures += 1

        return {
            'success': success,
            'damage_taken': damage_taken,
            'time_taken': time_taken,
            'enemy_level': enemy_level,
            'reward': self.enemy_difficulties.get(enemy_level, 
                                                {'reward': enemy_level})['reward']
        }

    def update_combat_patterns(self, enemy_level: int, outcome: Dict) -> None:
        """Update combat patterns based on outcomes"""
        if enemy_level not in self.combat_patterns:
            self.combat_patterns[enemy_level] = {
                'success_rate': 0.5,
                'avg_damage_taken': 20,
                'avg_time': 10
            }

        pattern = self.combat_patterns[enemy_level]
        # Update success rate
        pattern['success_rate'] = (pattern['success_rate'] * 0.9 +
                                 (0.1 if outcome['success'] else 0))
        # Update average damage taken
        pattern['avg_damage_taken'] = (pattern['avg_damage_taken'] * 0.9 +
                                     outcome['damage_taken'] * 0.1)
        # Update average time
        pattern['avg_time'] = (pattern['avg_time'] * 0.9 +
                             outcome['time_taken'] * 0.1)