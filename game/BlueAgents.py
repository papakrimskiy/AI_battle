import pygame
import os
from .ImageRect import *


class BlueMeleeAgent:
    def __init__(self, x, y):
            self.image = ImageRect(x, y, os.path.join("game", "BlueMeleeAgent.png")) 
            self.speed = 2         # TO BE DECREASED LATER
            self.max_health = 100
            self.health = self.max_health
            self.damage = 10           
            self.target = None
            self.last_attack_time = 1000  # first attack comes 1 second after contact
            self.attack_cooldown = 2000  # 2 seconds in milliseconds

    def move_towards_red_base(self, red_base):
        if self.target is None:
            self.target = red_base.rect.center

        dx = self.target[0] - self.image.rect.centerx
        dy = self.target[1] - self.image.rect.centery
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance > 0:
            dx = dx / distance
            dy = dy / distance

        self.image.rect.x += dx * self.speed
        self.image.rect.y += dy * self.speed

    def attack(self, blue_base):
        current_time = pygame.time.get_ticks()
        if self.image.rect.colliderect(blue_base.rect):
            self.speed = 0
            if current_time - self.last_attack_time >= self.attack_cooldown:
                blue_base.health -= self.damage
                self.last_attack_time = current_time

    def update(self, red_base):
        self.move_towards_red_base(red_base)
        self.attack(red_base)

    def draw(self, screen):
        screen.blit(self.image.image, self.image.rect)
        self.draw_health_bar(screen)

    def draw_health_bar(self, screen):
        bar_width = self.image.rect.width
        bar_height = 5
        bar_position = (self.image.rect.x, self.image.rect.y - 10)
                
        # Draw health (blue bar for Blue Agents)
        health_width = int(self.health / self.max_health * bar_width)
        pygame.draw.rect(screen, (0, 255, 0), (*bar_position, health_width, bar_height))
