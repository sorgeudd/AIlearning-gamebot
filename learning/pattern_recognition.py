from typing import Dict, List
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

class PatternRecognizer:
    def __init__(self):
        self.scaler = StandardScaler()
        self.kmeans = KMeans(n_clusters=5)
        self.observations = []
        self.patterns = {}

    def analyze_observation(self, observation: Dict) -> None:
        """Analyze and learn from new observation"""
        if not observation:
            return

        self.observations.append(observation)

        if len(self.observations) >= 100:
            self._update_patterns()
            self.observations = self.observations[-1000:]  # Keep last 1000 observations

    def _update_patterns(self) -> None:
        """Update learned patterns using clustering"""
        if len(self.observations) < 50:
            return

        # Extract features from observations
        features = []
        for obs in self.observations:
            feature_vector = self._extract_features(obs)
            if feature_vector:  # Only add valid feature vectors
                features.append(feature_vector)

        if not features:  # If no valid features, return
            return

        # Normalize features
        features_normalized = self.scaler.fit_transform(features)

        # Perform clustering
        clusters = self.kmeans.fit_predict(features_normalized)

        # Update patterns based on clusters
        for i, cluster in enumerate(clusters):
            if cluster not in self.patterns:
                self.patterns[cluster] = []
            self.patterns[cluster].append(self.observations[i])

    def _extract_features(self, observation: Dict) -> List[float]:
        """Extract numerical features from observation"""
        try:
            features = []

            # Position features
            pos = observation.get('player_position', (0, 0))
            features.extend([float(pos[0]), float(pos[1])])

            # Object counts
            nearby_objects = observation.get('nearby_objects', [])
            resource_count = sum(1 for obj in nearby_objects if getattr(obj, 'type', '') == 'resource')
            fishing_count = sum(1 for obj in nearby_objects if getattr(obj, 'type', '') == 'fishing_spot')
            enemy_count = sum(1 for obj in nearby_objects if getattr(obj, 'type', '') == 'enemy')

            features.extend([float(resource_count), float(fishing_count), float(enemy_count)])

            return features
        except Exception as e:
            print(f"Error extracting features: {e}")
            return None

    def select_best_resource(self, resources: List) -> Dict:
        """Select the best resource target based on learned patterns"""
        if not resources:
            return {}

        scores = []
        for resource in resources:
            # Calculate score based on type and distance
            type_score = {'wood': 1, 'ore': 2, 'herbs': 3}.get(
                getattr(resource, 'properties', {}).get('resource_type', ''), 1)
            scores.append(type_score)

        best_index = int(np.argmax(scores))
        return resources[best_index]

    def select_best_fishing_spot(self, fishing_spots: List) -> Dict:
        """Select the best fishing spot based on learned patterns"""
        if not fishing_spots:
            return {}

        scores = []
        for spot in fishing_spots:
            # Calculate score based on fish type
            type_score = {'common': 1, 'rare': 2, 'exotic': 3}.get(
                getattr(spot, 'properties', {}).get('fish_type', ''), 1)
            scores.append(type_score)

        best_index = int(np.argmax(scores))
        return fishing_spots[best_index]

    def select_best_combat_target(self, enemies: List) -> Dict:
        """Select the best combat target based on learned patterns"""
        if not enemies:
            return {}

        scores = []
        for enemy in enemies:
            # Calculate score based on level and health
            level_score = 10 - abs(5 - getattr(enemy, 'properties', {}).get('level', 5))
            health_score = 100 - getattr(enemy, 'properties', {}).get('health', 100)
            scores.append(level_score + health_score)

        best_index = int(np.argmax(scores))
        return enemies[best_index]

    def update_patterns(self, action: Dict, outcome: Dict) -> None:
        """Update pattern recognition based on action outcomes"""
        if action and outcome:
            # Store action-outcome pair for learning
            self.observations.append({
                'action': action,
                'outcome': outcome,
                'success': outcome.get('success', False)
            })