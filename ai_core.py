from typing import Dict, List, Tuple, Optional
import numpy as np
from learning.pattern_recognition import PatternRecognizer
from learning.state_machine import StateMachine
from learning.openai_analyzer import OpenAIAnalyzer
from learning.screen_observer import ScreenObserver
from data.data_collector import DataCollector
from game_environment import GameObject

class AIBot:
    def __init__(self):
        self.pattern_recognizer = PatternRecognizer()
        self.state_machine = StateMachine()
        self.data_collector = DataCollector()
        self.openai_analyzer = OpenAIAnalyzer()
        self.screen_observer = ScreenObserver(callback=self._handle_observation)
        self.current_state = 'idle'
        self.current_target: Optional[GameObject] = None
        self.inventory: Dict = {}
        self.recent_actions: List[Dict] = []
        self.learned_patterns: List[Dict] = []

    def start_learning(self, game_window_region: Optional[Tuple[int, int, int, int]] = None) -> None:
        """Start observing and learning from player gameplay"""
        self.screen_observer.start_observation(region=game_window_region)

    def stop_learning(self) -> None:
        """Stop observing gameplay"""
        self.screen_observer.stop_observation()

    def _handle_observation(self, observation_data: Dict) -> None:
        """Process observations from screen capture"""
        # Store observation
        self.data_collector.store_observation(observation_data)

        # Analyze observation
        if 'pattern_identified' in observation_data:
            pattern = observation_data['pattern']
            self.learned_patterns.append(pattern)

            # Use OpenAI to analyze the pattern
            analysis = self.openai_analyzer.analyze_game_state({
                'observed_pattern': pattern,
                'recent_patterns': self.learned_patterns[-5:]
            }, self.recent_actions)

            if analysis:
                # Update behavior based on learned patterns
                self._update_behavior(analysis)

    def _update_behavior(self, analysis: Dict) -> None:
        """Update AI behavior based on observed patterns"""
        if 'recommended_action' in analysis:
            # Adjust state machine transitions based on observed patterns
            self.state_machine.update_transitions(
                self.current_state,
                {'success': True, 'learned_pattern': True}
            )

            # Update pattern recognition weights
            self.pattern_recognizer.analyze_observation({
                'learned_pattern': analysis.get('recommended_action'),
                'success_rate': analysis.get('risk_assessment', 0.5)
            })

    def observe_environment(self, game_state: Dict) -> None:
        """Process and learn from the current game state"""
        # Collect data about the environment
        observation_data = {
            'nearby_objects': game_state.get('nearby_objects', []),
            'player_position': game_state.get('player_position', (0, 0)),
            'player_status': game_state.get('player_status', {})
        }

        self.data_collector.store_observation(observation_data)
        self.pattern_recognizer.analyze_observation(observation_data)

        # Get strategic insights from OpenAI
        analysis = self.openai_analyzer.analyze_game_state(game_state, self.recent_actions)
        if analysis:
            # Use OpenAI's recommendations to influence state transitions
            if analysis.get('risk_assessment', 0) > 0.7 and \
               game_state.get('player_status', {}).get('health', 100) < 70:
                self.current_state = 'healing'
            elif analysis.get('recommended_action') != self.current_state:
                self.current_state = analysis.get('recommended_action', 'explore')

    def decide_action(self, game_state: Dict) -> Dict:
        """Decide the next action based on current state and observations"""
        nearby_objects = game_state.get('nearby_objects', [])

        # Update state based on environment and current goals
        new_state = self.state_machine.get_next_state(
            current_state=self.current_state,
            environment=game_state
        )

        if new_state != self.current_state:
            self.current_state = new_state
            self.current_target = None

        # Generate action based on state
        action: Dict
        if self.current_state == 'gathering':
            action = self._handle_gathering(nearby_objects)
        elif self.current_state == 'fishing':
            action = self._handle_fishing(nearby_objects)
        elif self.current_state == 'combat':
            action = self._handle_combat(nearby_objects)
        elif self.current_state == 'healing':
            action = {'action': 'healing'}
        else:
            action = {'action': 'explore'}

        # Store action for analysis
        self.recent_actions.append(action)
        self.recent_actions = self.recent_actions[-10:]  # Keep last 10 actions

        return action

    def _handle_gathering(self, nearby_objects: List[GameObject]) -> Dict:
        """Handle resource gathering logic"""
        resources = [obj for obj in nearby_objects if obj.type == 'resource']
        if resources:
            target = self.pattern_recognizer.select_best_resource(resources)
            if isinstance(target, GameObject):
                return {
                    'action': 'gather',
                    'target': target,
                    'position': target.position
                }
        return {'action': 'explore'}

    def _handle_fishing(self, nearby_objects: List[GameObject]) -> Dict:
        """Handle fishing logic"""
        fishing_spots = [obj for obj in nearby_objects if obj.type == 'fishing_spot']
        if fishing_spots:
            target = self.pattern_recognizer.select_best_fishing_spot(fishing_spots)
            if isinstance(target, GameObject):
                return {
                    'action': 'fish',
                    'target': target,
                    'position': target.position
                }
        return {'action': 'explore'}

    def _handle_combat(self, nearby_objects: List[GameObject]) -> Dict:
        """Handle combat logic"""
        enemies = [obj for obj in nearby_objects if obj.type == 'enemy']
        if enemies:
            target = self.pattern_recognizer.select_best_combat_target(enemies)
            if isinstance(target, GameObject):
                return {
                    'action': 'combat',
                    'target': target,
                    'position': target.position
                }
        return {'action': 'explore'}

    def learn_from_outcome(self, action: Dict, outcome: Dict) -> None:
        """Learn from the results of actions"""
        self.pattern_recognizer.update_patterns(action, outcome)
        self.state_machine.update_transitions(self.current_state, outcome)
        self.data_collector.store_outcome(action, outcome)

        # Learn from outcome using OpenAI
        success = outcome.get('success', False)
        pattern_analysis = self.openai_analyzer.learn_from_outcome(action, outcome, success)

        if pattern_analysis:
            # Use pattern analysis to adjust behavior
            success_rate = pattern_analysis.get('success_rate', 0)
            if success_rate < 0.3:  # If success rate is low
                # Force state change based on improvement suggestions
                suggestions = pattern_analysis.get('improvement_suggestions', [])
                if suggestions and self.current_state in suggestions[0].lower():
                    self.current_state = 'explore'  # Reset to exploration