import pygame
import sys
import random
from math import *

pygame.init()
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)

SCREEN_WIDTH = 432
SCREEN_HEIGHT = 768
GRAVITY = 0.2
DISTANCE = 350
TIME = 2500

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
CLOCK = pygame.time.Clock()

background = None
floor = None
bird = None
bird_rect = None
message = None
message_rect = None

pipe_surface = None
pipe_spawn = None
pipes = []
pipes_height = [250, 300, 350, 400, 450, 500, 550, 600]

birds = []
bird_flap = None
bird_index = 0

font = None
font_rect = None

score, highest_score = 999, 0

bird_movement = 0
floor_x_pos = 0
game_active = True

def set_game_icon(icon_path):
    icon = pygame.image.load(icon_path).convert()
    pygame.display.set_icon(icon)

def set_game_caption(caption):
    pygame.display.set_caption(caption)

def set_game_background(background_path):
    global background
    background = pygame.image.load(background_path).convert()
    background = pygame.transform.scale2x(background)
    
def set_game_floor(floor_path):
    global floor
    floor = pygame.image.load(floor_path).convert()
    floor = pygame.transform.scale2x(floor)

def set_game_bird():
    bird_up = pygame.transform.scale2x(pygame.image.load(r"assests/yellowbird-upflap.png"))
    bird_mid = pygame.transform.scale2x(pygame.image.load(r"assests/yellowbird-midflap.png"))
    bird_down = pygame.transform.scale2x(pygame.image.load(r"assests/yellowbird-downflap.png"))
    
    global bird, bird_rect, birds
    
    birds = [bird_up, bird_mid, bird_down]
    
    bird = birds[bird_index]
    bird_rect = bird.get_rect(center=(100, 100))

def set_bird_flap():
    global bird_flap
    bird_flap = pygame.USEREVENT + 1
    pygame.time.set_timer(bird_flap, 200)

def bird_animation():
    new_bird = birds[bird_index]
    new_bird_rect = new_bird.get_rect(center=(100, bird_rect.centery))
    return [new_bird, new_bird_rect]

def rotate_bird(bird):
    new_bird = pygame.transform.rotozoom(bird, -bird_movement * 2.5, 1)
    return new_bird

def set_game_message(message_path):
    global message, message_rect
    message = pygame.image.load(message_path).convert_alpha()
    message = pygame.transform.scale2x(message)
    message_rect = message.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

def set_game_pipe(pipe_path):
    global pipe_surface, pipe_spawn
    pipe_surface = pygame.image.load(pipe_path).convert()
    pipe_surface = pygame.transform.scale2x(pipe_surface)
    
    pipe_spawn = pygame.USEREVENT
    pygame.time.set_timer(pipe_spawn, TIME)    

def create_pipe():
    random_bottom_pipe_pos = random.choice(pipes_height)
    bottom_pipe_rect = pipe_surface.get_rect(midtop=(432, random_bottom_pipe_pos))
    
    random_top_pipe_pos = random.choice(pipes_height)
    
    if random_top_pipe_pos > random_bottom_pipe_pos - DISTANCE:
        random_top_pipe_pos = random_bottom_pipe_pos - DISTANCE
        
    top_pipe_rect = pipe_surface.get_rect(midbottom=(432, random_top_pipe_pos))
    
    return [bottom_pipe_rect, top_pipe_rect]

def game_move_pipe(pipes):
    for pipe_rect in pipes:
        pipe_rect.centerx -= 1
        if pipe_rect.centerx < 0:
            pipes.remove(pipe_rect)

def game_display_pipe(pipes):
    for pipe_rect in pipes:
        if pipe_rect.bottom >= 600:
            SCREEN.blit(pipe_surface, pipe_rect)
        else:
            flip_pipe = pygame.transform.flip(pipe_surface, False, True)
            SCREEN.blit(flip_pipe, pipe_rect)

def check_collision(bird_rect, pipes, *argv):
    top, bottom = argv
    if bird_rect.centery < top or bird_rect.centery > bottom:
        return False
    else:
        for pipe_rect in pipes:
            if bird_rect.colliderect(pipe_rect):
                return False
        return True

def set_game_font(font_path):
    global font
    font = pygame.font.Font(font_path, 40)

def score_display(str_score, width, height):
    score_surface = font.render(str_score, True, (255, 255, 255))
    score_rect = score_surface.get_rect(center=(width, height))
    SCREEN.blit(score_surface, score_rect)

if __name__ == "__main__":
    
    flap_sound = pygame.mixer.Sound(r"sound/sfx_wing.wav")
    hit_sound = pygame.mixer.Sound(r"sound/sfx_hit.wav")
    point_sound = pygame.mixer.Sound(r"sound/sfx_point.wav")

    hit_sound_play = True
    
    set_game_caption("Flappy Bird")
    set_game_icon(r"assests/yellowbird-midflap.png")
    set_game_background(r"assests/background-night.png")
    set_game_floor(r"assests/floor.png")
    set_game_bird()
    set_bird_flap()
    set_game_message(r"assests/message.png")
    set_game_pipe(r"assests/pipe-green.png")
    set_game_font(r"04B_19.TTF")
    
    file = open("score.txt", "r+")
    highest_score = int(file.read())
    
    while True:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_active == False:
                        bird_rect.centery = 100
                        bird_movement = 0
                        pipes.clear()
                        game_active = False
                        score = 0
                        hit_sound_play = True
                    else:
                        bird_movement = -8
                        flap_sound.play()
                        
            if game_active:            
                if event.type == pipe_spawn:
                    print(event.type)
                    pipes.extend(create_pipe())
                if event.type == bird_flap:
                    bird_index += 1
                    bird_index %= 3
                    
                    bird, bird_rect = bird_animation()
                             
        # background
        SCREEN.blit(background, (0, 0))
        
         # Game logic
        game_active = check_collision(bird_rect, pipes, 0, 600)

        if game_active == False:
            if hit_sound_play == True:
                hit_sound.play()
                hit_sound_play = False
                
            SCREEN.blit(message, message_rect)
            score_display("HIGHEST SCORE: " + str(highest_score), 216, 100)
            score_display("SCORE: " + str(score), 216, 50)
        else:
            # bird
            bird_movement += GRAVITY
            rotated_bird = rotate_bird(bird)
            bird_rect.centery += bird_movement
            SCREEN.blit(rotated_bird, bird_rect) 
            
            # pipes
            game_move_pipe(pipes)
            game_display_pipe(pipes)
            
            # score
            if len(pipes) > 0 and bird_rect.centerx == pipes[0].centerx:
                score += 1
                point_sound.play()
                if score > highest_score:
                    file.seek(0)
                    highest_score = score
                    file.write(str(highest_score))
            
            score_display(str(score), 50, 50)
            
        # floor
        SCREEN.blit(floor, (floor_x_pos, 600))
        SCREEN.blit(floor, (floor_x_pos + SCREEN_WIDTH, 600))
        floor_x_pos -= 1
        
        if floor_x_pos < -1 * SCREEN_WIDTH:
            floor_x_pos = 0
        
        # Update display and maintain frame rate
        CLOCK.tick(120)
        pygame.display.update()