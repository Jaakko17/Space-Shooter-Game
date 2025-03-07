import pygame
import random
import math

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Set up the game window
WIDTH = 800
HEIGHT = 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

# Clock for frame rate
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Load assets
player_img = pygame.image.load("playerShip2_blue.png").convert_alpha()
red_ufo_img = pygame.image.load("ufoRed.png").convert_alpha()
green_ufo_img = pygame.image.load("ufoGreen.png").convert_alpha()
bullet_img = pygame.image.load("laserBlue01.png").convert_alpha()
background_img = pygame.image.load("bg_02_h.png").convert()
tnt_img = pygame.image.load("tnt.png").convert_alpha()
explosion_img = pygame.image.load("explosion.png").convert_alpha()
pill_yellow_img = pygame.image.load("pill_yellow.png").convert_alpha()
boss_img = pygame.image.load("InfUFO_1.png").convert_alpha()  # Boss sprite sheet
shoot_sound = pygame.mixer.Sound("sfx_laser1.ogg")
explosion_sound = pygame.mixer.Sound("explosion.wav")
boss_music = pygame.mixer.Sound("Bossmusic.wav")

# Scale images
player_img = pygame.transform.scale(player_img, (50, 50))
red_ufo_img = pygame.transform.scale(red_ufo_img, (50, 50))
green_ufo_img = pygame.transform.scale(green_ufo_img, (50, 50))
bullet_img = pygame.transform.scale(bullet_img, (10, 10))
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
tnt_img = pygame.transform.scale(tnt_img, (30, 30))
explosion_img = pygame.transform.scale(explosion_img, (50, 50))
pill_yellow_img = pygame.transform.scale(pill_yellow_img, (20, 20))

# Explosion frame settings
EXPLOSION_FRAME_WIDTH = 32
EXPLOSION_FRAME_HEIGHT = 32
EXPLOSION_FRAMES = 6
EXPLOSION_ANIMATION_SPEED = 5

# Boss frame settings
BOSS_FRAME_WIDTH = 160  # Width of each frame
BOSS_FRAME_HEIGHT = 40  # Height of each frame (updated to 40 pixels)
BOSS_FRAMES = 9  # Total frames
BOSS_ANIMATION_SPEED = 5  # Animation speed for 9 frames

# Player setup
player_x = WIDTH // 2 - 25
player_y = HEIGHT - 60
player_speed = 10

# Game variables
score = 0
font = pygame.font.SysFont(None, 48)
frame_count = 0
passed_ufos = 0
max_passed_ufos = 10
boss_active = False
boss_health = 50
boss_x = WIDTH // 2 - 80  # Adjusted for wider boss (160px width)
boss_y = -100
boss_speed_x = 4
boss_speed_y = 1
boss_shoot_delay = 1000
last_boss_shot = 0
player_bullets = []  # Player's bullets
boss_bullets = []    # Boss's bullets
boss_frame_index = 0
boss_animation_timer = 0

# Difficulty settings
difficulty = None
game_state = "start"
DIFFICULTY_LEVELS = {
    "easy": {"enemy_speed": 2, "spawn_interval": 180, "shoot_delay": 250, "bullet_speed": 6},
    "medium": {"enemy_speed": 3, "spawn_interval": 120, "shoot_delay": 200, "bullet_speed": 7},
    "hard": {"enemy_speed": 5, "spawn_interval": 90, "shoot_delay": 150, "bullet_speed": 8}
}

# Initialize game objects
red_enemies = []
green_enemies = []
tnt_x = random.randint(0, WIDTH - 30)
tnt_y = -30
tnt_speed = 2
powerup_x = random.randint(0, WIDTH - 20)
powerup_y = -20
powerup_active = False
powerup_timer = 0
powerup_duration = 5000
powerup_spawn_interval = 300
powerup_spawn_timer = 0
last_shot_time = 0
explosions = []

