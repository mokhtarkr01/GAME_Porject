import pygame
from random import randint


class fruit:
    def __init__(self, image, screen_width, screen_height):
        self.image = pygame.image.load("Pic/Devil_fruit.png").convert_alpha()
        self.image= pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.reset_position()

    def reset_position(self):
        # Spawn at random X position at the top
        self.rect.x = randint(0, self.screen_width - self.rect.width)
        self.rect.y = -self.rect.height  # Start above the screen
        self.vitesse = randint(1, 5)

    def deplace(self):
        self.rect = self.rect.move(0, self.vitesse)

        # Respawn if banana goes off screen bottom
        if self.rect.top > self.screen_height:
            self.reset_position()

    def affiche(self, fenetre):
        fenetre.blit(self.image, self.rect)

    def collision(self, targetRect):
        return self.rect.colliderect(targetRect)