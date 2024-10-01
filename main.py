import pygame
from constants import *
import Base
import ImageRect

running = True
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
screen.fill(LIGHT_GREEN)
base_blue = Base.Base(BLUE, 40, 40)
base_red = Base.Base(RED, 700, 600)
agent = ImageRect.ImageRect(200, 200, 'RedMeleeAgent.png')

while running:

    for event in pygame.event.get():
        # quit the game
        if event.type == pygame.QUIT:
            running = False

    base_red.draw(screen)
    base_blue.draw(screen)
    agent.draw(screen)

    pygame.display.update()

pygame.quit()
