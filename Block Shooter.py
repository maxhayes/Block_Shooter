import pygame
import pygame.mixer
import random
from pygame.locals import *
pygame.init()

# --- Constants ---
# color:
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

# screen:
SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 700
SCREEN_SIZE = ([SCREEN_WIDTH, SCREEN_HEIGHT])
screen = pygame.display.set_mode(SCREEN_SIZE)

# pos/speed/quantity:
PLAYER_SPEED = 5
BULLET_SPEED = 15
BLOCK_SPEED = 2

BLOCK_AMOUNT = 25
MAX_BOS = 3

# --- init Variables ---
clock = pygame.time.Clock()
pygame.mouse.set_visible(False)
# p1:
p1_speedx = 0
p1_speedy = 0
p1_keyspressed = 0
p1_can_fire = True
p1_direct = 'left'
p1_control_bullet = True

# p2:
p2_speedx = 0
p2_speedy = 0
p2_keyspressed = 0
p2_can_fire = True
p2_direct = 'right'
p2_control_bullet = True

# both:
change_x = 0
change_y = 0
is_dead = False


# ---  Create Lists  ---
# (for collision detection)
p1_list = pygame.sprite.Group()
p2_list = pygame.sprite.Group()
all_sprites_list = pygame.sprite.Group()
all_bullets_list = pygame.sprite.Group()
p1_bullet_list = pygame.sprite.Group()
p2_bullet_list = pygame.sprite.Group()
wall_list = pygame.sprite.Group()
block_list = pygame.sprite.Group() #(not active)
player_list = pygame.sprite.Group()#(not active)
# Add more lists as new classes for objects
# are added
# _____________________________________________________________________________
# --------------------------- CLASSES FOR GAME OBJECTS ------------------------
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Player class
class Player(pygame.sprite.Sprite):
    
    def __init__(self, color, x, y, player_list):
        self.player_list = player_list
        self.change_x = 0
        self.change_y = 0

        pygame.sprite.Sprite.__init__(self)
        
        # Create image
        self.image = pygame.Surface([15, 15])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # add to list
        all_sprites_list.add(self)
        self.player_list.add(self)
    
    def changespeed(self, x, y):
        self.change_x += x
        self.change_y += y
            
    
    def move(self, wall_list = wall_list):
        
        # move left/right:
        self.rect.x += self.change_x
        # hit wall check
        player_hit_wall = pygame.sprite.spritecollide(self, wall_list, False)
        for wall in player_hit_wall:
            if self.change_x > 0:
                self.rect.right = wall.rect.left
            if self.change_x < 0:
                self.rect.left = wall.rect.right

        # move up/down
        self.rect.y += self.change_y
        # hit wall check
        player_hit_wall = pygame.sprite.spritecollide(self, wall_list, False)
        for wall in player_hit_wall:
            if self.change_y > 0:
                self.rect.bottom = wall.rect.top
            if self.change_y < 0:
                self.rect.top = wall.rect.bottom

        # keep player on the screen
        if self.rect.x >= SCREEN_WIDTH - 15:
            self.rect.x = SCREEN_WIDTH - 15
        if self.rect.x <= 0:
            self.rect.x = 0
        if self.rect.y >= SCREEN_HEIGHT - 15:
            self.rect.y = SCREEN_HEIGHT - 15
        if self.rect.y <= 0:
            self.rect.y = 0
          

# Bullet class
class Bullet(pygame.sprite.Sprite):
    # create the bullet
    # x and y are the pos of the player firing the bullet
    def __init__(self, x ,y, firing_players_list, direction = 'right'):
        pygame.sprite.Sprite.__init__(self)
        self.firing_players_list = firing_players_list

        self.direction = direction
    
        self.image = pygame.Surface([3,3])
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()

        # put the bullet where the player is:
        self.rect.x = (x + 7.5) 
        self.rect.y = (y + 7.5)

        all_sprites_list.add(self)
        all_bullets_list.add(self)
        self.firing_players_list.add(self)
        
    def move(self, direction = 'right', move_with_player = False):

        if not move_with_player:
            direction = self.direction

        if direction == 'right':
            self.rect.x += BULLET_SPEED
        elif direction == 'left':
            self.rect.x -= BULLET_SPEED
        elif direction == 'up':
            self.rect.y -= BULLET_SPEED
        elif direction == 'down':
            self.rect.y += BULLET_SPEED

        if move_with_player:
            self.direction = direction

        # remove bullets that fly off the screen
        remove = False
        if self.rect.x >= SCREEN_WIDTH + 5:
            remove = True
        elif self.rect.x <= -5:
            remove = True
        elif self.rect.y >= SCREEN_HEIGHT + 5:
            remove = True
        elif self.rect.y <= -5:
            remove = True

        if remove == True:
            self.remove()

    def remove(self):
        all_sprites_list.remove(self)
        all_bullets_list.remove(self)
        self.firing_players_list.remove(self)
        print('bullet removed')

     
