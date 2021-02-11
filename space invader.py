import pygame
import random
import math
from pygame import mixer
import time
#initialise the pygame
pygame.init()

#create the screen
screen = pygame.display.set_mode((800,600))

# Add background image
background = pygame.image.load('space.png')

# Background sound
mixer.music.load('xfilestheme.wav')
mixer.music.play(-1)

# Title and Icon
pygame.display.set_caption('Space Invaeders')
icon = pygame.image.load('ufo.png')
pygame.display.set_icon(icon)

# Player
playerImg = pygame.image.load('player.png')
playerX = 370
playerY = 480

playerX_change = 0

# enemy
enemyImg = []
enemyX = []
enemyY = []
enemyX_change = []
enemyY_change = []
num_of_enemies = 6
for i in range(num_of_enemies):
    enemyImg.append(pygame.image.load('alien.png'))
    enemyX.append(random.randint(0,736))
    enemyY.append(random.randint(50,150))
    enemyX_change.append(3)
    enemyY_change.append(40)

# Bullet
# Ready - cant see bullet in the screen
# Fire - The bullet is currently moving
bulletImg = pygame.image.load('bullet.png')
bulletX = 0
bulletY = 480
bulletX_change = 0
bulletY_change = 10
bullet_state = 'ready'

# Score
score_value = 0
font = pygame.font.Font('freesansbold.ttf',32)
textX = 10
textY = 10

# Game over text
over_font = pygame.font.Font('freesansbold.ttf',64)

# Bday text
bday_font = pygame.font.Font('freesansbold.ttf', 24)

def won():
    won_text = over_font.render('YOU WON!!', True, (0,255,0))
    screen.blit(won_text,(200,200))

def bday():
    bday_text = over_font.render('HAPPY BIRTHDAY',True, (186,85,211))
    screen.blit(bday_text,(100,250))

def name():
    name_text = over_font.render('AAREEN', True, (186,85,211))
    screen.blit(name_text,(250,300))

def show_score(x,y):
    score = font.render('Score: ' + str(score_value), True, (255,255,255))
    screen.blit(score,(x,y))

def game_over_text():
    over_text = over_font.render('GAME OVER', True, (255,0,0))
    screen.blit(over_text,(200,200))

def player(x,y):
    screen.blit(playerImg,(x,y))

def enemy(x,y, i):
    screen.blit(enemyImg[i],(x,y))

def fire_bullet(x,y):
    global bullet_state
    bullet_state = 'fire'
    screen.blit(bulletImg,(x + 16,y + 10))

def fire_bullet2(x,y):
    global bullet2_state
    bullet2_state = 'fire'

def isCollision(enemyX,enemyY,bulletX,bulletY):
    distance = math.sqrt(math.pow(enemyX-bulletX,2) + math.pow(enemyY-bulletY,2))
    if distance < 27:
        return True
    else:
        return False

# Game loop
running = True
while running:
    # RGB colours go 0 - 255. Arguments are all RGB https://www.rapidtables.com/web/color/RGB_Color.html
    screen.fill((0,0,0))

    # Background image
    screen.blit(background,(0,0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                playerX_change = - 5

            if event.key == pygame.K_RIGHT:
                playerX_change = 5

            if event.key == pygame.K_SPACE:
                if bullet_state is 'ready':
                    bullet_sound = mixer.Sound('laser.wav')
                    bullet_sound.play()
                    bulletX = playerX
                    fire_bullet(bulletX,bulletY)

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                playerX_change = 0

    # Checking for boundaries of spaceship so it does not go out of bounds
    playerX += playerX_change
    if playerX <= 0:
        playerX = 0
    elif playerX >= 736:
        playerX = 736
        # Enemy movement
    for i in range(num_of_enemies):

        # Game over
        if enemyY[i] > 300:
            for j in range(num_of_enemies):
                enemyY[j] = 2000

            game_over_text()
            bday()
            name()
            break

        elif score_value is 1:
            for j in range(num_of_enemies):
                enemyX[j] += 50
                if enemyX[j] == 0:
                    enemyY += 5
            won()
            bday()
            name()
        enemyX[i] += enemyX_change[i]
        if enemyX[i] <= 0:
            enemyX_change[i] = 3
            enemyY[i] += enemyY_change[i]
        elif enemyX[i] >= 736:
            enemyX_change[i] = -3
            enemyY[i] += enemyY_change[i]
        # Collision
        collision = isCollision(enemyX[i],enemyY[i],bulletX,bulletY)
        if collision:
            explosion_sound = mixer.Sound('Torpedo+Explosion.wav')
            explosion_sound.play()
            bulletY = 480
            bullet_state = 'ready'
            score_value += 1
            enemyX[i] = random.randint(0,736)
            enemyY[i] = random.randint(50,150)

        enemy(enemyX[i],enemyY[i], i)

    # Bullet movement
    if bulletY <= 0:
        bulletY = 480
        bullet_state = 'ready'

    if bullet_state is 'fire':
        fire_bullet(bulletX,bulletY)
        bulletY -= bulletY_change


    player(playerX,playerY)
    show_score(textX,textY)
    pygame.display.update()