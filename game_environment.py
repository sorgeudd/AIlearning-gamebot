import random
from dataclasses import dataclass
from typing import Dict, List, Tuple, TypedDict, Union

class GameObjectProperties(TypedDict, total=False):
    resource_type: str
    fish_type: str
    level: int
    health: int

@dataclass
class GameObject:
    type: str
    position: Tuple[int, int]
    properties: GameObjectProperties

class GameEnvironment:
    def __init__(self, size: Tuple[int, int] = (100, 100)):
        self.size = size
        self.objects: List[GameObject] = []
        self.player_position = (0, 0)
        self.initialize_environment()

    def initialize_environment(self):
        # Create resource nodes
        for _ in range(20):
            self.objects.append(GameObject(
                type='resource',
                position=(random.randint(0, self.size[0]), random.randint(0, self.size[1])),
                properties={'resource_type': random.choice(['wood', 'ore', 'herbs'])}
            ))

        # Create fishing spots
        for _ in range(10):
            self.objects.append(GameObject(
                type='fishing_spot',
                position=(random.randint(0, self.size[0]), random.randint(0, self.size[1])),
                properties={'fish_type': random.choice(['common', 'rare', 'exotic'])}
            ))

        # Create enemies
        for _ in range(15):
            self.objects.append(GameObject(
                type='enemy',
                position=(random.randint(0, self.size[0]), random.randint(0, self.size[1])),
                properties={'level': random.randint(1, 10), 'health': 100}
            ))

    def get_nearby_objects(self, position: Tuple[int, int], radius: int) -> List[GameObject]:
        """Return objects within the specified radius of the position"""
        nearby = []
        for obj in self.objects:
            distance = ((position[0] - obj.position[0]) ** 2 + 
                       (position[1] - obj.position[1]) ** 2) ** 0.5
            if distance <= radius:
                nearby.append(obj)
        return nearby

    def interact_with_object(self, obj: GameObject) -> Dict:
        """Simulate interaction with a game object"""
        if obj.type == 'resource':
            return {
                'action': 'gather',
                'resource_type': obj.properties['resource_type'],
                'amount': random.randint(1, 5)
            }
        elif obj.type == 'fishing_spot':
            return {
                'action': 'fish',
                'fish_type': obj.properties['fish_type'],
                'success': random.random() > 0.3
            }
        elif obj.type == 'enemy':
            return {
                'action': 'combat',
                'enemy_level': obj.properties['level'],
                'damage_dealt': random.randint(10, 30)
            }
        return {}

    def update(self):
        """Update game state"""
        # Simulate simple object movement
        for obj in self.objects:
            if obj.type == 'enemy':
                obj.position = (
                    (obj.position[0] + random.randint(-1, 1)) % self.size[0],
                    (obj.position[1] + random.randint(-1, 1)) % self.size[1]
                )