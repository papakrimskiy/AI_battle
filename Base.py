import pygame


class Base:
    def __init__(self, color: tuple, x, y):
        self.rect = pygame.Rect(x, y, 70, 60)
        self.color = color
        self.health = 500

        self.agents_list = []

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
