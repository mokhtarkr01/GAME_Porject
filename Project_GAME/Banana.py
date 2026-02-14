import pygame
from random import randint


class Banana:
    def __init__(self, image, screen_width, screen_height):
        self.image = pygame.image.load("Pic/Food.png").convert_alpha()
        self.image= pygame.transform.scale(self.image, (100, 100))
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

# In your main game loop:
# score = 0
# banana = Banana('banana_transparent.png', screen_width, screen_height)
#
# while running:
#     # ... other code ...
#
#     banana.deplace()
#
#     # Check collision with hero
#     if banana.collision(persoRect):
#         score += 1  # or += 10, whatever you want
#         banana.reset_position()  # Respawn the banana
#
#     banana.affiche(fenetre)
#
#     # Display score
#     # font.render(f"Score: {score}", ...)