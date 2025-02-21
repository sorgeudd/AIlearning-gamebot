from typing import Dict, List
import random

class StateMachine:
    def __init__(self):
        self.states = ['idle', 'gathering', 'fishing', 'combat', 'exploring', 'healing']
        self.transitions = {
            'idle': {'gathering': 0.3, 'fishing': 0.3, 'combat': 0.2, 'exploring': 0.2},
            'gathering': {'idle': 0.1, 'exploring': 0.2, 'combat': 0.1, 'gathering': 0.6},
            'fishing': {'idle': 0.1, 'exploring': 0.2, 'gathering': 0.1, 'fishing': 0.6},
            'combat': {'idle': 0.2, 'exploring': 0.2, 'gathering': 0.1, 'combat': 0.3, 'healing': 0.2},
            'exploring': {'gathering': 0.3, 'fishing': 0.3, 'combat': 0.2, 'idle': 0.2},
            'healing': {'idle': 0.4, 'exploring': 0.3, 'gathering': 0.2, 'fishing': 0.1}
        }
        self.state_timers = {state: 0 for state in self.states}
        self.state_success_rates = {state: 0.5 for state in self.states}
        self.consecutive_failures = {state: 0 for state in self.states}

    def get_next_state(self, current_state: str, environment: Dict) -> str:
        """Determine the next state based on current state and environment"""
        # Check player health
        player_health = environment.get('player_status', {}).get('health', 100)
        if player_health < 50 and current_state != 'healing':
            return 'healing'

        # Increment state timer
        self.state_timers[current_state] += 1

        # Check for forced transitions based on environment
        if self._check_forced_transition(environment):
            return self._handle_forced_transition(environment)

        # Check for repeated failures
        if self.consecutive_failures[current_state] >= 3:
            # Reset failure counter and transition to a different state
            self.consecutive_failures[current_state] = 0
            available_states = [s for s in self.states if s != current_state]
            return random.choice(available_states)

        # Normal state transition logic
        if self.state_timers[current_state] > 10:  # Consider transition after 10 ticks
            transition_probs = self.transitions[current_state]
            # Adjust probabilities based on success rates and health
            adjusted_probs = {
                state: prob * (1 + self.state_success_rates[state])
                for state, prob in transition_probs.items()
            }

            # Reduce combat probability when health is low
            if player_health < 70:
                adjusted_probs['combat'] = adjusted_probs.get('combat', 0) * 0.5

            # Normalize probabilities
            total = sum(adjusted_probs.values())
            adjusted_probs = {
                state: prob/total for state, prob in adjusted_probs.items()
            }

            # Random selection based on adjusted probabilities
            rand_val = random.random()
            cumulative = 0
            for state, prob in adjusted_probs.items():
                cumulative += prob
                if rand_val <= cumulative:
                    self.state_timers[current_state] = 0
                    return state

        return current_state

    def _check_forced_transition(self, environment: Dict) -> bool:
        """Check if environment requires a forced state transition"""
        nearby_objects = environment.get('nearby_objects', [])
        player_health = environment.get('player_status', {}).get('health', 100)

        # Force healing if health is very low
        if player_health < 30:
            return True

        # Force combat if enemy is too close
        dangerous_enemies = [obj for obj in nearby_objects 
                           if obj.type == 'enemy' and obj.properties['level'] > 5]
        if dangerous_enemies and player_health > 50:
            return True

        return False

    def _handle_forced_transition(self, environment: Dict) -> str:
        """Handle forced state transitions"""
        nearby_objects = environment.get('nearby_objects', [])
        player_health = environment.get('player_status', {}).get('health', 100)

        # Prioritize healing when health is low
        if player_health < 30:
            return 'healing'

        # Prioritize combat for dangerous enemies if health is good
        dangerous_enemies = [obj for obj in nearby_objects 
                           if obj.type == 'enemy' and obj.properties['level'] > 5]
        if dangerous_enemies and player_health > 50:
            return 'combat'

        return 'exploring'

    def update_transitions(self, state: str, outcome: Dict) -> None:
        """Update transition probabilities based on action outcomes"""
        success = outcome.get('success', False)

        # Update success rate for the state
        current_rate = self.state_success_rates[state]
        self.state_success_rates[state] = current_rate * 0.9 + (0.1 if success else 0)

        # Update consecutive failures
        if success:
            self.consecutive_failures[state] = 0
        else:
            self.consecutive_failures[state] += 1

        # Adjust transition probabilities
        if success:
            # Increase probability of staying in successful state
            for target_state in self.transitions[state]:
                if target_state == state:
                    self.transitions[state][target_state] *= 1.1
                else:
                    self.transitions[state][target_state] *= 0.9

            # Normalize probabilities
            total = sum(self.transitions[state].values())
            self.transitions[state] = {
                target: prob/total 
                for target, prob in self.transitions[state].items()
            }