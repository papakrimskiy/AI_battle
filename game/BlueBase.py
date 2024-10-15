import pygame
from .BlueAgents import BlueMeleeAgent
from .constants import SCREEN_HEIGHT, SCREEN_WIDTH

class BlueBase:
    def __init__(self, color: tuple, x, y):
        self.rect = pygame.Rect(x, y, 70, 60)
        self.color = color
        self.max_health = 500
        self.health = self.max_health
        self.agents_list = []
        self.last_spawn_time = -4000 # agents start to spawn 1 second after the game starts
        self.spawn_interval = 5000  # 5 seconds in milliseconds


    def draw_health_bar(self, screen):
        bar_width = self.rect.width
        bar_height = 10
        bar_position = (self.rect.x, self.rect.y - 20)

        # Draw background (black bar)
        pygame.draw.rect(screen, (0, 0, 0), (*bar_position, bar_width, bar_height))

        # Draw health (green bar)
        health_width = int(self.health / self.max_health * bar_width)
        pygame.draw.rect(screen, (0, 255, 0), (*bar_position, health_width, bar_height))

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_spawn_time >= self.spawn_interval:
            self.spawn_agent()
            self.last_spawn_time = current_time

    def spawn_agent(self):
        new_agent = BlueMeleeAgent(self.rect.centerx, self.rect.centery)
        self.agents_list.append(new_agent)

    def destroyed(self, screen):
        return self.health <= 0

    def display_game_over(self, screen, message):
        game_over_font = pygame.font.SysFont("Arial", 60)
        text = game_over_font.render(message, True, (255, 0, 0))
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        self.draw_health_bar(screen)
        if self.health <= 0:
            self.display_game_over(screen, "Red team wins!")
