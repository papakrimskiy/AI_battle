import pygame
from ImageRect import *


class RedMeleeAgent:
    def __init__(self, x, y):
            self.image = ImageRect(x, y, "RedMeleeAgent.png") 
            self.speed = 10
            self.health = 100
            self.damage = 10            # TO BE DECREASED LATER
            self.target = None
            self.last_attack_time = 0
            self.attack_cooldown = 2000  # 2 seconds in milliseconds

    def move_towards_blue_base(self, blue_base):
        if self.target is None:
            self.target = blue_base.rect.center

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

    def update(self, blue_base):
        self.move_towards_blue_base(blue_base)
        self.attack(blue_base)

    def draw(self, screen):
        screen.blit(self.image.image, self.image.rect)

