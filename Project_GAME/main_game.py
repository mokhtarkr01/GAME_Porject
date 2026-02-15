import pygame
from pygame.locals import *
import random
import math
import json
import os
from Banana import Banana
from fruit import fruit

# Initialisation de pygame
pygame.init()
pygame.mixer.init()

# High Score System
HIGH_SCORE_FILE = "highscore.json"


def load_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE, 'r') as f:
                data = json.load(f)
                return data.get('high_score', 0)
        except:
            return 0
    return 0


def save_high_score(score):
    with open(HIGH_SCORE_FILE, 'w') as f:
        json.dump({'high_score': score}, f)


high_score = load_high_score()

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
enemy = pygame.transform.scale(enemy, (150, 100))
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
devil_fruit_spawn_chance = 0.001  # Very low chance per frame
devil_fruit_active = False

# Police pour afficher le score
font = pygame.font.Font(None, 36)
pause_font = pygame.font.Font(None, 72)
game_over_font = pygame.font.Font(None, 100)
menu_font = pygame.font.Font(None, 60)
small_font = pygame.font.Font(None, 28)

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


# Particle System
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-5, -1)
        self.life = 60
        self.color = color
        self.size = random.randint(3, 8)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2  # gravity
        self.life -= 1
        self.size = max(1, self.size - 0.1)

    def draw(self, surface):
        alpha = int((self.life / 60) * 255)
        particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        color_with_alpha = (*self.color, alpha)
        pygame.draw.circle(particle_surface, color_with_alpha, (self.size, self.size), int(self.size))
        surface.blit(particle_surface, (int(self.x - self.size), int(self.y - self.size)))


particles = []

# Screen Shake
screen_shake = 0
shake_offset_x = 0
shake_offset_y = 0

# Gear Transition Effect
gear_transition = False
gear_transition_alpha = 0
gear_transition_timer = 0


# Hero Trail Effect
class TrailSegment:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image.copy()
        self.alpha = 150

    def update(self):
        self.alpha -= 15

    def draw(self, surface):
        if self.alpha > 0:
            self.image.set_alpha(self.alpha)
            surface.blit(self.image, (self.x, self.y))


trail_segments = []
trail_timer = 0

# Game States
MENU = 0
PLAYING = 1
GAME_OVER = 2
game_state = MENU

# Menu variables
menu_selection = 0  # 0 = Play, 1 = Quit
menu_pulse = 0


# Function to reset game
def reset_game():
    global score, bananas, devil_fruit, devil_fruit_active, bird_active
    global paused, game_over, aura_active, aura_pulse, aura_timer
    global particles
    global screen_shake, shake_offset_x, shake_offset_y
    global gear_transition, gear_transition_alpha, gear_transition_timer
    global trail_segments, trail_timer, game_state
    global persoRect, enemyRect, enemy1Rect, enemy_speed, enemy1_speed
    global is_jumping, y_velocity, perso, enemy, enemy1, fond

    # Reset score and game state
    score = 0
    paused = False
    game_over = False
    bird_active = False
    game_state = PLAYING

    # Reset positions
    persoRect.bottomleft = (0, HEIGHT)
    enemyRect.bottomleft = (WIDTH, HEIGHT)
    enemy1Rect.midleft = (WIDTH, 155)

    # Reset speeds
    enemy_speed = random.randint(2, 6)
    enemy1_speed = random.randint(2, 4)

    # Reset jump
    is_jumping = False
    y_velocity = 0

    # Reset aura
    aura_active = False
    aura_pulse = 0
    aura_timer = 0

    # Reset particles and effects
    particles.clear()
    trail_segments.clear()
    screen_shake = 0
    shake_offset_x = 0
    shake_offset_y = 0
    gear_transition = False
    gear_transition_alpha = 0
    gear_transition_timer = 0
    trail_timer = 0

    # Reset bananas
    bananas.clear()
    for i in range(num_bananas):
        banana = Banana("Pic/banana_transparent.png", WIDTH, HEIGHT)
        bananas.append(banana)

    # Reset devil fruit
    devil_fruit = None
    devil_fruit_active = False

    # Reset to Gear 1
    fond = pygame.image.load("Pic/back_gear1.jpg").convert()
    fond = pygame.transform.scale(fond, (WIDTH, HEIGHT))
    perso = pygame.image.load("Pic/Hero_gear1.png").convert_alpha()
    perso = pygame.transform.scale(perso, (100, 100))
    enemy = pygame.image.load("Pic/lion.png").convert_alpha()
    enemy = pygame.transform.scale(enemy, (180, 100))
    enemy1 = pygame.image.load("Pic/Bird.png").convert_alpha()
    enemy1 = pygame.transform.scale(enemy1, (100, 100))

    # Restart music
    pygame.mixer.music.play(-1)


