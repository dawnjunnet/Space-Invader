import pygame
import os
import random
import time
from pygame import mixer
pygame.init()
pygame.font.init()
WIDTH, HEIGHT = 750,750
WIN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption('Space invaders')

red_space_ship = pygame.image.load('alien.png')
green_space_ship = pygame.image.load(os.path.join('assets','pixel_ship_green_small.png'))
blue_space_ship = pygame.image.load(os.path.join('assets','pixel_ship_blue_small.png'))

red_laser =  pygame.image.load(os.path.join('assets','pixel_laser_red.png'))
green_laser =  pygame.image.load(os.path.join('assets','pixel_laser_green.png'))
blue_laser =  pygame.image.load(os.path.join('assets','pixel_laser_blue.png'))
yellow_laser =  pygame.image.load('bullet.png')

YELLOW_SPACE_SHIP = pygame.image.load('player.png')

bg = pygame.transform.scale(pygame.image.load('space.png'), (WIDTH,HEIGHT))

bullet_sound = mixer.Sound('laser.wav')
life = mixer.Sound('lost.wav')
mixer.music.load('retro.wav')
mixer.music.play(-1)
hit_sound = mixer.Sound('hit.wav')
lost_game = mixer.Sound('lost game.wav')
lost_life = mixer.Sound('respawn.wav')

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

class Ship:
    COOLDOWN = 30
    def __init__(self,x,y,health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self,win):
        win.blit(self.ship_img,(self.x,self.y))
        for laser in self.lasers:
            laser.draw(win)

    def move_lasers(self,vel,obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                life.play()
                obj.health -= 10
                self.lasers.remove(laser)
                return True

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x + 15,self.y,self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

class Player(Ship):
    def __init__(self,x,y,health=100):
        super().__init__(x,y,health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = yellow_laser
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        self.respawn = False
        self.first = True
        self.level_up = False

    def move_lasers(self, vel, objs):
        self.cooldown()
        vel = vel * -1
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT): #if laser is off the screen remove it
                self.lasers.remove(laser)
            else: #if the laser is not off the screen check if it has hit an enemy
                for obj in objs:
                    if laser.collision(obj):
                        hit_sound.play()
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self,win):
        super().draw(win)
        self.healthbar(win)

    def healthbar(self,win):
        pygame.draw.rect(win,(255,0,0),(self.x,self.y+self.ship_img.get_height() + 10,self.ship_img.get_width(),10))
        pygame.draw.rect(win,(0,255,0),(self.x,self.y+self.ship_img.get_height() + 10,self.ship_img.get_width() * (self.health/self.max_health),10))

class Enemy(Ship):
    COLOUR_MAP = {'red': (red_space_ship,red_laser),
                  'green': (green_space_ship,green_laser),
                  'blue': (blue_space_ship,blue_laser)
                }
    def __init__(self,x,y,colour,health=100):
        super().__init__(x,y,health)
        self.ship_img, self.laser_img = self.COLOUR_MAP[colour]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self,vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x - 17,self.y,self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

def collide(obj1,obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask,(offset_x, offset_y)) != None

def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont('comicsans',50)
    lost_font = pygame.font.SysFont('comicsanc', 60)

    enemies = []
    wave_length = 5
    enemy_vel = 1

    laser_vel = 5
    player_vel = 5

    player = Player(300,630)

    clock = pygame.time.Clock()
    lost = False
    lost_count = 0


    player.first = True

    def redraw_window():
        WIN.blit(bg,(0,0))
        level_label = main_font.render(f'Level: {level}',1,(255,255,255))
        lives_label = main_font.render(f'Lives: {lives}',1,(255,255,255))
        WIN.blit(lives_label,(10,10))
        WIN.blit(level_label,(WIDTH - level_label.get_width()-10,10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render('You Lost!!', 1, (255,255,255))
            WIN.blit(lost_label,(WIDTH/2 - lost_label.get_width()/2,350))

        if player.level_up:
            level_label = main_font.render('LEVEL: ' + str(level),1,(255,255,255))
            WIN.blit(level_label,(WIDTH/2-level_label.get_width()/2,350))
            current = time.time()*1000.0

            if current - ms > 3000:
                player.level_up = False

        pygame.display.update()

    while run:
        redraw_window()
        clock.tick(FPS)

        if player.health <= 0 and lives > 0:
            player.respawn = True
            player.first = False
            player.health = player.max_health
            lost_life.play()
            lives -= 1

        if lives <= 0:
            lost_game.play()
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            if level < 7:
                wave_length += 5

            else:
                wave_length +=3
            player.level_up = True
            ms = time.time()*1000.0
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100),random.randrange(-1500,-100), random.choice(['red','blue','green']))
                enemies.append(enemy)

        if player.level_up:
            if player.health <= 0.5*player.max_health:
                player.health += 0.5*player.max_health

            if level%2==0:
                lives += 1
                player.level_up = False

            else:
                player.health = player.max_health

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and player.x - player_vel > 0:
            player.x -= player_vel

        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH:
            player.x += player_vel

        if keys[pygame.K_UP] and player.y - player_vel > 0:
            player.y -= player_vel

        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 25 < HEIGHT :
            player.y += player_vel

        if keys[pygame.K_SPACE]:
            player.shoot()
            bullet_sound.play()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel,player)

            if random.randrange(0,2*FPS) == 1:
                enemy.shoot()

            if collide(enemy,player): #Did enemy collided with player
                life.play()
                player.health -= 10
                enemies.remove(enemy)

            elif enemy.y + enemy.get_height() > HEIGHT: #did enemy pass the barrier
                life.play()
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(laser_vel,enemies)

def main_menu():
    title_font = pygame.font.SysFont('comicsans',50)
    run = True
    while run:
        WIN.blit(bg,(0,0))
        title_label = title_font.render('PRESS ENETER TO START',1,(255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2,300))
        bday_label = title_font.render('HAPPY BDAY AA!!',1,(255,255,255))
        WIN.blit(bday_label, (WIDTH/2 - bday_label.get_width()/2,400))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    main()

    quit()

main_menu()


