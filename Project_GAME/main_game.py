import pygame
from pygame.locals import *
import random
import math
from Banana import Banana
from fruit import fruit

# Initialisation de pygame
pygame.init()
pygame.mixer.init()

# Charger la musique
pygame.mixer.music.load("Sounds/African Safari Music.mp3")
pygame.mixer.music.play(-1)  # boucle infinie

# Dimensions de la fenêtre
WIDTH = 640
HEIGHT = 480
fenetre = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Monkey D Rush ")

# Horloge pour contrôler le FPS
clock = pygame.time.Clock()

# Chargement des images
fond = pygame.image.load("Pic/back_gear1.jpg").convert()
fond = pygame.transform.scale(fond, (WIDTH, HEIGHT))

perso = pygame.image.load("Pic/Hero_gear1.png").convert_alpha()
enemy = pygame.image.load("Pic/lion.png").convert_alpha()
enemy1 = pygame.image.load("Pic/Bird.png").convert_alpha()

# Redimensionnement
perso = pygame.transform.scale(perso, (100, 100))
enemy = pygame.transform.scale(enemy, (180, 100))
enemy1 = pygame.transform.scale(enemy1, (100, 100))

# Rectangles
persoRect = perso.get_rect()
enemyRect = enemy.get_rect()
enemy1Rect = enemy1.get_rect()

# Position initiale
persoRect.bottomleft = (0, HEIGHT)
enemyRect.bottomleft = (WIDTH, HEIGHT)
enemy1Rect.midleft = (WIDTH, 155)  # Bird flies in the middle of screen

# Vitesse des ennemis
enemy_speed = random.randint(2, 6)
enemy1_speed = random.randint(2, 4)

# Variables pour le saut
is_jumping = False
jump_speed = 20
gravity = 1
y_velocity = 0

# Score et bananes
score = 0
bananas = []
num_bananas = 4

# Créer plusieurs bananes
for i in range(num_bananas):
    banana = Banana("Pic/banana_transparent.png", WIDTH, HEIGHT)
    bananas.append(banana)

# Devil Fruit (rare fruit that activates aura)
devil_fruit = None
devil_fruit_spawn_chance = 0.0001  # Very low chance per frame
devil_fruit_active = False

# Police pour afficher le score
font = pygame.font.Font(None, 36)
pause_font = pygame.font.Font(None, 72)
game_over_font = pygame.font.Font(None, 100)

# LOAD SOUNDS ONCE (not in the loop!)
mabrouk_sound = pygame.mixer.Sound("Sounds/score-sound.mp3")
Gear2_sound = pygame.mixer.Sound("Sounds/gear-second.mp3")
Gear3_sound = pygame.mixer.Sound("Sounds/gear-third.mp3")
Gear4_sound = pygame.mixer.Sound("Sounds/gear-fourth.mp3")
gameover_sound = pygame.mixer.Sound("Sounds/gameover_laugh.mp3")
gameover_sound2 = pygame.mixer.Sound("Sounds/gameover_laugh2.mp3")
aura_sound = pygame.mixer.Sound("Sounds/Aura.mp3")

# Track if bird should be active
bird_active = False

# Pause variable
paused = False

# Game Over variable
game_over = False

# Aura variables
aura_active = False
aura_pulse = 0
aura_timer = 0
aura_duration = 300  # 5 seconds at 60 FPS (5 * 60 = 300 frames)

