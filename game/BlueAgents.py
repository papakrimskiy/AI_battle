import pygame
import os
from .ImageRect import *
import math
from .RedAgents import RedMeleeAgent


class BlueMeleeAgent:
    def __init__(self, x, y):
            self.image = ImageRect(x, y, os.path.join("game", "BlueMeleeAgent.png")) 
            self.speed = 2
            self.max_health = 100
            self.health = self.max_health
            self.damage = 10           
            self.target = None
            self.last_attack_time = 0  # first attack comes 1 second after contact
            self.attack_cooldown = 1000  # 1 seconds in milliseconds
            self.attack_range = 70  # pixels
            self.defending_base = False
            self.reached_initial_position = False
            self.initial_position = (x, y)

    def find_nearest_enemy(self, red_agents):
        nearest_enemy = None
        min_distance = float('inf')
        for red_agent in red_agents:
            distance = math.hypot(self.image.rect.centerx - red_agent.image.rect.centerx,
                                  self.image.rect.centery - red_agent.image.rect.centery)
            if distance < min_distance:
                min_distance = distance
                nearest_enemy = red_agent
        return nearest_enemy, min_distance

    def attack(self, target):
        if target.health <= 0:
            self.target = None
            return
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            target.health -= self.damage
            target.health = max(0, target.health)
            self.last_attack_time = current_time

    def is_base_under_attack(self, blue_base, red_agents):
        for red_agent in red_agents:
            if red_agent.is_alive() and blue_base.rect.colliderect(red_agent.image.rect):
                return True
        return False

    def update(self, red_base, blue_base, red_agents, blue_agents, obstacles):
        if not self.is_alive():
            return  # Don't update dead agents

        if not self.reached_initial_position:
            self.target = self.initial_position
            self.move_towards_target(obstacles)
            if self.image.rect.center == self.initial_position:
                self.reached_initial_position = True
            return

        base_under_attack = self.is_base_under_attack(blue_base, red_agents)

        if base_under_attack and not self.defending_base:
            distances = sorted([
                (agent, math.hypot(agent.image.rect.centerx - blue_base.rect.centerx,
                                   agent.image.rect.centery - blue_base.rect.centery))
                for agent in blue_agents if (agent.is_alive() and not agent.image.rect.colliderect(red_base.rect))
                                                                  # don't defend if already attacking enemy base
            ], key=lambda x: x[1])
            
            closest_third = distances[:len(distances) // 3]
            if self in [agent for agent, _ in closest_third]:
                self.defending_base = True
                self.target = blue_base.rect.center
        
        if self.defending_base:
            if not base_under_attack:
                self.defending_base = False
            else:
                self.move_towards_target(obstacles)
                nearest_enemy, distance = self.find_nearest_enemy(red_agents)
                if nearest_enemy and distance <= self.attack_range and nearest_enemy.is_alive():
                    self.target = nearest_enemy.image.rect.center
                    self.attack(nearest_enemy)
                return

        nearest_enemy, distance = self.find_nearest_enemy(red_agents)
        
        if nearest_enemy and distance <= self.attack_range and nearest_enemy.is_alive():
            self.target = nearest_enemy.image.rect.center
            if distance <= self.attack_range / 2:  # If very close, stop and attack
                self.attack(nearest_enemy)
                if not nearest_enemy.is_alive():
                    self.target = None  # Reset target if enemy is killed
            else:
                self.move_towards_target(obstacles)
        else:
            self.target = red_base.rect.center
            self.move_towards_target(obstacles)
            if self.image.rect.colliderect(red_base.rect):
                self.speed = 0
                self.attack(red_base)

    def move_towards_target(self, obstacles):
        if not self.target:
            return

        dx = self.target[0] - self.image.rect.centerx
        dy = self.target[1] - self.image.rect.centery
        distance = math.hypot(dx, dy)
        
        if distance > self.speed:
            dx, dy = dx / distance, dy / distance
            new_x = self.image.rect.x + dx * self.speed
            new_y = self.image.rect.y + dy * self.speed
        
            # Check for collisions
            new_rect = self.image.rect.copy()
            new_rect.x = new_x
            new_rect.y = new_y

            if not any(new_rect.colliderect(obstacle.rect) for obstacle in obstacles):
                self.image.rect = new_rect
            else:
                # Simple avoidance: try moving horizontally or vertically
                new_rect_x = self.image.rect.copy()
                new_rect_x.x = new_x
                new_rect_y = self.image.rect.copy()
                new_rect_y.y = new_y

                if not any(new_rect_x.colliderect(obstacle.rect) for obstacle in obstacles):
                    self.image.rect.x = new_x
                elif not any(new_rect_y.colliderect(obstacle.rect) for obstacle in obstacles):
                    self.image.rect.y = new_y

    def draw(self, screen):
        screen.blit(self.image.image, self.image.rect)
        self.draw_health_bar(screen)

    def draw_health_bar(self, screen):
        bar_width = self.image.rect.width
        bar_height = 5
        bar_position = (self.image.rect.x, self.image.rect.y - 10)
                
        # Draw health (green bar)
        health_width = int(self.health / self.max_health * bar_width)
        pygame.draw.rect(screen, (0, 255, 0), (*bar_position, health_width, bar_height))

    def is_alive(self):
        return self.health > 0