class Wall(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, color = BLUE, width = 20, length = SCREEN_HEIGHT / 2, orientation = 'v', moving = False):
        pygame.sprite.Sprite.__init__(self)
        
        # internalize variables
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.orientation = orientation
        self.moving = moving
        
        # decide if wall is horizontal or veritcal
        if orientation == 'v':
            self.width = width
            self.length = length
        elif orientation == 'h':
            self.width = length
            self.length = width
            
        # Draw the surface
        self.image = pygame.Surface([self.width, self.length])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        
        # position the surfcace
        self.rect.x = self.pos_x
        self.rect.y = self.pos_y
        
        # add the surface to lists
        all_sprites_list.add(self)
        wall_list.add(self)
        
    def move(self):
        if self.moving:
            if self.orientation == 'v':
                self.rect.x += 1
            elif self.orientation == 'h':
                self.rect.y += 1

# Block class

# Sheild class (moving = true/false)

# Mines (... one day)
# _____________________________________________________________________________
# ---------------------------- CREATE GAME OBJECTS ----------------------------
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# create players
player_1 = Player(RED, SCREEN_WIDTH - 50, SCREEN_HEIGHT - 50, p1_list)
player_2 = Player(GREEN, 50, 50, p2_list)

# design level (WALLS, BLOCKS)
# create walls:
wall_1 = Wall(SCREEN_WIDTH / 2 + 150, 0)
wall_2 = Wall(SCREEN_WIDTH / 2 - 150, SCREEN_HEIGHT - wall_1.length)

# _____________________________________________________________________________
# ------------------------------ MAIN GAME LOOP -------------------------------
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
done = False

