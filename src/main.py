# Author: Atanu Sarkar
# Space Invaders (my version)
# v1.1.4
# 11-April-2020, 03:04 AM (IST)
from cortex import Cortex
import multiprocessing
import time
import pygame
import random
import math
from pygame import mixer
import time
from log import main

# import sched

# game constants
WIDTH = 800
HEIGHT = 600

# global variables
running = True
pause_state = 0
score = 0
highest_score = 0
life = 3
kills = 0
difficulty = 1
level = 1
max_kills_to_difficulty_up = 5
max_difficulty_to_level_up = 2
initial_player_velocity = 3.0
initial_enemy_velocity = 1.0
weapon_shot_velocity = 5.0
single_frame_rendering_time = 0
total_time = 0
frame_count = 0
fps = 0

pad = 0
engagement = 0
smile = False
blink = False
relax = 0
red_alpha = 0
blue_alpha = 0
# game objects
player = type('Player', (), {})()
bullet = type('Bullet', (), {})()
enemies = []
lasers = []

# initialize pygame
pygame.init()

# Input key states (keyboard)
LEFT_ARROW_KEY_PRESSED = 0
RIGHT_ARROW_KEY_PRESSED = 0
UP_ARROW_KEY_PRESSED = 0
SPACE_BAR_PRESSED = 0
ENTER_KEY_PRESSED = 0
ESC_KEY_PRESSED = 0
window_initialized = False
# create display window
window = None
pygame.display.set_caption("Space Invaders")
window_icon = pygame.image.load("res/images/alien.png")
pygame.display.set_icon(window_icon)

# game sounds
pause_sound = None
level_up_sound = None
weapon_annihilation_sound = None
game_over_sound = None

# create background
background_img = pygame.image.load("res/images/background.png")  # 800 x 600 px image
background_music_paths = ["res/sounds/Space_Invaders_Music.ogg",
                          "res/sounds/Space_Invaders_Music_x2.ogg",
                          "res/sounds/Space_Invaders_Music_x4.ogg",
                          "res/sounds/Space_Invaders_Music_x8.ogg",
                          "res/sounds/Space_Invaders_Music_x16.ogg",
                          "res/sounds/Space_Invaders_Music_x32.ogg"]


# function for background music
def init_background_music():
    if difficulty == 1:
        mixer.quit()
        mixer.init()
    if 1 <= difficulty <= 6:
        mixer.music.load(background_music_paths[int(difficulty) - 1])
    elif difficulty < 1:
        mixer.music.load(background_music_paths[0])
    else:
        mixer.music.load(background_music_paths[5])
    mixer.music.play(-1)


# create player class
class Player:
    def __init__(self, img_path, width, height, x, y, dx, dy, kill_sound_path):
        self.img_path = img_path
        self.img = pygame.image.load(self.img_path)
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.kill_sound_path = kill_sound_path
        self.kill_sound = mixer.Sound(self.kill_sound_path)

    def draw(self):
        window.blit(self.img, (self.x, self.y))


# create enemy class
class Enemy:
    def __init__(self, img_path, width, height, x, y, dx, dy, kill_sound_path):
        self.img_path = img_path
        self.img = pygame.image.load(self.img_path)
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.kill_sound_path = kill_sound_path
        self.kill_sound = mixer.Sound(self.kill_sound_path)

    def draw(self):
        window.blit(self.img, (self.x, self.y))


# create bullet class
class Bullet:
    def __init__(self, img_path, width, height, x, y, dx, dy, fire_sound_path):
        self.img_path = img_path
        self.img = pygame.image.load(self.img_path)
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.fired = False
        self.fire_sound_path = fire_sound_path
        self.fire_sound = mixer.Sound(self.fire_sound_path)

    def draw(self):
        if self.fired:
            window.blit(self.img, (self.x, self.y))


# create laser class
class Laser:
    def __init__(self, img_path, width, height, x, y, dx, dy, shoot_probability, relaxation_time, beam_sound_path):
        self.img_path = img_path
        self.img = pygame.image.load(self.img_path)
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.beamed = False
        self.shoot_probability = shoot_probability
        self.shoot_timer = 0
        self.relaxation_time = relaxation_time
        self.beam_sound_path = beam_sound_path
        self.beam_sound = mixer.Sound(self.beam_sound_path)

    def draw(self):
        if self.beamed:
            window.blit(self.img, (self.x, self.y))

