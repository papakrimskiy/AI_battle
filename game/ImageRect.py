import pygame


class ImageRect:
    def __init__(self, x, y, image_path):
        self.image = pygame.image.load(image_path)
        if 'Ranged' in image_path:
            transform_ratio = 2            
        else:
            transform_ratio = 6

        self.image = pygame.transform.scale(self.image,
                                            (int(self.image.get_width() / transform_ratio) , int(self.image.get_height() / transform_ratio)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
