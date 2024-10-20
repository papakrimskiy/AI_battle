import pygame
import os
import numpy as np
from typing import List, Tuple, Union, Optional
from .ImageRect import ImageRect
from .SharedKnowledge import SharedKnowledge
from .constants import SCREEN_WIDTH, SCREEN_HEIGHT

class TankAgent:
    shared_knowledge = SharedKnowledge()

    def __init__(self, x: int, y: int, team: str):
        self.team = team
        image_path = os.path.join("game", "sheald.png")
        self.image = ImageRect(x, y, image_path)
        # Уменьшаем размер изображения в 3 раза
        original_size = self.image.image.get_size()
        new_size = (original_size[0] // 3, original_size[1] // 3)
        self.image.image = pygame.transform.scale(self.image.image, new_size)
        self.image.rect = self.image.image.get_rect(center=(x, y))

        self.speed = 1  # Танк медленнее обычных агентов
        self.max_health = 5000  # Больше здоровья, чем у обычных агентов
        self.health = self.max_health
        self.damage = 30  # Больше урона
        self.base_damage = 15  # Урон по базе
        self.repair_amount = 5  # Количество здоровья, восстанавливаемого базе за один тик
        self.target: Optional[Tuple[int, int]] = None
        self.last_attack_time = 0
        self.attack_cooldown = 1500  # Более долгая перезарядка
        self.attack_range = 100  # Больший радиус атаки
        self.id = id(self)
        self.defending_base = False
        self.reached_initial_position = False
        self.initial_position = (x, y)
        self.personal_obstacles = set()

    def is_alive(self) -> bool:
        return self.health > 0

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image.image, self.image.rect)
        self.draw_health_bar(screen)

    def draw_health_bar(self, screen: pygame.Surface):
        bar_width = self.image.rect.width
        bar_height = 5
        bar_position = (self.image.rect.x, self.image.rect.y - 10)

        health_width = int(self.health / self.max_health * bar_width)
        pygame.draw.rect(screen, (0, 255, 0), (*bar_position, health_width, bar_height))

    def update(self, enemy_base, ally_base, enemy_agents, ally_agents, obstacles):
        if not self.is_alive():
            return
        state = self.get_state(enemy_base, ally_base, enemy_agents, ally_agents, obstacles)
        action = self.choose_action(state, ally_base, enemy_agents, obstacles)
        self.perform_action(action, enemy_base, ally_base, enemy_agents, ally_agents, obstacles)

    def get_state(self, enemy_base, ally_base, enemy_agents, ally_agents, obstacles):
        return {
            'health': self.health,
            'position': self.image.rect.center,
            'enemy_base_position': enemy_base.rect.center,
            'ally_base_position': ally_base.rect.center,
            'enemy_positions': [agent.image.rect.center for agent in enemy_agents if agent.is_alive()],
            'ally_positions': [agent.image.rect.center for agent in ally_agents if agent.is_alive()],
            'obstacles': obstacles
        }

    def choose_action(self, state, ally_base, enemy_agents, obstacles):
        if self.is_base_under_attack(ally_base, enemy_agents, obstacles):
            return 'defend'
        elif ally_base.health < ally_base.max_health * 0.5:
            return 'repair'
        elif self.health < self.max_health * 0.3:
            return 'retreat'
        else:
            return 'attack'

    def perform_action(self, action, enemy_base, ally_base, enemy_agents, ally_agents, obstacles):
        if action == 'attack':
            self.move_towards_enemy_base(enemy_base)
            self.attack_base(enemy_base)
        elif action == 'defend':
            self.defend_base(ally_base, enemy_agents)
        elif action == 'repair':
            self.repair_base(ally_base)
        elif action == 'retreat':
            self.retreat([(ally_base.rect.x, ally_base.rect.y)])

    def move_towards_enemy_base(self, enemy_base):
        target_position = np.array(enemy_base.rect.center)
        my_position = np.array(self.image.rect.center)
        direction = target_position - my_position
        distance = np.linalg.norm(direction)

        if distance > self.speed:
            normalized_direction = direction / distance
            new_position = my_position + self.speed * normalized_direction

            new_position[0] = np.clip(new_position[0], 0, SCREEN_WIDTH - 1)
            new_position[1] = np.clip(new_position[1], 0, SCREEN_HEIGHT - 1)

            self.image.rect.center = tuple(new_position)

    def defend_base(self, base, enemies):
        base_center = np.array(base.rect.center)
        my_pos = np.array(self.image.rect.center)

        ideal_distance = 150  # Танк держится дальше от базы, чем обычные агенты
        to_base = base_center - my_pos
        dist_to_base = np.linalg.norm(to_base)

        if dist_to_base > ideal_distance:
            self.move_towards(base_center)
        elif dist_to_base < ideal_distance - 10 and dist_to_base != 0:
            self.move_towards(tuple(my_pos - to_base / dist_to_base * 10))

        for enemy in enemies:
            if np.linalg.norm(np.array(enemy.image.rect.center) - base_center) < ideal_distance + 50:
                self.attack(enemy)
                break

    def repair_base(self, base):
        if np.linalg.norm(np.array(self.image.rect.center) - np.array(base.rect.center)) <= self.attack_range:
            base.health = min(base.health + self.repair_amount, base.max_health)
        else:
            self.move_towards(base.rect.center)

    def retreat(self, safe_locations: List[Tuple[int, int]]):
        nearest_safe_location = min(safe_locations, key=lambda loc: np.linalg.norm(np.array(loc) - np.array(self.image.rect.center)))
        self.move_towards(nearest_safe_location)

    def move_towards(self, target):
        direction = np.array(target) - np.array(self.image.rect.center)
        distance = np.linalg.norm(direction)

        if distance <= self.speed:
            new_position = target
        else:
            normalized_direction = direction / distance
            new_position = np.array(self.image.rect.center) + self.speed * normalized_direction

        new_position = np.clip(new_position, [0, 0], [SCREEN_WIDTH, SCREEN_HEIGHT])
        self.image.rect.center = tuple(map(int, new_position))

        return np.array_equal(new_position, target)

    def attack(self, target):
        if target.health <= 0:
            self.target = None
            return
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            target.health -= self.damage
            target.health = max(0, target.health)
            self.last_attack_time = current_time

    def is_base_under_attack(self, ally_base, enemy_agents, obstacles):
        return any(agent.is_alive() and ally_base.rect.colliderect(agent.image.rect) for agent in enemy_agents)

    def attack_base(self, enemy_base):
        if pygame.Rect.colliderect(self.image.rect, enemy_base.rect):
            current_time = pygame.time.get_ticks()
            if current_time - self.last_attack_time >= self.attack_cooldown:
                enemy_base.health -= self.base_damage
                enemy_base.health = max(0, enemy_base.health)
                self.last_attack_time = current_time

    def find_nearest_enemy(self, enemy_agents: List[Union['RedMeleeAgent', 'BlueMeleeAgent']], obstacles: List['Obstacle']) -> Tuple[Optional[Union['RedMeleeAgent', 'BlueMeleeAgent']], float]:
        if not enemy_agents:
            return None, float('inf')

        agent_positions = np.array([agent.image.rect.center for agent in enemy_agents if agent.is_alive()])
        my_position = np.array(self.image.rect.center)

        distances = np.linalg.norm(agent_positions - my_position, axis=1)
        visible_mask = np.ones(len(agent_positions), dtype=bool)  # Все врачи видимы для танка

        if not np.any(visible_mask):
            return None, float('inf')

        visible_distances = distances[visible_mask]
        nearest_index = np.argmin(visible_distances)
        nearest_agent = [agent for agent in enemy_agents if agent.is_alive()][np.where(visible_mask)[0][nearest_index]]

        return nearest_agent, visible_distances[nearest_index]

    def share_enemy_positions(self, enemy_agents: List[Union['RedMeleeAgent', 'BlueMeleeAgent']]):
        for enemy in enemy_agents:
            if enemy.is_alive():
                self.shared_knowledge.update_enemy_position(id(enemy), enemy.image.rect.center)
