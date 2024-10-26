import pygame
import random
import math
from game_manager import GameManager
# Инициализация Pygame
pygame.init()


if __name__ == "__main__":
    game = GameManager()
    game.run()
    pygame.quit()
