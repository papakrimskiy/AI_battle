import pygame
from RedAgents import RedMeleeAgent
import random

class RedBase:
    def __init__(self, color: tuple, x, y):
        self.rect = pygame.Rect(x, y, 70, 60)
        self.color = color
        self.health = 500
        self.agents_list = []
        self.last_spawn_time = pygame.time.get_ticks()
        self.spawn_interval = 5000  # 5 seconds in milliseconds

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_spawn_time >= self.spawn_interval:
            self.spawn_agent()
            self.last_spawn_time = current_time

    def spawn_agent(self):
        new_agent = RedMeleeAgent(self.rect.x, self.rect.y)
        self.agents_list.append(new_agent)