# function for scoreboard in the top left
def scoreboard():
    x_offset = 10
    y_offset = 10
    # set font type and size
    font = pygame.font.SysFont("calibre", 16)

    # render font and text sprites
    score_sprint = font.render("SCORE : " + str(score), True, (255, 255, 255))
    highest_score_sprint = font.render("HI-SCORE : " + str(highest_score), True, (255, 255, 255))
    level_sprint = font.render("LEVEL : " + str(level), True, (255, 255, 255))
    difficulty_sprint = font.render("DIFFICULTY : " + str(difficulty), True, (255, 255, 255))
    life_sprint = font.render("LIFE LEFT : " + str(life) + " | " + ("@ " * life), True, (255, 255, 255))
    pad_sprint = font.render("PAD : " + str(pad), True, (255, 255, 255))
    engagement_sprint = font.render("Engagement : " + str(engagement), True, (255, 255, 255))
    relax_sprint = font.render("Relax : " + str(relax), True, (255, 255, 255))
    # performance info
    fps_sprint = font.render("FPS : " + str(fps), True, (255, 255, 255))
    frame_time_in_ms = round(single_frame_rendering_time * 1000, 2)
    frame_time_sprint = font.render("FT : " + str(frame_time_in_ms) + " ms", True, (255, 255, 255))

    # place the font sprites on the screen
    window.blit(score_sprint, (x_offset, y_offset))
    window.blit(highest_score_sprint, (x_offset, y_offset + 20))
    window.blit(level_sprint, (x_offset, y_offset + 40))
    window.blit(difficulty_sprint, (x_offset, y_offset + 60))
    window.blit(life_sprint, (x_offset, y_offset + 80))
    window.blit(fps_sprint, (WIDTH - 80, y_offset))
    window.blit(frame_time_sprint, (WIDTH - 80, y_offset + 20))
    window.blit(pad_sprint, (x_offset, y_offset + 100))
    window.blit(engagement_sprint, (x_offset, y_offset + 120))
    window.blit(relax_sprint, (x_offset, y_offset + 140))


def collision_check(object1, object2):
    x1_cm = object1.x + object1.width / 2
    y1_cm = object1.y + object1.width / 2
    x2_cm = object2.x + object2.width / 2
    y2_cm = object2.y + object2.width / 2
    distance = math.sqrt(math.pow((x2_cm - x1_cm), 2) + math.pow((y2_cm - y1_cm), 2))
    return distance < ((object1.width + object2.width) / 2)


# def collision_check(object1_x, object1_y, object1_diameter, object2_x, object2_y, object2_diameter):
#     x1_cm = object1_x + object1_diameter / 2
#     y1_cm = object1_y + object1_diameter / 2
#     x2_cm = object2_x + object2_diameter / 2
#     y2_cm = object2_y + object2_diameter / 2
#     distance = math.sqrt(math.pow((x2_cm - x1_cm), 2) + math.pow((y2_cm - y1_cm), 2))
#     return distance < ((object1_diameter + object2_diameter) / 2)

# level up animation when the player reaches the threshold for new level/difficulty
def level_up():
    global life
    global level
    global difficulty
    global max_difficulty_to_level_up
    level_up_sound.play()
    level += 1
    life += 1       # grant a life
    difficulty = 1  # reset difficulty
    # TODO: change player and bullet speeds, enemy laser speed and firing probability wrt level
    #  come up with interesting gameplay ideas.
    #  variables in hand:
    #  1. speed of weapons
    #  2. enemy (up to 6) & player velocity
    #  3. laser firing probability
    #  future ideas:
    #  1. add new type of enemies
    #  2. add new player spaceship and bullets!
    #  future features:
    #  1. create player profile ad store highest score to DB
    #  2. multiplayer
    if level % 2 == 0:
        player.dx += 1
        bullet.dy += 1
        max_difficulty_to_level_up += 2
        for each_laser in lasers:
            each_laser.shoot_probability += 0.1
            if each_laser.shoot_probability > 1.0:
                each_laser.shoot_probability = 1.0
            each_laser.relaxation_time -= 10
            if each_laser.relaxation_time < 5:
                each_laser.relaxation_time = 5
    if max_difficulty_to_level_up > 9:
        max_difficulty_to_level_up = 9


    font = pygame.font.SysFont("freesansbold", 64)
    gameover_sprint = font.render("LEVEL UP", True, (255, 255, 255))
    window.blit(gameover_sprint, (WIDTH / 2 - 120, HEIGHT / 2 - 32))
    pygame.display.update()
    init_game()
    time.sleep(1.0)