# Game loop
running = True
try:
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if game_state == "start":
                    if event.key == pygame.K_1:
                        difficulty = "easy"
                        game_state = "playing"
                    elif event.key == pygame.K_2:
                        difficulty = "medium"
                        game_state = "playing"
                    elif event.key == pygame.K_3:
                        difficulty = "hard"
                        game_state = "playing"
                    if game_state == "playing":
                        score = 0
                        passed_ufos = 0
                        red_enemies = []
                        green_enemies = []
                        tnt_y = -30
                        powerup_y = -20
                        player_bullets = []
                        boss_bullets = []
                        powerup_active = False
                        boss_active = False
                        boss_health = 50
                        boss_frame_index = 0
                        boss_animation_timer = 0
                        enemy_speed = DIFFICULTY_LEVELS[difficulty]["enemy_speed"]
                        spawn_interval = DIFFICULTY_LEVELS[difficulty]["spawn_interval"]
                        shoot_delay = DIFFICULTY_LEVELS[difficulty]["shoot_delay"]
                        bullet_speed = DIFFICULTY_LEVELS[difficulty]["bullet_speed"]
                        pygame.mixer.music.stop()
                elif game_state == "ending" and event.key == pygame.K_SPACE:
                    game_state = "start"
                    difficulty = None
                    pygame.mixer.music.stop()

        if game_state == "playing":
            # Player movement
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and player_x > 0:
                player_x -= player_speed
            if keys[pygame.K_RIGHT] and player_x < WIDTH - 50:
                player_x += player_speed

            # Player shooting
            current_time = pygame.time.get_ticks()
            if keys[pygame.K_SPACE] and current_time - last_shot_time >= shoot_delay:
                if powerup_active:
                    player_bullets.append([player_x + 10, player_y, 0, -bullet_speed])
                    player_bullets.append([player_x + 30, player_y, 0, -bullet_speed])
                else:
                    player_bullets.append([player_x + 20, player_y, 0, -bullet_speed])
                shoot_sound.play()
                last_shot_time = current_time

            # Power-up timer
            if powerup_active and current_time - powerup_timer >= powerup_duration:
                powerup_active = False

            # Bullet movement
            for bullet in player_bullets[:]:
                bullet[0] += bullet[2]  # x += vx
                bullet[1] += bullet[3]  # y += vy
                if bullet[1] < 0:
                    player_bullets.remove(bullet)

            # Boss activation
            if score >= 200 and not boss_active:
                boss_active = True
                boss_x = WIDTH // 2 - 80
                boss_y = -100
                pygame.mixer.music.load("Bossmusic.wav")
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)

            # Boss movement and shooting
            if boss_active:
                boss_y += boss_speed_y
                boss_x += random.randint(-boss_speed_x, boss_speed_x)
                if boss_x < 0:
                    boss_x = 0
                if boss_x > WIDTH - 160:
                    boss_x = WIDTH - 160
                if boss_y > 50:
                    boss_y = 50

                # Boss shooting
                if current_time - last_boss_shot >= boss_shoot_delay:
                    if boss_health > 10:
                        # Single bullet straight down
                        boss_bullets.append([boss_x + 80, boss_y + 40, 0, 5])
                    else:
                        # Three bullets in 120-degree spread
                        angles = [-60, 0, 60]  # Angles: 60° left, straight down, 60° right
                        for angle in angles:
                            alpha = math.radians(angle)
                            vx = -5 * math.sin(alpha)  # Negative sin to adjust direction
                            vy = 5 * math.cos(alpha)   # Positive y for downward motion
                            boss_bullets.append([boss_x + 80, boss_y + 40, vx, vy])
                    last_boss_shot = current_time

                # Boss animation
                boss_animation_timer += 1
                if boss_animation_timer >= BOSS_ANIMATION_SPEED:
                    boss_animation_timer = 0
                    boss_frame_index = (boss_frame_index + 1) % BOSS_FRAMES

                # Move boss bullets
                for bullet in boss_bullets[:]:
                    bullet[0] += bullet[2]  # x += vx
                    bullet[1] += bullet[3]  # y += vy
                    if bullet[1] > HEIGHT or bullet[0] < 0 or bullet[0] > WIDTH:
                        boss_bullets.remove(bullet)

            # Enemy spawning (disabled during boss fight)
            spawn_timer = spawn_timer + 1 if 'spawn_timer' in locals() else 0
            if spawn_timer >= spawn_interval and not boss_active:
                spawn_timer = 0
                if random.random() < 0.5:
                    red_enemies.append([random.randint(0, WIDTH - 50), 0])
                else:
                    green_enemies.append([random.randint(0, WIDTH - 50), 0])

            # Move enemies
            for red_enemy in red_enemies[:]:
                red_enemy[1] += enemy_speed
                if red_enemy[1] > HEIGHT:
                    red_enemies.remove(red_enemy)
                    score -= 10
                    passed_ufos += 1

            for green_enemy in green_enemies[:]:
                green_enemy[1] += enemy_speed
                if green_enemy[1] > HEIGHT:
                    green_enemies.remove(green_enemy)
                    score -= 20
                    passed_ufos += 1

            # TNT movement (disabled during boss fight)
            if not boss_active:
                tnt_y += tnt_speed
                if tnt_y > HEIGHT:
                    tnt_x = random.randint(0, WIDTH - 30)
                    tnt_y = -30

            # Power-up movement (allowed during boss fight)
            powerup_spawn_timer += 1
            if powerup_spawn_timer >= powerup_spawn_interval and powerup_y < 0:
                powerup_spawn_timer = 0
                powerup_x = random.randint(0, WIDTH - 20)
                powerup_y = 0
            powerup_y += 2
            if powerup_y > HEIGHT:
                powerup_y = -20

            # Collisions
            player_rect = pygame.Rect(player_x, player_y, 50, 50)
            powerup_rect = pygame.Rect(powerup_x, powerup_y, 20, 20)
            if player_rect.colliderect(powerup_rect):
                powerup_active = True
                powerup_timer = current_time
                powerup_y = -20

            for bullet in player_bullets[:]:
                bullet_rect = pygame.Rect(bullet[0], bullet[1], 10, 10)
                for red_enemy in red_enemies[:]:
                    enemy_rect = pygame.Rect(red_enemy[0], red_enemy[1], 50, 50)
                    if bullet_rect.colliderect(enemy_rect):
                        player_bullets.remove(bullet)
                        red_enemies.remove(red_enemy)
                        score += 10
                        break
                for green_enemy in green_enemies[:]:
                    enemy_rect = pygame.Rect(green_enemy[0], green_enemy[1], 50, 50)
                    if bullet_rect.colliderect(enemy_rect):
                        player_bullets.remove(bullet)
                        green_enemies.remove(green_enemy)
                        score += 20
                        break
                tnt_rect = pygame.Rect(tnt_x, tnt_y, 30, 30)
                if not boss_active and bullet_rect.colliderect(tnt_rect):
                    player_bullets.remove(bullet)
                    explosions.append([tnt_x + 15, tnt_y + 15, 0, 0])
                    explosion_sound.play()
                    tnt_x = random.randint(0, WIDTH - 30)
                    tnt_y = -30
                    score -= 20
                boss_rect = pygame.Rect(boss_x, boss_y, 160, 40)  # Updated height to 40
                if boss_active and bullet_rect.colliderect(boss_rect):
                    player_bullets.remove(bullet)
                    boss_health -= 1
                    if boss_health <= 0:
                        boss_active = False
                        boss_y = -100
                        pygame.mixer.music.stop()
                        game_state = "ending"

            # Boss bullet collision with player
            for bullet in boss_bullets[:]:
                boss_bullet_rect = pygame.Rect(bullet[0], bullet[1], 10, 10)
                if player_rect.colliderect(boss_bullet_rect):
                    boss_bullets.remove(bullet)
                    score -= 50
                    if score < 0:
                        game_state = "ending"

            # Update explosions
            for explosion in explosions[:]:
                explosion[3] += 1
                if explosion[3] >= EXPLOSION_ANIMATION_SPEED:
                    explosion[3] = 0
                    explosion[2] = (explosion[2] + 1) % EXPLOSION_FRAMES
                    if explosion[2] == 0:
                        explosions.remove(explosion)

            # Game over conditions
            if score < 0 or passed_ufos >= max_passed_ufos:
                game_state = "ending"

        # Drawing
        window.blit(background_img, (0, 0))  # Draw background each frame
        if game_state == "start":
            title_text = font.render("Space Shooter", True, WHITE)
            easy_text = font.render("1 - Easy", True, GREEN)
            medium_text = font.render("2 - Medium", True, YELLOW)
            hard_text = font.render("3 - Hard", True, RED)
            window.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 3))
            window.blit(easy_text, (WIDTH // 2 - easy_text.get_width() // 2, HEIGHT // 2))
            window.blit(medium_text, (WIDTH // 2 - medium_text.get_width() // 2, HEIGHT // 2 + 50))
            window.blit(hard_text, (WIDTH // 2 - hard_text.get_width() // 2, HEIGHT // 2 + 100))
        elif game_state == "playing":
            window.blit(player_img, (player_x, player_y))
            for red_enemy in red_enemies:
                window.blit(red_ufo_img, (red_enemy[0], red_enemy[1]))
            for green_enemy in green_enemies:
                window.blit(green_ufo_img, (green_enemy[0], green_enemy[1]))
            if not boss_active:
                window.blit(tnt_img, (tnt_x, tnt_y))
            window.blit(pill_yellow_img, (powerup_x, powerup_y))
            for bullet in player_bullets:
                window.blit(bullet_img, (bullet[0], bullet[1]))
            for bullet in boss_bullets:
                window.blit(bullet_img, (bullet[0], bullet[1]))
            if boss_active:
                frame_y = boss_frame_index * BOSS_FRAME_HEIGHT
                source_rect = pygame.Rect(0, frame_y, BOSS_FRAME_WIDTH, BOSS_FRAME_HEIGHT)
                window.blit(boss_img, (boss_x, boss_y), source_rect)
                health_text = font.render(f"Boss HP: {boss_health}", True, WHITE)
                window.blit(health_text, (10, 60))
            for explosion in explosions:
                frame_x = explosion[2] * EXPLOSION_FRAME_WIDTH
                window.blit(explosion_img, (explosion[0] - EXPLOSION_FRAME_WIDTH // 2, explosion[1] - EXPLOSION_FRAME_HEIGHT // 2),
                           (frame_x, 0, EXPLOSION_FRAME_WIDTH, EXPLOSION_FRAME_HEIGHT))
            score_text = font.render(f"Score: {score}", True, WHITE)
            window.blit(score_text, (10, 10))
        elif game_state == "ending":
            for y in range(HEIGHT):
                blue = min(255, y // 2)
                color = (0, 0, blue)
                pygame.draw.line(window, color, (0, y), (WIDTH, y))
            title_font = pygame.font.SysFont(None, 72)
            if score >= 200 and not boss_active:
                ending_text = title_font.render("Boss Defeated!", True, WHITE)
            elif score >= 100:
                ending_text = title_font.render("Congratulations!", True, WHITE)
            else:
                ending_text = title_font.render("Game Over!", True, WHITE)
            score_text = font.render(f"Final Score: {score}", True, WHITE)
            pulse = (math.sin(frame_count * 0.05) + 1) / 2
            pulse_color = (255, int(100 + 155 * pulse), int(100 + 155 * pulse))
            restart_text = font.render("Press SPACE to Restart", True, pulse_color)
            window.blit(ending_text, (WIDTH // 2 - ending_text.get_width() // 2, HEIGHT // 4))
            window.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
            window.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT * 3 // 4))
            frame_count += 1

        pygame.display.update()
        clock.tick(60)

except Exception as e:
    print(f"Game crashed with error: {e}")
    pygame.quit()

pygame.quit()