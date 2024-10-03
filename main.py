import pygame
from RedAgents import RedMeleeAgent
from BlueAgents import BlueMeleeAgent
from constants import *
from BlueBase import BlueBase
from RedBase import RedBase
import random
from Obstacle import Obstacle


running = True
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
screen.fill(LIGHT_GREEN)
blue_base = BlueBase(BLUE, 40, 40)
red_base = RedBase(RED, 700, 600)

# Generating agents
# Calculate spawn area for red agents
spawn_radius = 40  # Adjust this value as needed
spawn_count = 1  # Number of agents to spawn per cooldown
red_agents = []
blue_agents = []
for _ in range(spawn_count):
    red_spawn_x = red_base.rect.centerx + random.randint(-spawn_radius, spawn_radius)
    red_spawn_y = red_base.rect.centery + random.randint(-spawn_radius, spawn_radius)
    red_agents.append(RedMeleeAgent(red_spawn_x, red_spawn_y))

    blue_spawn_x = blue_base.rect.centerx + random.randint(-spawn_radius, spawn_radius)
    blue_spawn_y = blue_base.rect.centery + random.randint(-spawn_radius, spawn_radius)
    blue_agents.append(BlueMeleeAgent(blue_spawn_x, blue_spawn_y))

# Generating obstacles
random.seed(1)
num_obstacles = random.randint(20, 30)
existing_rects = [blue_base.rect, red_base.rect]
obstacles = Obstacle.generate_obstacles(num_obstacles, SCREEN_WIDTH, SCREEN_HEIGHT, existing_rects)


while running:

    for event in pygame.event.get():
        # quit the game
        if event.type == pygame.QUIT:
            running = False

    # Update agents
    for agent in red_agents:
        agent.update(blue_base)  # Use base_blue as the target
    for agent in blue_agents:
        agent.update(red_base)  # Use base_red as the target

    # Draw everything
    screen.fill(LIGHT_GREEN)
    for agent in red_agents:
        agent.draw(screen)
    for agent in blue_agents:
        agent.draw(screen)
    red_base.draw(screen)
    blue_base.draw(screen)
    for obstacle in obstacles:
        obstacle.draw(screen)

    # Update bases to spawn agents
    red_base.update()
    blue_base.update()

    # Add newly spawned agents to the red_agents list
    red_agents.extend(red_base.agents_list)
    red_base.agents_list.clear()
    blue_agents.extend(blue_base.agents_list)
    blue_base.agents_list.clear()

    # Set framerate cap
    clock = pygame.time.Clock()
    clock.tick(30)

    pygame.display.update()

pygame.quit()