def respawn(enemy_obj):
    enemy_obj.x = random.randint(0, (WIDTH - enemy_obj.width))
    enemy_obj.y = random.randint(((HEIGHT / 10) * 1 - (enemy_obj.height / 2)),
                                 ((HEIGHT / 10) * 4 - (enemy_obj.height / 2)))


def kill_enemy(player_obj, bullet_obj, enemy_obj):
    global score
    global kills
    global difficulty
    bullet_obj.fired = False
    enemy_obj.kill_sound.play()
    bullet_obj.x = player_obj.x + player_obj.width / 2 - bullet_obj.width / 2
    bullet_obj.y = player_obj.y + bullet_obj.height / 2
    score = score + 10 * difficulty * level
    kills += 1
    if kills % max_kills_to_difficulty_up == 0:
        difficulty += 1

        init_background_music()
    print("Score:", score)
    print("level:", level)
    print("difficulty:", difficulty)
    respawn(enemy_obj)

# respawn function
def rebirth(player_obj):
    player_obj.x = (WIDTH / 2) - (player_obj.width / 2)
    player_obj.y = (HEIGHT / 10) * 9 - (player_obj.height / 2)


def gameover_screen():
    scoreboard()
    font = pygame.font.SysFont("freesansbold", 64)
    gameover_sprint = font.render("GAME OVER", True, (255, 255, 255))
    window.blit(gameover_sprint, (WIDTH / 2 - 140, HEIGHT / 2 - 32))
    pygame.display.update()

    mixer.music.stop()
    game_over_sound.play()
    time.sleep(13.0)
    mixer.quit()


def gameover_screen_no_engagement():
    scoreboard()
    font = pygame.font.SysFont("freesansbold", 64)
    gameover_sprint = font.render("GAME OVER", True, (255, 255, 255))
    window.blit(gameover_sprint, (WIDTH / 2 - 140, HEIGHT / 2 - 32))
    gameover_engagement_sprint = font.render("Please pay more attention!", True, (255, 255, 255))
    window.blit(gameover_engagement_sprint, (WIDTH / 2 - 250, HEIGHT / 2 - 0))
    pygame.display.update()

    mixer.music.stop()
    game_over_sound.play()
    time.sleep(13.0)
    mixer.quit()


def gameover():
    global running
    global score
    global highest_score

    if score > highest_score:
        highest_score = score

    # console display
    print("----------------")
    print("GAME OVER !!")
    print("----------------")
    print("you died at")
    print("Level:", level)
    print("difficulty:", difficulty)
    print("Your Score:", score)
    print("----------------")
    print("Try Again !!")
    print("----------------")
    running = False
    gameover_screen()

def gameover_no_engagement():
    global running
    global score
    global highest_score

    if score > highest_score:
        highest_score = score

    # console display
    print("----------------")
    print("GAME OVER !!")
    print("----------------")
    print("PLEASE PAY MORE ATTENTION TO THE GAME!")
    print("----------------")
    print("you died at")
    print("Level:", level)
    print("difficulty:", difficulty)
    print("Your Score:", score)
    print("----------------")
    print("Try Again !!")
    print("----------------")
    running = False
    gameover_screen_no_engagement()


def kill_player(player_obj, enemy_obj, laser_obj):
    global life
    laser_obj.beamed = False
    player_obj.kill_sound.play()
    laser_obj.x = enemy_obj.x + enemy_obj.width / 2 - laser_obj.width / 2
    laser_obj.y = enemy_obj.y + laser_obj.height / 2
    life -= 1
    print("Life Left:", life)
    if life > 0:
        rebirth(player_obj)
    else:
        gameover()


