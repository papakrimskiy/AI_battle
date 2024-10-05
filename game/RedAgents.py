import pygame
from .ImageRect import *
import os
import math


class RedMeleeAgent:
    def __init__(self, x, y):
            self.image = ImageRect(x, y, os.path.join("game", "RedMeleeAgent.png")) 
            self.speed = 2
            self.max_health = 100
            self.health = self.max_health
            self.damage = 10            
            self.target = None
            self.last_attack_time = 0  # first attack comes 1 second after contact
            self.attack_cooldown = 1000  # 1 seconds in milliseconds
            self.attack_range = 50  # pixels

    def find_nearest_enemy(self, blue_agents):
        nearest_enemy = None
        min_distance = float('inf')
        for blue_agent in blue_agents:
            distance = math.hypot(self.image.rect.centerx - blue_agent.image.rect.centerx,
                                  self.image.rect.centery - blue_agent.image.rect.centery)
            if distance < min_distance:
                min_distance = distance
                nearest_enemy = blue_agent
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

    def update(self, blue_base, blue_agents):
        if not self.is_alive():
            return  # Don't update dead agents

        nearest_enemy, distance = self.find_nearest_enemy(blue_agents)

        if nearest_enemy and distance <= self.attack_range and nearest_enemy.is_alive():
            self.target = nearest_enemy.image.rect.center
            if distance <= self.attack_range / 2:  # If very close, stop and attack
                self.attack(nearest_enemy)
                if not nearest_enemy.is_alive():
                    self.target = None  # Reset target if enemy is killed
            else:
                self.move_towards_target()
        else:
            self.target = blue_base.rect.center
            self.move_towards_target()
            if self.image.rect.colliderect(blue_base.rect):
                self.speed = 0
                self.attack(blue_base)

    def move_towards_target(self):
        if self.target:
            dx = self.target[0] - self.image.rect.centerx
            dy = self.target[1] - self.image.rect.centery
            dist = math.hypot(dx, dy)
            if dist != 0:
                dx, dy = dx / dist, dy / dist
                self.image.rect.x += dx * self.speed
                self.image.rect.y += dy * self.speed

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