# Boucle principale
continuer = True
while continuer:
    clock.tick(60)  # 60 FPS

    for event in pygame.event.get():
        if event.type == QUIT:
            continuer = False
        if event.type == KEYDOWN:
            # Menu controls
            if game_state == MENU:
                if event.key == K_UP or event.key == K_DOWN:
                    menu_selection = 1 - menu_selection  # Toggle between 0 and 1
                if event.key == K_RETURN or event.key == K_SPACE:
                    if menu_selection == 0:  # Play
                        reset_game()
                    else:  # Quit
                        continuer = False

            # Game Over controls
            elif game_state == GAME_OVER:
                if event.key == K_r:  # Restart
                    pygame.mixer.stop()  # Stop all sounds including game over sound
                    reset_game()
                elif event.key == K_m:  # Menu
                    pygame.mixer.stop()  # Stop all sounds including game over sound
                    game_state = MENU
                    menu_selection = 0
                elif event.key == K_ESCAPE:  # Quit
                    continuer = False

            # Playing controls
            elif game_state == PLAYING:
                # Toggle pause with Escape key
                if event.key == K_ESCAPE:
                    paused = not paused
                    if paused:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()

                # Début du saut si espace pressé
                if event.key == K_SPACE and not is_jumping and not paused:
                    is_jumping = True
                    y_velocity = -jump_speed

    # MENU STATE
    if game_state == MENU:
        menu_pulse += 0.1

        fenetre.fill((0, 0, 0))

        # Title
        title_text = game_over_font.render("MONKEY D RUSH", True, (255, 215, 0))
        title_rect = title_text.get_rect(center=(WIDTH // 2, 100))
        fenetre.blit(title_text, title_rect)

        # High Score
        high_score_text = font.render(f"High Score: {high_score}", True, (255, 255, 255))
        high_score_rect = high_score_text.get_rect(center=(WIDTH // 2, 180))
        fenetre.blit(high_score_text, high_score_rect)

        # Menu options
        play_color = (255, 255, 0) if menu_selection == 0 else (150, 150, 150)
        quit_color = (255, 255, 0) if menu_selection == 1 else (150, 150, 150)

        # Add pulse effect to selected option
        pulse_scale = 1.0 + math.sin(menu_pulse) * 0.1

        play_text = menu_font.render("PLAY", True, play_color)
        if menu_selection == 0:
            play_text = pygame.transform.scale(play_text,
                                               (int(play_text.get_width() * pulse_scale),
                                                int(play_text.get_height() * pulse_scale)))
        play_rect = play_text.get_rect(center=(WIDTH // 2, 280))
        fenetre.blit(play_text, play_rect)

        quit_text = menu_font.render("QUIT", True, quit_color)
        if menu_selection == 1:
            quit_text = pygame.transform.scale(quit_text,
                                               (int(quit_text.get_width() * pulse_scale),
                                                int(quit_text.get_height() * pulse_scale)))
        quit_rect = quit_text.get_rect(center=(WIDTH // 2, 350))
        fenetre.blit(quit_text, quit_rect)

        # Instructions
        inst_text = small_font.render("Use Arrow Keys to select, ENTER to confirm", True, (200, 200, 200))
        inst_rect = inst_text.get_rect(center=(WIDTH // 2, 430))
        fenetre.blit(inst_text, inst_rect)

    # GAME OVER STATE
    elif game_state == GAME_OVER:
        fenetre.fill((0, 0, 0))

        # GAME OVER text
        game_over_text = game_over_font.render("GAME OVER", True, (255, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
        fenetre.blit(game_over_text, game_over_rect)

        # Final Score text
        final_score_text = font.render(f"Final Score: {score}", True, (255, 255, 255))
        final_score_rect = final_score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 10))
        fenetre.blit(final_score_text, final_score_rect)

        # High Score text
        if score > high_score:
            new_high_text = font.render("NEW HIGH SCORE!", True, (255, 215, 0))
            new_high_rect = new_high_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
            fenetre.blit(new_high_text, new_high_rect)
        else:
            high_score_text = font.render(f"High Score: {high_score}", True, (200, 200, 200))
            high_score_rect = high_score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
            fenetre.blit(high_score_text, high_score_rect)

        # Options
        restart_text = small_font.render("Press R to Restart", True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))
        fenetre.blit(restart_text, restart_rect)

        menu_text = small_font.render("Press M for Menu", True, (255, 255, 255))
        menu_rect = menu_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 110))
        fenetre.blit(menu_text, menu_rect)

        quit_text = small_font.render("Press ESC to Quit", True, (255, 255, 255))
        quit_rect = quit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 140))
        fenetre.blit(quit_text, quit_rect)

    # PLAYING STATE
    elif game_state == PLAYING:
        # Skip game logic if paused
        if not paused:
            # Update trail effect
            trail_timer += 1
            if trail_timer >= 3:  # Add trail segment every 3 frames
                trail_segments.append(TrailSegment(persoRect.x, persoRect.y, perso))
                trail_timer = 0

            # Update and remove old trail segments
            for segment in trail_segments[:]:
                segment.update()
                if segment.alpha <= 0:
                    trail_segments.remove(segment)

            # Update particles
            for particle in particles[:]:
                particle.update()
                if particle.life <= 0:
                    particles.remove(particle)

            # Update screen shake
            if screen_shake > 0:
                screen_shake -= 1
                shake_offset_x = random.randint(-screen_shake, screen_shake)
                shake_offset_y = random.randint(-screen_shake, screen_shake)
            else:
                shake_offset_x = 0
                shake_offset_y = 0

            # Update gear transition
            if gear_transition:
                gear_transition_timer += 1
                if gear_transition_timer < 30:
                    gear_transition_alpha = min(255, gear_transition_alpha + 17)
                elif gear_transition_timer < 60:
                    gear_transition_alpha = max(0, gear_transition_alpha - 17)
                else:
                    gear_transition = False
                    gear_transition_timer = 0
                    gear_transition_alpha = 0

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

                # Create particle explosion
                for _ in range(20):
                    particles.append(Particle(
                        banana.rect.centerx,
                        banana.rect.centery,
                        (255, 255, 0)  # Yellow particles
                    ))

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
                    screen_shake = 15  # Strong shake
                    gear_transition = True
                    gear_transition_alpha = 0
                    gear_transition_timer = 0

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
                    screen_shake = 15
                    gear_transition = True
                    gear_transition_alpha = 0
                    gear_transition_timer = 0

                # Gear 4
                if score == 35:
                    fond = pygame.image.load("Pic/back_gear4.jpg").convert()
                    perso = pygame.image.load("Pic/Hero_gear4.png").convert_alpha()
                    enemy = pygame.image.load("Pic/Gorilla_gear.png").convert_alpha()
                    fond = pygame.transform.scale(fond, (WIDTH, HEIGHT))
                    perso = pygame.transform.scale(perso, (100, 100))
                    enemy = pygame.transform.scale(enemy, (190, 100))
                    Gear4_sound.play()
                    screen_shake = 20  # Strongest shake
                    gear_transition = True
                    gear_transition_alpha = 0
                    gear_transition_timer = 0

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
                # Create explosion particles
                for _ in range(30):
                    particles.append(Particle(
                        enemyRect.centerx,
                        enemyRect.centery,
                        (255, 100, 0)  # Orange/red particles
                    ))
                screen_shake = 10
            else:
                print("Game Over! (Lion)")
                print(f"Score final: {score}")
                game_state = GAME_OVER
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)
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
                    # Create explosion particles
                    for _ in range(30):
                        particles.append(Particle(
                            enemy1Rect.centerx,
                            enemy1Rect.centery,
                            (255, 100, 0)  # Orange/red particles
                        ))
                    screen_shake = 10
                else:
                    print("Game Over! (Bird)")
                    print(f"Score final: {score}")
                    game_state = GAME_OVER
                    if score > high_score:
                        high_score = score
                        save_high_score(high_score)
                    pygame.mixer.music.stop()  # Stop background music
                    pygame.mixer.stop()  # Stop all other sounds
                    gameover_sound.play()  # Play only death sound

        # Display section for PLAYING state
        # Normal game display
        fenetre.blit(fond, (shake_offset_x, shake_offset_y))

        # Draw trail segments (before hero)
        for segment in trail_segments:
            segment.draw(fenetre)

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
                glow_pos = (persoRect.centerx - radius + shake_offset_x, persoRect.centery - radius + shake_offset_y)
                fenetre.blit(glow_surface, glow_pos)

        # Apply shake offset to all game objects
        perso_pos = (persoRect.x + shake_offset_x, persoRect.y + shake_offset_y)
        enemy_pos = (enemyRect.x + shake_offset_x, enemyRect.y + shake_offset_y)

        fenetre.blit(perso, perso_pos)
        fenetre.blit(enemy, enemy_pos)

        # Afficher le bird si actif
        if bird_active:
            enemy1_pos = (enemy1Rect.x + shake_offset_x, enemy1Rect.y + shake_offset_y)
            fenetre.blit(enemy1, enemy1_pos)

        # Draw particles
        for particle in particles:
            particle.draw(fenetre)

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

        # Gear transition flash effect
        if gear_transition and gear_transition_alpha > 0:
            flash_surface = pygame.Surface((WIDTH, HEIGHT))
            flash_surface.set_alpha(gear_transition_alpha)
            flash_surface.fill((255, 255, 255))
            fenetre.blit(flash_surface, (0, 0))

            # Display "GEAR UP!" text during transition
            if gear_transition_timer < 45:
                gear_text = game_over_font.render("GEAR UP!", True, (255, 215, 0))
                gear_text_rect = gear_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                fenetre.blit(gear_text, gear_text_rect)

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