def destroy_weapons(player_obj, bullet_obj, enemy_obj, laser_obj):
    bullet_obj.fired = False
    laser_obj.beamed = False
    weapon_annihilation_sound.play()
    bullet_obj.x = player_obj.x + player_obj.width / 2 - bullet_obj.width / 2
    bullet_obj.y = player_obj.y + bullet_obj.height / 2
    laser_obj.x = enemy_obj.x + enemy_obj.width / 2 - laser_obj.width / 2
    laser_obj.y = enemy_obj.y + laser_obj.height / 2


# timer = sched.scheduler(time.time, time.sleep)
#
#
# def calculate_fps(sc):
#     global frame_count
#     fps = frame_count
#     print("FPS =", fps)
#     frame_count = 0
#     timer.enter(60, 1, calculate_fps, (sc,))
#
#
# timer.enter(60, 1, calculate_fps, (timer, ))
# timer.run()


def pause_game():
    pause_sound.play()
    scoreboard()
    font = pygame.font.SysFont("freesansbold", 64)
    gameover_sprint = font.render("PAUSED", True, (255, 255, 255))
    window.blit(gameover_sprint, (WIDTH / 2 - 80, HEIGHT / 2 - 32))
    pygame.display.update()
    mixer.music.pause()


def init_game():
    global pause_sound
    global level_up_sound
    global game_over_sound
    global weapon_annihilation_sound
    global window
    global window_initialized
    if not window_initialized:
        window = pygame.display.set_mode((WIDTH, HEIGHT))
        window_initialized = True
    pause_sound = mixer.Sound("res/sounds/pause.wav")
    level_up_sound = mixer.Sound("res/sounds/1up.wav")
    game_over_sound = mixer.Sound("res/sounds/gameover.wav")
    weapon_annihilation_sound = mixer.Sound("res/sounds/annihilation.wav")

    # player
    player_img_path = "res/images/spaceship.png"  # 64 x 64 px image
    player_width = 64
    player_height = 64
    player_x = (WIDTH / 2) - (player_width / 2)
    player_y = (HEIGHT / 10) * 9 - (player_height / 2)
    player_dx = initial_player_velocity
    player_dy = 0
    player_kill_sound_path = "res/sounds/explosion.wav"

    global player
    player = Player(player_img_path, player_width, player_height, player_x, player_y, player_dx, player_dy,
                    player_kill_sound_path)

    # bullet
    bullet_img_path = "res/images/bullet.png"  # 32 x 32 px image
    bullet_width = 32
    bullet_height = 32
    bullet_x = player_x + player_width / 2 - bullet_width / 2
    bullet_y = player_y + bullet_height / 2
    bullet_dx = 0
    bullet_dy = weapon_shot_velocity
    bullet_fire_sound_path = "res/sounds/gunshot.wav"

    global bullet
    bullet = Bullet(bullet_img_path, bullet_width, bullet_height, bullet_x, bullet_y, bullet_dx, bullet_dy,
                    bullet_fire_sound_path)

    # enemy (number of enemy = level number)
    enemy_img_path = "res/images/enemy.png"  # 64 x 64 px image
    enemy_width = 64
    enemy_height = 64
    enemy_dx = initial_enemy_velocity
    enemy_dy = (HEIGHT / 10) / 2
    enemy_kill_sound_path = "res/sounds/enemykill.wav"

    # laser beam (equals number of enemies and retains corresponding enemy position)
    laser_img_path = "res/images/beam.png"  # 24 x 24 px image
    laser_width = 24
    laser_height = 24
    laser_dx = 0
    laser_dy = weapon_shot_velocity
    shoot_probability = 0.3
    relaxation_time = 80
    laser_beam_sound_path = "res/sounds/laser.wav"

    global enemies
    global lasers

    enemies.clear()
    lasers.clear()

    for lev in range(level):
        enemy_x = random.randint(0, (WIDTH - enemy_width))
        enemy_y = random.randint(((HEIGHT / 10) * 1 - (enemy_height / 2)), ((HEIGHT / 10) * 4 - (enemy_height / 2)))
        laser_x = enemy_x + enemy_width / 2 - laser_width / 2
        laser_y = enemy_y + laser_height / 2

        enemy_obj = Enemy(enemy_img_path, enemy_width, enemy_height, enemy_x, enemy_y, enemy_dx, enemy_dy,
                          enemy_kill_sound_path)
        enemies.append(enemy_obj)

        laser_obj = Laser(laser_img_path, laser_width, laser_height, laser_x, laser_y, laser_dx, laser_dy,
                          shoot_probability, relaxation_time, laser_beam_sound_path)
        lasers.append(laser_obj)

