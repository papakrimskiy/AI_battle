import pygame
import os
import numpy as np
from .ImageRect import ImageRect
from .SharedKnowledge import SharedKnowledge
from .constants import SCREEN_WIDTH, SCREEN_HEIGHT
from typing import List, Tuple, Union, Optional

class BlueRangedAgent:
    shared_knowledge = SharedKnowledge()

    def __init__(self, x: int, y: int, team: str):
        self.team = team
        image_path = os.path.join("game", "BlueRangedAgent.png")
        self.image = ImageRect(x, y, image_path)
        original_size = self.image.image.get_size()
        new_size = (original_size[0] // 3, original_size[1] // 3)
        self.image.image = pygame.transform.scale(self.image.image, new_size)
        self.image.rect = self.image.image.get_rect(center=(x, y))

        self.speed = 1  
        self.max_health = 2000  
        self.health = self.max_health
        self.damage = 50  
        self.base_damage = 15  
        self.target: Optional[Tuple[int, int]] = None
        self.last_attack_time = 0
        self.attack_cooldown = 1500  
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

    def perform_action(self, action, enemy_base, ally_base, enemy_agents, ally_agents, obstalces):
        if action == 'attack':
            self.move_towards_enemy_base(enemy_base)
            self.attack(enemy_base)
        elif action == 'defend':
            self.defend_base(ally_base, enemy_agents)
        elif action == 'retreat':
            self.retreat(ally_base)

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

    def find_nearest_enemy(self, enemy_agents):
        # Find the closest enemy agent
        closest_enemy = None
        closest_distance = float('inf')
        for enemy in enemy_agents:
            if enemy.is_alive():
                distance = self.get_distance(self.image.rect.center, enemy.image.rect.center)
                if distance < closest_distance:
                    closest_distance = distance
                    closest_enemy = enemy
        return closest_enemy

    def get_distance(self, pos1, pos2):
        return np.linalg.norm(np.array(pos1) - np.array(pos2))

    def move_away_from_enemies(self, enemies):
        for enemy in enemies:
            if enemy.is_alive():
                enemy_position = np.array(enemy.image.rect.center)
                my_position = np.array(self.image.rect.center)
                distance = self.get_distance(my_position, enemy_position)

                if distance < self.attack_range:  # If too close to an enemy
                    direction = my_position - enemy_position  # Move away from the enemy
                    normalized_direction = direction / np.linalg.norm(direction)
                    new_position = my_position + self.speed * normalized_direction
                    self.image.rect.center = tuple(np.clip(new_position, [0, 0], [SCREEN_WIDTH, SCREEN_HEIGHT]))

    def attack(self, target):
        if target.health <= 0:
            self.target = None
            return
        
        distance = self.get_distance(self.image.rect.center, target.rect.center)  # Calculate distance
        if distance <= self.attack_range:  # Check if within attack range
            current_time = pygame.time.get_ticks()
            if current_time - self.last_attack_time >= self.attack_cooldown:
                target.health -= self.damage
                target.health = max(0, target.health)
                self.last_attack_time = current_time

    def move_towards(self, target):
        # Ranged agents may not need to move as close as melee agents
        direction = np.array(target) - np.array(self.image.rect.center)
        distance = np.linalg.norm(direction)

        if distance > self.attack_range:  # Only move if outside attack range
            normalized_direction = direction / distance
            new_position = np.array(self.image.rect.center) + self.speed * normalized_direction
            new_position = np.clip(new_position, [0, 0], [SCREEN_WIDTH, SCREEN_HEIGHT])
            self.image.rect.center = tuple(map(int, new_position))

    def choose_action(self, state, ally_base, enemy_agents, obstacles):
        if self.is_base_under_attack(ally_base, enemy_agents, obstacles):
            return 'defend'
        elif self.health < self.max_health * 0.3:
            return 'retreat'
        else:
            return 'attack'

    def defend_base(self, base, enemies):
        # Ranged agents can defend from a distance
        base_center = np.array(base.rect.center)
        my_pos = np.array(self.image.rect.center)

        ideal_distance = 200  # Ranged agents keep a greater distance
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

    def is_base_under_attack(self, ally_base, enemy_agents, obstacles):
        return any(agent.is_alive() and ally_base.rect.colliderect(agent.image.rect) for agent in enemy_agents)

    def retreat(self, ally_base):
        # Ranged agents may not need to retreat as close as melee agents
        direction = np.array(ally_base.rect.center) - np.array(self.image.rect.center)
        distance = np.linalg.norm(direction)

        if distance > self.attack_range:  # Only move if outside attack range
            normalized_direction = direction / distance
            new_position = np.array(self.image.rect.center) + self.speed * normalized_direction
            new_position = np.clip(new_position, [0, 0], [SCREEN_WIDTH, SCREEN_HEIGHT])
            self.image.rect.center = tuple(map(int, new_position))

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
    
    def share_enemy_positions(self, enemy_agents: List[Union['RedMeleeAgent', 'BlueMeleeAgent']]):
        for enemy in enemy_agents:
            if enemy.is_alive():
                self.shared_knowledge.update_enemy_position(id(enemy), enemy.image.rect.center)