# Boucle principale
continuer = True
while continuer:
    clock.tick(60)  # 60 FPS

    for event in pygame.event.get():
        if event.type == QUIT:
            continuer = False
        if event.type == KEYDOWN:
            # Toggle pause with Escape key (only if not game over)
            if event.key == K_ESCAPE and not game_over:
                paused = not paused
                if paused:
                    pygame.mixer.music.pause()
                else:
                    pygame.mixer.music.unpause()

            # Début du saut si espace pressé (only when not paused and not game over)
            if event.key == K_SPACE and not is_jumping and not paused and not game_over:
                is_jumping = True
                y_velocity = -jump_speed

    # Skip game logic if paused or game over
    if not paused and not game_over:
        # Gestion des touches (appui continu)
        keys = pygame.key.get_pressed()
        if keys[K_LEFT] and persoRect.left > 0:
            persoRect.x -= 5
        if keys[K_RIGHT] and persoRect.right < WIDTH:
            persoRect.x += 5

        # Mise à jour du saut
        if is_jumping:
            persoRect.y += y_velocity
            y_velocity += gravity
            if persoRect.bottom >= HEIGHT:
                persoRect.bottom = HEIGHT
                is_jumping = False
                y_velocity = 0

        # Déplacement de l'ennemi (lion)
        enemyRect.x -= enemy_speed
        if enemyRect.right < 0:
            enemyRect.x = WIDTH + random.randint(50, 300)
            enemy_speed = random.randint(2, 6)

        # Déplacement du bird (enemy1) - only if active
        if bird_active:
            enemy1Rect.x -= enemy1_speed
            if enemy1Rect.right < 0:
                enemy1Rect.x = WIDTH + random.randint(50, 300)
                enemy1_speed = random.randint(2, 4)

        # Update aura pulse animation
        if aura_active:
            aura_pulse += 0.1
            aura_timer += 1
            # Deactivate aura after 5 seconds
            if aura_timer >= aura_duration:
                aura_active = False
                aura_timer = 0

        # Devil Fruit spawn logic (rare)
        if not devil_fruit_active and random.random() < devil_fruit_spawn_chance:
            devil_fruit = fruit("Pic/Devil_fruit.png", WIDTH, HEIGHT)
            devil_fruit_active = True

        # Update Devil Fruit
        if devil_fruit_active and devil_fruit:
            devil_fruit.deplace()

            # Check collision with hero
            if devil_fruit.collision(persoRect):
                # Activate aura
                aura_active = True
                aura_timer = 0
                # Remove devil fruit
                devil_fruit_active = False
                devil_fruit = None

        # Mise à jour des bananes
        for banana in bananas:
            banana.deplace()

            # Vérifier collision avec le héros
            if banana.collision(persoRect):
                old_score = score
                score += 1
                banana.reset_position()

                # Check if we just crossed a milestone
                if score % 10 == 0 and old_score % 10 != 0:
                    mabrouk_sound.play()

                # Gear 2
                if score == 15:
                    fond = pygame.image.load("Pic/back_gear2.jpg").convert()
                    perso = pygame.image.load("Pic/Hero_gear2.png").convert_alpha()
                    fond = pygame.transform.scale(fond, (WIDTH, HEIGHT))
                    perso = pygame.transform.scale(perso, (100, 100))
                    enemy = pygame.image.load("Pic/Hippo_gear.png").convert_alpha()
                    perso = pygame.transform.scale(perso, (100, 100))
                    enemy = pygame.transform.scale(enemy, (160, 100))
                    Gear2_sound.play()
                    bird_active = True  # Activate the bird!

                # Gear 3
                if score == 25:
                    fond = pygame.image.load("Pic/back_gear3.jpg").convert()
                    perso = pygame.image.load("Pic/Hero_gear3.png").convert_alpha()
                    fond = pygame.transform.scale(fond, (WIDTH, HEIGHT))
                    perso = pygame.transform.scale(perso, (100, 100))
                    enemy = pygame.image.load("Pic/Bearr_gear.png").convert_alpha()
                    perso = pygame.transform.scale(perso, (100, 100))
                    enemy = pygame.transform.scale(enemy, (180, 100))
                    Gear3_sound.play()

                # Gear 4
                if score == 35:
                    fond = pygame.image.load("Pic/back_gear4.jpg").convert()
                    perso = pygame.image.load("Pic/Hero_gear4.png").convert_alpha()
                    enemy = pygame.image.load("Pic/Gorilla_gear.png").convert_alpha()
                    fond = pygame.transform.scale(fond, (WIDTH, HEIGHT))
                    perso = pygame.transform.scale(perso, (100, 100))
                    enemy = pygame.transform.scale(enemy, (190, 100))
                    Gear4_sound.play()

                # Activate aura at every 100 points (100, 200, 300, etc.)
                if score % 100 == 0 and score > 0:
                    aura_active = True
                    aura_timer = 0

        # Collision avec le lion
        persoCollisionRect = persoRect.inflate(-30, -30)
        enemyCollisionRect = enemyRect.inflate(-30, -30)
        if persoCollisionRect.colliderect(enemyCollisionRect):
            if aura_active:
                # Kill the lion - reset its position
                enemyRect.x = WIDTH + random.randint(50, 300)
                enemy_speed = random.randint(2, 6)
            else:
                print("Game Over! (Lion)")
                print(f"Score final: {score}")
                game_over = True
                pygame.mixer.music.stop()  # Stop background music
                pygame.mixer.stop()  # Stop all other sounds
                gameover_sound2.play()  # Play only death sound

        # Collision avec le bird (if active)
        if bird_active:
            enemy1CollisionRect = enemy1Rect.inflate(-30, -30)
            if persoCollisionRect.colliderect(enemy1CollisionRect):
                if aura_active:
                    # Kill the bird - reset its position
                    enemy1Rect.x = WIDTH + random.randint(50, 300)
                    enemy1_speed = random.randint(2, 4)
                else:
                    print("Game Over! (Bird)")
                    print(f"Score final: {score}")
                    game_over = True
                    pygame.mixer.music.stop()  # Stop background music
                    pygame.mixer.stop()  # Stop all other sounds
                    gameover_sound.play()  # Play only death sound

    # Affichage
    if game_over:
        # Black screen for Game Over
        fenetre.fill((0, 0, 0))

        # GAME OVER text
        game_over_text = game_over_font.render("GAME OVER", True, (255, 255, 255))
        game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        fenetre.blit(game_over_text, game_over_rect)

        # Final Score text
        final_score_text = font.render(f"Final Score: {score}", True, (255, 255, 255))
        final_score_rect = final_score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        fenetre.blit(final_score_text, final_score_rect)

    else:
        # Normal game display
        fenetre.blit(fond, (0, 0))

        # Draw glowing aura if active (before drawing the hero)
        if aura_active:
            # Create pulsing effect
            pulse_offset = math.sin(aura_pulse) * 10
            aura_sound.play()
            # Draw multiple layers for glow effect
            for i in range(3, 0, -1):
                radius = 60 + pulse_offset + (i * 10)
                alpha = 80 - (i * 20)

                # Create surface for the glow
                glow_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)

                # Draw glow with golden/yellow color
                color = (255, 215, 0, alpha)  # Golden color with transparency
                pygame.draw.circle(glow_surface, color, (radius, radius), int(radius))

                # Position the glow centered on the hero
                glow_pos = (persoRect.centerx - radius, persoRect.centery - radius)
                fenetre.blit(glow_surface, glow_pos)

        fenetre.blit(perso, persoRect)
        fenetre.blit(enemy, enemyRect)

        # Afficher le bird si actif
        if bird_active:
            fenetre.blit(enemy1, enemy1Rect)

        # Afficher les bananes
        for banana in bananas:
            banana.affiche(fenetre)

        # Afficher Devil Fruit if active
        if devil_fruit_active and devil_fruit:
            devil_fruit.affiche(fenetre)
            if devil_fruit.collision(persoRect):
                aura_sound.play()

        # Afficher le score
        score_text = font.render(f"Score: {score}", True, (255, 255, 0))
        fenetre.blit(score_text, (10, 10))

        # Afficher "PAUSED" si le jeu est en pause
        if paused:
            pause_text = pause_font.render("PAUSED", True, (255, 255, 255))
            pause_rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            # Semi-transparent overlay
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            fenetre.blit(overlay, (0, 0))
            fenetre.blit(pause_text, pause_rect)

    pygame.display.update()

pygame.quit()