import numpy as np
from typing import Dict, Tuple, Set

class SharedKnowledge:
    def __init__(self):
        self.known_obstacles = set()
        self.enemy_positions: Dict[int, np.ndarray] = {}

    def add_obstacle(self, obstacle):
        self.known_obstacles.add(obstacle)

    def get_known_obstacles(self):
        return list(self.known_obstacles)

    def update_enemy_position(self, enemy_id: int, position: Tuple[int, int]):
        self.enemy_positions[enemy_id] = np.array(position)

    def get_enemy_positions(self) -> Dict[int, np.ndarray]:
        return self.enemy_positions
