import pygame
from game.RedAgents import RedMeleeAgent
from game.BlueAgents import BlueMeleeAgent
from game.TankAgent import TankAgent  # Добавляем импорт TankAgent
from game.constants import *
from game.BlueBase import BlueBase
from game.RedBase import RedBase
import random
from game.Obstacle import Obstacle
from game.BlueRangedAgent import BlueRangedAgent
from game.RedRangedAgent import RedRangedAgent

# Initialize pygame font
pygame.font.init()
font = pygame.font.Font(None, 36)  # None uses default font, 36 is the font size

running = True
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
screen.fill(LIGHT_GREEN)
blue_base = BlueBase(BLUE, 40, 40)
red_base = RedBase(RED, 700, 600)
red_melee_agents = []  # Changed from red_agents to red_melee_agents
blue_melee_agents = []  # Changed from blue_agents to blue_melee_agents
red_tanks = []  # Добавляем список для красных танков
blue_tanks = []  # Добавляем список для синих танков
red_ranged_agents = []  # Добавляем список для красных дальнобойных агентов
blue_ranged_agents = []  # Добавляем список для синих дальнобойных агентов

# Generating obstacles
random.seed(18) # seed for obstacles, feel free to try different seeds and find better ones
num_obstacles = random.randint(15, 20)
existing_rects = [blue_base.rect, red_base.rect]
obstacles = Obstacle.generate_obstacles(num_obstacles, SCREEN_WIDTH, SCREEN_HEIGHT, existing_rects)

game_over = False
winner = None

# Создаем объект Clock для управления FPS
clock = pygame.time.Clock()

while running:

    for event in pygame.event.get():
        # quit the game
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # Remove dead agents and tanks
    red_melee_agents = [agent for agent in red_melee_agents if agent.is_alive()]
    blue_melee_agents = [agent for agent in blue_melee_agents if agent.is_alive()]
    red_tanks = [tank for tank in red_tanks if tank.is_alive()]
    blue_tanks = [tank for tank in blue_tanks if tank.is_alive()]
    red_ranged_agents = [agent for agent in red_ranged_agents if agent.is_alive()]
    blue_ranged_agents = [agent for agent in blue_ranged_agents if agent.is_alive()]

    # Update agents and tanks
    for red_melee_agent in red_melee_agents:  # Updated variable name
        red_melee_agent.update(blue_base, red_base, blue_melee_agents + blue_tanks + blue_ranged_agents, red_melee_agents + red_tanks + red_ranged_agents, obstacles)
    for blue_melee_agent in blue_melee_agents:  # Updated variable name
        blue_melee_agent.update(red_base, blue_base, red_melee_agents + red_tanks + red_ranged_agents, blue_melee_agents + blue_tanks + blue_ranged_agents, obstacles)
    for red_tank in red_tanks:
        red_tank.update(blue_base, red_base, blue_melee_agents + blue_tanks + blue_ranged_agents, red_melee_agents + red_tanks + red_ranged_agents, obstacles)
    for blue_tank in blue_tanks:
        blue_tank.update(red_base, blue_base, red_melee_agents + red_tanks + red_ranged_agents, blue_melee_agents + blue_tanks + blue_ranged_agents, obstacles)
    for red_ranged_agent in red_ranged_agents:  # Обновляем красных дальнобойных агентов
        red_ranged_agent.update(blue_base, red_base, blue_melee_agents + blue_tanks + blue_ranged_agents, red_melee_agents + red_tanks + red_ranged_agents, obstacles)
    for blue_ranged_agent in blue_ranged_agents:  # Обновляем синих дальнобойных агентов
        blue_ranged_agent.update(red_base, blue_base, red_melee_agents + red_tanks + red_ranged_agents, blue_melee_agents + blue_tanks + blue_ranged_agents, obstacles)

    # Draw everything
    screen.fill(LIGHT_GREEN)
    red_base.draw(screen)
    blue_base.draw(screen)
    for agent in red_melee_agents + blue_melee_agents + red_tanks + blue_tanks + red_ranged_agents + blue_ranged_agents:
        agent.draw(screen)

    for obstacle in obstacles:
        obstacle.draw(screen)

    # Update bases to spawn agents and tanks
    red_base.update()
    blue_base.update()

    # Add newly spawned agents and tanks to the lists
    red_melee_agents.extend([agent for agent in red_base.agents_list if isinstance(agent, RedMeleeAgent)])  # Updated variable name
    red_tanks.extend([agent for agent in red_base.agents_list if isinstance(agent, TankAgent)])
    red_ranged_agents.extend([agent for agent in red_base.agents_list if isinstance(agent, RedRangedAgent)])  # Добавляем дальнобойных агентов
    blue_melee_agents.extend([agent for agent in blue_base.agents_list if isinstance(agent, BlueMeleeAgent)])  # Updated variable name
    blue_tanks.extend([agent for agent in blue_base.agents_list if isinstance(agent, TankAgent)])
    blue_ranged_agents.extend([agent for agent in blue_base.agents_list if isinstance(agent, BlueRangedAgent)])  # Добавляем дальнобойных агентов
    red_base.agents_list.clear()
    blue_base.agents_list.clear()

    # Устанавливаем частоту кадров в 60 FPS
    clock.tick(60)

    pygame.display.update()

    # Check if the game is over
    if not game_over:
        if blue_base.destroyed(screen):
            game_over = True
            winner = "Red"
        elif red_base.destroyed(screen):
            game_over = True
            winner = "Blue"

    if game_over:
        running = False
        game_over_text = font.render(f"Game Over! {winner} wins!", True, (255, 0, 0))
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        screen.blit(game_over_text, text_rect)
        pygame.display.update()
        pygame.time.wait(3000)

pygame.quit()