def start_game(fused_queue, engagement_queue, smile_queue, blink_queue, stress_relax_queue):
    global WIDTH
    global HEIGHT

    global running
    global pause_state
    global score
    global highest_score
    global life
    global kills
    global difficulty
    global level
    global max_kills_to_difficulty_up
    global max_difficulty_to_level_up
    global initial_player_velocity
    global initial_enemy_velocity
    global weapon_shot_velocity
    global single_frame_rendering_time
    global total_time
    global frame_count
    global fps
    # global pad

    global player
    global bullet
    global enemies
    global lasers

    global LEFT_ARROW_KEY_PRESSED
    global RIGHT_ARROW_KEY_PRESSED
    global UP_ARROW_KEY_PRESSED
    global SPACE_BAR_PRESSED
    global ENTER_KEY_PRESSED
    global ESC_KEY_PRESSED

    # global window

    global pause_sound
    global level_up_sound
    global weapon_annihilation_sound
    global game_over_sound

    global background_img

    global pad
    global engagement
    global smile
    global blink
    global relax
    global red_alpha
    global blue_alpha
    # init game
    init_game()
    init_background_music()
    runned_once = False

    start_time = time.time()
    engagement_timer = start_time
    next_difficulty = difficulty

    speed_factor = float(2 ** (level/2 + difficulty - 1))
    # main game loop begins
    while running:


        current_time = time.time()


        if not fused_queue.empty():
            pad = fused_queue.get()
            # print(pad)
        if difficulty < 0:
            gameover_no_engagement()
        elapsed_time = current_time - engagement_timer
        if not engagement_queue.empty():
            engagement_timer = current_time
            engagement = engagement_queue.get()
            print("Engagement: ", engagement)
            if engagement >= 0.4:
                next_difficulty += engagement-0.2
            else:
                next_difficulty -= (0.4 - engagement)


        else:
            interpolation_ratio = elapsed_time / 10  # Linear interpolation ratio
            difficulty += (next_difficulty - difficulty) * interpolation_ratio


        if not smile_queue.empty():
            # print(smile_queue.get())
            if smile_queue.get() == "laugh" or smile_queue.get() == "smile" or smile_queue.get() == "clench":
                print(smile_queue.get())
                smile = True
            else:
                smile = False


        if not blink_queue.empty():

            if blink_queue.get() == "blink":
                print(blink_queue.get())
            if blink_queue.get() == "blink":
                blink = True
            else:
                blink = False




        if not stress_relax_queue.empty():
            relax = stress_relax_queue.get()
            print("Relax/Stress: ", relax)
            relax = relax*100
            # print(relax)
            # print(red_alpha, blue_alpha)


        else:
            interpolation_ratio = elapsed_time / 10
            # print(interpolation_ratio)
            if relax > 0:
                blue_alpha += (relax - blue_alpha) * interpolation_ratio * 0.05
                if red_alpha > 0:
                    red_alpha += (-relax - red_alpha) * interpolation_ratio* 0.05
            else:

                red_alpha += (-relax - red_alpha) * interpolation_ratio* 0.05
                if blue_alpha > 0:
                    blue_alpha += (relax - blue_alpha) * interpolation_ratio* 0.05
        if red_alpha > 100:
            red_alpha = 100
        if blue_alpha < 0:
            blue_alpha = 0
        if blue_alpha > 100:
            blue_alpha = 100
        if red_alpha < 0:
            red_alpha = 0




        overlay_color_red = pygame.Surface((WIDTH, HEIGHT))
        overlay_color_blue = pygame.Surface((WIDTH, HEIGHT))
        overlay_color_red.set_alpha(red_alpha)
        overlay_color_blue.set_alpha(blue_alpha)
        overlay_color_blue.fill((0, 0, 255))
        overlay_color_red.fill((255, 0, 0))


        if (difficulty >= max_difficulty_to_level_up) and (life != 0):
            level_up()
            engagement_timer = current_time
            next_difficulty = 1


        # start of frame timing
        start_time = time.time()

        # background



        window.fill((0, 0, 0))
        window.blit(background_img, (0, 0))
        window.blit(overlay_color_red, (0, 0))
        window.blit(overlay_color_blue, (0, 0))


        # Update the display
        # pygame.display.flip()

        # register events
        for event in pygame.event.get():
            # Quit Event
            if event.type == pygame.QUIT:
                running = False

            # Keypress Down Event
            if event.type == pygame.KEYDOWN:
                # Left Arrow Key down
                if event.key == pygame.K_LEFT:
                    print("LOG: Left Arrow Key Pressed Down")
                    LEFT_ARROW_KEY_PRESSED = 1
                # Right Arrow Key down
                if event.key == pygame.K_RIGHT:
                    print("LOG: Right Arrow Key Pressed Down")
                    RIGHT_ARROW_KEY_PRESSED = 1
                # Up Arrow Key down
                if event.key == pygame.K_UP:
                    print("LOG: Up Arrow Key Pressed Down")
                    UP_ARROW_KEY_PRESSED = 1
                # Space Bar down
                if event.key == pygame.K_SPACE:
                    print("LOG: Space Bar Pressed Down")
                    SPACE_BAR_PRESSED = 1
                # Enter Key down ("Carriage RETURN key" from old typewriter lingo)
                if event.key == pygame.K_RETURN:
                    print("LOG: Enter Key Pressed Down")
                    ENTER_KEY_PRESSED = 1
                    pause_state += 1
                # Esc Key down
                if event.key == pygame.K_ESCAPE:
                    print("LOG: Escape Key Pressed Down")
                    ESC_KEY_PRESSED = 1
                    pause_state += 1

            # Keypress Up Event
            if event.type == pygame.KEYUP:
                # Right Arrow Key up
                if event.key == pygame.K_RIGHT:
                    print("LOG: Right Arrow Key Released")
                    RIGHT_ARROW_KEY_PRESSED = 0
                # Left Arrow Key up
                if event.key == pygame.K_LEFT:
                    print("LOG: Left Arrow Key Released")
                    LEFT_ARROW_KEY_PRESSED = 0
                # Up Arrow Key up
                if event.key == pygame.K_UP:
                    print("LOG: Up Arrow Key Released")
                    UP_ARROW_KEY_PRESSED = 0
                # Space Bar up
                if event.key == pygame.K_SPACE:
                    print("LOG: Space Bar Released")
                    SPACE_BAR_PRESSED = 0
                # Enter Key up ("Carriage RETURN key" from old typewriter lingo)
                if event.key == pygame.K_RETURN:
                    print("LOG: Enter Key Released")
                    ENTER_KEY_PRESSED = 0
                # Esc Key up
                if event.key == pygame.K_ESCAPE:
                    print("LOG: Escape Key Released")
                    ESC_KEY_PRESSED = 0

        # check for pause game event
        if pause_state == 2:
            pause_state = 0
            runned_once = False
            mixer.music.unpause()
        if pause_state == 1:
            if not runned_once:
                runned_once = True
                pause_game()
            continue
        # manipulate game objects based on events and player actions
        # player spaceship movement
        if RIGHT_ARROW_KEY_PRESSED:
            player.x += player.dx * speed_factor
        if LEFT_ARROW_KEY_PRESSED:
            player.x -= player.dx * speed_factor
        if smile:
            player.x += player.dx * speed_factor
        else:
            player.x -= player.dx * speed_factor
        # bullet firing
        if (SPACE_BAR_PRESSED or UP_ARROW_KEY_PRESSED or blink) and not bullet.fired:
            bullet.fired = True
            bullet.fire_sound.play()
            bullet.x = player.x + player.width / 2 - bullet.width / 2
            bullet.y = player.y + bullet.height / 2
        # bullet movement
        if bullet.fired:
            bullet.y -= bullet.dy

        # iter through every enemies and lasers
        for i in range(len(enemies)):
            # laser beaming
            if not lasers[i].beamed:
                lasers[i].shoot_timer += 1
                if lasers[i].shoot_timer == lasers[i].relaxation_time:
                    lasers[i].shoot_timer = 0
                    random_chance = random.randint(0, 100)
                    if random_chance <= (lasers[i].shoot_probability * 100):
                        lasers[i].beamed = True
                        lasers[i].beam_sound.play()
                        lasers[i].x = enemies[i].x + enemies[i].width / 2 - lasers[i].width / 2
                        lasers[i].y = enemies[i].y + lasers[i].height / 2
            # enemy movement
            enemies[i].x += enemies[i].dx * speed_factor
            # laser movement
            if lasers[i].beamed:
                lasers[i].y += lasers[i].dy

        # collision check
        for i in range(len(enemies)):
            bullet_enemy_collision = collision_check(bullet, enemies[i])
            if bullet_enemy_collision:
                kill_enemy(player, bullet, enemies[i])

        for i in range(len(lasers)):
            laser_player_collision = collision_check(lasers[i], player)
            if laser_player_collision:
                kill_player(player, enemies[i], lasers[i])

        for i in range(len(enemies)):
            enemy_player_collision = collision_check(enemies[i], player)
            if enemy_player_collision:
                kill_enemy(player, bullet, enemies[i])
                kill_player(player, enemies[i], lasers[i])

        for i in range(len(lasers)):
            bullet_laser_collision = collision_check(bullet, lasers[i])
            if bullet_laser_collision:
                destroy_weapons(player, bullet, enemies[i], lasers[i])

        # boundary check: 0 <= x <= WIDTH, 0 <= y <= HEIGHT
        # player spaceship
        if player.x < 0:
            player.x = 0
        if player.x > WIDTH - player.width:
            player.x = WIDTH - player.width
        # enemy
        for enemy in enemies:
            if enemy.x <= 0:
                enemy.dx = abs(enemy.dx) * 1
                enemy.y += enemy.dy
            if enemy.x >= WIDTH - enemy.width:
                enemy.dx = abs(enemy.dx) * -1
                enemy.y += enemy.dy
        # bullet
        if bullet.y < 0:
            bullet.fired = False
            bullet.x = player.x + player.width / 2 - bullet.width / 2
            bullet.y = player.y + bullet.height / 2
        # laser
        for i in range(len(lasers)):
            if lasers[i].y > HEIGHT:
                lasers[i].beamed = False
                lasers[i].x = enemies[i].x + enemies[i].width / 2 - lasers[i].width / 2
                lasers[i].y = enemies[i].y + lasers[i].height / 2

        # create frame by placing objects on the surface
        scoreboard()
        for laser in lasers:
            laser.draw()
        for enemy in enemies:
            enemy.draw()
        bullet.draw()
        player.draw()

        # render the display
        pygame.display.update()

        # end of rendering, end on a frame
        frame_count += 1
        end_time = time.time()
        single_frame_rendering_time = end_time - start_time
        # fps = 1 / render_time

        total_time = total_time + single_frame_rendering_time
        if total_time >= 1.0:
            fps = frame_count
            frame_count = 0
            total_time = 0
        # print("rendering time:", single_frame_rendering_time)
        # print("FPS:", fps)


if __name__ =='__main__':
    # global window
    # window = pygame.display.set_mode((WIDTH, HEIGHT))

    # start_game()
    fused_queue = multiprocessing.Queue()
    engagement_queue = multiprocessing.Queue()
    smile_queue = multiprocessing.Queue()
    blink_queue = multiprocessing.Queue()
    stress_relax_queue = multiprocessing.Queue()

    sender = multiprocessing.Process(target=main, args=(fused_queue,engagement_queue, smile_queue, blink_queue, stress_relax_queue))
    sender.start()

    receiver = multiprocessing.Process(target=start_game, args=(fused_queue,engagement_queue, smile_queue, blink_queue, stress_relax_queue))
    time.sleep(1)
    receiver.start()

    receiver.join()
    if sender.is_alive():
        sender.terminate()
    sender.join()