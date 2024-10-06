import pygame
from game.RedAgents import RedMeleeAgent
from game.BlueAgents import BlueMeleeAgent
from game.constants import *
from game.BlueBase import BlueBase
from game.RedBase import RedBase
import random
from game.Obstacle import Obstacle

# Initialize pygame font
pygame.font.init()
font = pygame.font.Font(None, 36)  # None uses default font, 36 is the font size

running = True
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
screen.fill(LIGHT_GREEN)
blue_base = BlueBase(BLUE, 40, 40)
red_base = RedBase(RED, 700, 600)
red_agents = []
blue_agents = []

# Generating obstacles
random.seed(18) # seed for obstacles, feel free to try different seeds and find better ones
num_obstacles = random.randint(15, 20)
existing_rects = [blue_base.rect, red_base.rect]
obstacles = Obstacle.generate_obstacles(num_obstacles, SCREEN_WIDTH, SCREEN_HEIGHT, existing_rects)

game_over = False
winner = None

while running:

    for event in pygame.event.get():
        # quit the game
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # Remove dead agents
    red_agents = [agent for agent in red_agents if agent.is_alive()]
    blue_agents = [agent for agent in blue_agents if agent.is_alive()]

    # Update agents
    for red_agent in red_agents:
        red_agent.update(blue_base, red_base, blue_agents, red_agents, obstacles)
    for blue_agent in blue_agents:
        blue_agent.update(red_base, blue_base, red_agents, blue_agents, obstacles)

    # Draw everything
    screen.fill(LIGHT_GREEN)
    red_base.draw(screen)
    blue_base.draw(screen)
    for agent in red_agents:
        agent.draw(screen)
    for agent in blue_agents:
        agent.draw(screen)
    
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
        pygame.time.wait(3000)


pygame.quit()
