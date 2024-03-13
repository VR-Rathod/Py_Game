import sys
import random
import pygame

pygame.init()

Width, Height = 800, 600
FPS = 60
White = (255, 255, 255)
Black = (0, 0, 0)
Red = (255, 0, 0)
Green = (0, 255, 0)
P_Size = 50
B_Size = 50
Power_Size = 30
Power_Speed = 4
Power_Spawn_Timer_Max = 900
Max_Blocks_On_Screen = 15
Min_Blocks_To_Spawn = 5

pygame.mixer.music.stop()
pygame.mixer.music.load("./tune.mp3")  # Replace with your music file
pygame.mixer.music.play(-1)


class GameObject(pygame.sprite.Sprite):
    def __init__(self, image_path, size, position=None):
        super().__init__()
        original_image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(original_image, size)
        self.rect = self.image.get_rect()
        if position:
            self.rect.topleft = position


class Power(GameObject):
    def __init__(self):
        super().__init__(Green, (Power_Size, Power_Size), (random.randint(0, Width - Power_Size), -Power_Size))

    def update(self):
        global power_spawn_timer
        global power_spawn_delay
        self.rect.y += Power_Speed
        if self.rect.y > Height:
            self.reset_position()
            power_spawn_timer = 0

    def reset_position(self):
        self.rect.y = -Power_Size
        self.rect.x = random.randint(0, Width - Power_Size)



class Player(GameObject):
    def __init__(self, image_path):
        super().__init__(image_path, (P_Size, P_Size), ((Width - P_Size) // 2, Height - P_Size))
        self.original_color = self.image.get_at((0, 0))
        self.invincible = False
        self.invincible_timer = 0
        self.invincible_duration = 15 * FPS
        self.blink_duration = 20
        self.death_animation_frames = 0
        self.death_animation_duration = 30

    def update(self):
        keys = pygame.key.get_pressed()
        self.rect.x += (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * 8
        self.rect.x = max(0, min(Width - P_Size, self.rect.x))

        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False

        if self.death_animation_frames > 0:
            self.death_animation_frames -= 1

    def draw_invincible_bar(self, screen):
        if self.invincible_timer > 0:
            bar_height = (self.invincible_timer / self.invincible_duration) * Height
            bar_rect = pygame.Rect(Width - 20, Height - bar_height, 10, bar_height)
            pygame.draw.rect(screen, Green, bar_rect)


class Block(GameObject):
    def __init__(self, image_path, player_position):
        super().__init__(image_path, (B_Size, B_Size), (random_position(player_position), -B_Size))
        self.speed = random.uniform(1.0, 2.0)

    def update(self):
        global block_speed
        self.rect.y += self.speed
        if self.rect.y > Height:
            self.reset_position()

    def reset_position(self):
        self.rect.y = -B_Size
        self.rect.x = random_position(self.rect.x)
        self.speed = random.uniform(1.0, 2.0)


def random_color():
    return random.randint(100, 200), random.randint(100, 200), random.randint(100, 200)


def random_position(player_x, pattern_factor=100):
    return random.randint(max(0, player_x - pattern_factor), min(Width - B_Size, player_x + pattern_factor))


def start_new_block(player_position):
    block = Block("s.png", player_position)
    All_Sprite.add(block)
    Block_Group.add(block)


def start_new_power():
    power = Power()
    All_Sprite.add(power)
    Power_Group.add(power)


def game_over():
    global score
    global high_score
    global music_paused

    if score > high_score:
        high_score = score

    font = pygame.font.Font(None, 74)
    game_over_text = font.render("Game Over", True, Red)
    screen.blit(game_over_text, (Width // 4, Height // 3))

    restart_font = pygame.font.Font(None, 36)
    restart_text = restart_font.render("Press R to Restart", True, White)
    restart_rect = restart_text.get_rect(center=(Width // 2, 2 * Height // 3))
    pygame.draw.rect(screen, Red, restart_rect.inflate(10, 10))
    screen.blit(restart_text, restart_rect)

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # Unpause the music when restarting the game
                    pygame.mixer.music.unpause()
                    return True

        # Pause the music while waiting for the player to restart
        pygame.mixer.music.pause()

    return False


def restart_game():
    global score
    global block_speed
    global All_Sprite
    global Block_Group
    global Power_Group
    global player
    global power_spawn_timer
    pygame.mixer.music.stop()

    All_Sprite = pygame.sprite.Group()
    Block_Group = pygame.sprite.Group()
    Power_Group = pygame.sprite.Group()
    player = Player("s.png")
    All_Sprite.add(player)
    pygame.mixer.music.play(-1)

    for _ in range(Min_Blocks_To_Spawn):
        block = Block("s.png", player.rect.x)
        All_Sprite.add(block)
        Block_Group.add(block)

    for _ in range(1):
        power = Power()
        All_Sprite.add(power)
        Power_Group.add(power)

    score = 0
    block_speed = 3
    power_spawn_timer = 0


screen = pygame.display.set_mode((Width, Height))
pygame.display.set_caption("Falling Box")

clock = pygame.time.Clock()

All_Sprite = pygame.sprite.Group()
Block_Group = pygame.sprite.Group()
Power_Group = pygame.sprite.Group()
player = Player("s.png")
All_Sprite.add(player)

score = 0
block_speed = 3
power_spawn_timer = 0
power_spawn_delay = 900

font = pygame.font.Font(None, 36)
high_score = 0

try:
    with open("highscore.txt", "r") as file:
        high_score = int(file.read())
except FileNotFoundError:
    pass

class MusicButton:
    def __init__(self, position, size):
        self.rect = pygame.Rect(position, size)
        self.is_on = True

    def toggle(self):
        self.is_on = not self.is_on
        if self.is_on:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()


music_button = MusicButton((Width - 100, 10), (90, 30))

# Main Game- Loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if music_button.rect.collidepoint(event.pos):
                music_button.toggle()

    All_Sprite.update()

    if len(Block_Group) < Max_Blocks_On_Screen and random.randint(0, 100) < 5 and power_spawn_timer == 0 and pygame.time.get_ticks() > 3000:
        start_new_block(player.rect.x)

    if power_spawn_timer == 0:
        power_spawn_delay -= 1
        if power_spawn_delay <= 0:
            start_new_power()
            power_spawn_timer = Power_Spawn_Timer_Max
            power_spawn_delay = 900

    if power_spawn_timer > 0:
        power_spawn_timer -= 1

    if pygame.sprite.spritecollide(player, Block_Group, False):
        if not player.invincible:
            score = 0
            block_speed = 3
            if game_over():
                restart_game()

    if pygame.sprite.spritecollide(player, Power_Group, True):
        player.invincible = True
        player.invincible_timer = player.invincible_duration

    screen.fill(Black)

    if player.invincible and player.invincible_timer % player.blink_duration * 2 < player.blink_duration:
        player.image.set_alpha(0)
    else:
        player.image.set_alpha(255)

    All_Sprite.draw(screen)

    player.draw_invincible_bar(screen)

    score_text = font.render("Score " + str(score), True, White)
    screen.blit(score_text, (10, 10))

    pygame.draw.rect(screen, Green if music_button.is_on else Red, music_button.rect)
    pygame.draw.rect(screen, Black, music_button.rect, 2)
    music_button_text = font.render("Music: " + ("ON" if music_button.is_on else "OFF"), True, White)
    screen.blit(music_button_text, (Width - 90, 15))

    pygame.display.flip()

    clock.tick(FPS)

    score = pygame.time.get_ticks() // 1000