while not done:
    
    # --- PROCESS EVENTS ---
    # ______________________
    for event in pygame.event.get():
        # Handle closing the window    
        if event.type == pygame.QUIT:
            done = True
        # Process 'player pushing key':
        elif event.type == pygame.KEYDOWN:
            # player 1 (moving):
            if event.key == pygame.K_LEFT:
                player_1.changespeed((-1*PLAYER_SPEED), 0)
                p1_direct = 'left'
                p1_keyspressed += 1
            elif event.key == pygame.K_RIGHT:
                player_1.changespeed(PLAYER_SPEED, 0)
                p1_direct = 'right'
                p1_keyspressed += 1
            elif event.key == pygame.K_UP:
                player_1.changespeed(0, (-1*PLAYER_SPEED))
                p1_direct = 'up'
                p1_keyspressed += 1
            elif event.key == pygame.K_DOWN:
                player_1.changespeed(0, PLAYER_SPEED)
                p1_direct = 'down'
                p1_keyspressed += 1
            # bullet control:
            elif event.key == pygame.K_LSHIFT:
                p1_control_bullet = True
            # fire button:
            elif event.key == pygame.K_SPACE:
                if p1_can_fire:
                    bullet = Bullet(player_1.rect.x, player_1.rect.y, p1_bullet_list, direction = p1_direct)

            # player 2 (moving):
            if event.key == pygame.K_a:
                player_2.changespeed((-1*PLAYER_SPEED), 0)
                p2_direct = 'left'
                p2_keyspressed += 1
            elif event.key == pygame.K_d:
                player_2.changespeed(PLAYER_SPEED, 0)
                p2_direct = 'right'
                p2_keyspressed += 1
            elif event.key == pygame.K_w:
                player_2.changespeed(0, (-1*PLAYER_SPEED))
                p2_direct = 'up'
                p2_keyspressed += 1
            elif event.key == pygame.K_s:
                player_2.changespeed(0, PLAYER_SPEED)
                p2_direct = 'down'
                p2_keyspressed += 1
            # bullet control
            elif event.key == pygame.K_j:
                p2_control_bullet = True
            # player 2 fire button:
            elif event.key == pygame.K_h:
                if p2_can_fire:
                    bullet = Bullet(player_2.rect.x, player_2.rect.y, p2_bullet_list, direction = p2_direct)
        # ========================================================

        # Procces 'player lifting key':
        # player 1:
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                player_1.changespeed(PLAYER_SPEED, 0)
                p1_keyspressed -= 1
            elif event.key == pygame.K_RIGHT:
                player_1.changespeed((-1*PLAYER_SPEED), 0)
                p1_keyspressed -= 1
            elif event.key == pygame.K_UP:
                player_1.changespeed(0, PLAYER_SPEED)
                p1_keyspressed -= 1
            elif event.key == pygame.K_DOWN:
                player_1.changespeed(0, (-1*PLAYER_SPEED))
                p1_keyspressed -= 1
            # turn off bullet control
           # elif event.key == pygame.K_LSHIFT:
               # p1_control_bullet = False
            
        # player 2:
            if event.key == pygame.K_a:
                player_2.changespeed(PLAYER_SPEED, 0)
                p2_keyspressed -= 1
            elif event.key == pygame.K_d:
                player_2.changespeed((-1*PLAYER_SPEED), 0)
                p2_keyspressed -= 1
            elif event.key == pygame.K_w:
                player_2.changespeed(0, PLAYER_SPEED)
                p2_keyspressed -= 1
            elif event.key == pygame.K_s:
                player_2.changespeed(0, (-1*PLAYER_SPEED))
                p2_keyspressed -= 1
            # turn off bullet control
           # elif event.key == pygame.K_j:
              #  p2_control_bullet = False

    # --- MOVE OBJECTS ---
    # ______________________
    # move players and their bullets

    player_1.move()
    for bullet in p1_bullet_list:
        bullet.move(p1_direct, move_with_player = p1_control_bullet)
    player_2.move()
    for bullet in p2_bullet_list:
        bullet.move(p2_direct, move_with_player = p2_control_bullet)

    # --- GAME LOGIC ---
    # __________________

    # limit amount of bullets on screen
    # player 1:
    p1_can_fire = True
    if len(p1_bullet_list) >= MAX_BOS:
        p1_can_fire = False

    # player 2:
    p2_can_fire = True
    if len(p2_bullet_list) >= MAX_BOS:
        p2_can_fire = False

    # --- COLLISIONS ---
    # __________________


    # PLAYER AND BULLET
    # p1:
    for bullet in p2_bullet_list:
        # see if player got hit with enemy bullet, delete player if so.
        p1_shot_list = pygame.sprite.spritecollide(bullet, p1_list, True)
        # if the player got shot...
        if p1_shot_list:
            # create a new player at the starting spot
            player_1 = Player(RED, SCREEN_WIDTH - 50, SCREEN_HEIGHT - 50, p1_list)
            # remove the bullet
            bullet.remove()            
    #p2:
    for bullet in p1_bullet_list:
        p2_shot_list = pygame.sprite.spritecollide(bullet, p2_list, True)
        if p2_shot_list:
            player_2 = Player(GREEN, 50, 50, p2_list)
            bullet.remove()

    # WALL AND BULLET:
    for wall in wall_list:
        bullet_hit_wall = pygame.sprite.spritecollide(wall, all_bullets_list, True)
        for bullet in bullet_hit_wall:
            bullet.remove()


     # if player has lifted all movement keys, stop movement
        # (This corrects for movement glitch upon respawn
        #   when player was killed while moving)
    if p1_keyspressed <= 0:
        player_1.change_x = 0
        player_1.change_y = 0
        p1_keyspressed = 0
    if p2_keyspressed <= 0:
        player_2.change_x = 0
        player_2.change_y = 0
        p2_keyspressed = 0

    
    # --- DRAW SCREEN ---
    # ___________________
    all_sprites_list.update()
    screen.fill(BLACK)
    all_sprites_list.draw(screen)
    clock.tick(60)
    pygame.display.flip()
    
pygame.quit()













