import pygame
import random
import ImageRect

class Obstacle:
    def __init__(self, x, y, obstacle_type):
        self.x = x
        self.y = y
        self.obstacle_type = obstacle_type # tree or rock
        self.size = (40, 40)  # Adjust this based on your actual image sizes
        self.rect = pygame.Rect(x, y, self.size[0], self.size[1])
        
        if obstacle_type == "tree":
            self.image = pygame.image.load("tree.png")
        elif obstacle_type == "rock":
            self.image = pygame.image.load("rock.png")

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    @staticmethod
    def generate_obstacles(num_obstacles, screen_width, screen_height, existing_rects):
        obstacles = []
        for _ in range(num_obstacles):
            while True:
                x = random.randint(0, screen_width - 40)
                y = random.randint(0, screen_height - 40)
                new_rect = pygame.Rect(x, y, 40, 40)
                
                if not any(new_rect.colliderect(rect) for rect in existing_rects):
                    obstacle_type = random.choice(["tree", "tree", "rock"])
                    obstacles.append(Obstacle(x, y, obstacle_type))
                    existing_rects.append(new_rect)
                    break
        return obstacles