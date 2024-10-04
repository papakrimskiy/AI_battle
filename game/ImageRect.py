import pygame


class ImageRect:
    def __init__(self, x, y, image_path):
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image,
                                      (int(self.image.get_width() / 6) , int(self.image.get_height() / 6)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
