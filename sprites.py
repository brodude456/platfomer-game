# Sprite classes for platform game
import pygame as pg
from settings import *
from random import choice, randrange, uniform
import settings
vec = pg.math.Vector2

class Spritesheet:
    # utility class for loading and parsing spritesheets
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height):
        # grab an image out of a larger spritesheet
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        image = pg.transform.scale(image, (width // 2, height // 2))
        return image

class Player(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.walking = False
        self.jumping = False
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = self.standing_frames[0]
        self.rect = self.image.get_rect()
        self.rect.center = (40, HEIGHT - 100)
        self.pos = vec(40, HEIGHT - 100)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.lives=3
        self.timebeetweenshohts=450
        self.lastshot=-self.timebeetweenshohts
        self.num_of_bullets=9
        self.bulletdir="up"
        self.plat=False
        self.jetpack=False
        self.shield=False
        #note:these lives only protect from mobs not falling to death forever alone
        #there are boost from whixh you can get more of health

    def load_images(self):
        self.standing_frames = [self.game.spritesheet.get_image(614, 1063, 120, 191),
                                self.game.spritesheet.get_image(690, 406, 120, 201)]
        for frame in self.standing_frames:
            frame.set_colorkey(BLACK)
        self.walk_frames_r = [self.game.spritesheet.get_image(678, 860, 120, 201),
                              self.game.spritesheet.get_image(692, 1458, 120, 207)]
        self.walk_frames_l = []
        for frame in self.walk_frames_r:
            frame.set_colorkey(BLACK)
            self.walk_frames_l.append(pg.transform.flip(frame, True, False))

    def jump_cut(self):
        if self.jumping:
            if self.vel.y < -9:
                self.vel.y = -9

    def jump(self):
        # jump only if standing on a platform
        self.rect.y += 2
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.y -= 2
        if hits and not self.jumping or self.jetpack:
            self.game.jump_sound.play()
            self.jumping = True
            self.vel.y = -PLAYER_JUMP
            if self.jetpack and hits and not self.jumping:
                self.vel.y=-(PLAYER_JUMP+10)


    def update(self):

        if not self.jetpack:
            self.animate()

        self.acc = vec(0, PLAYER_GRAV)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.acc.x = -PLAYER_ACC
            self.bulletdir="left"
        elif keys[pg.K_RIGHT]:
            self.acc.x = PLAYER_ACC
            self.bulletdir="right"
        elif keys[pg.K_a]:
            self.bulletdir="down"
        elif keys[pg.K_UP]:
            self.bulletdir="up"
        if keys[pg.K_d]:
            self.shoot()


        # apply friction
        self.acc.x += self.vel.x * PLAYER_FRICTION
        # equations of motion
        self.vel += self.acc
        if abs(self.vel.x) < 0.1:
            self.vel.x = 0
        self.pos += self.vel + 0.5 * self.acc
        # wrap around the sides of the screen
        if self.pos.x > WIDTH + self.rect.width / 2 :
            if self.plat:
                if self.plat.accx==0:
                    self.pos.x = 0 - self.rect.width / 2
            else:
                self.pos.x = 0 - self.rect.width / 2
        if self.pos.x < 0 - self.rect.width / 2:
             if self.plat:
                if self.plat.accx==0:
                    self.pos.x = WIDTH + self.rect.width / 2
             else:
                self.pos.x = WIDTH + self.rect.width / 2

        self.rect.midbottom = self.pos

        if self.shield:
            if pg.time.get_ticks()-self.shieldtimer>5000:
                self.shield-=1

                if self.shield==0:
                    self.shield=False

                self.shieldtimer=pg.time.get_ticks()
            else:
                self.standing_frames = [self.game.spritesheet.get_image(584,0,121,201),
                                self.game.spritesheet.get_image(581,1265,121,191)]
                for frame in self.standing_frames:
                    frame.set_colorkey(BLACK)
                self.walk_frames_r = [self.game.spritesheet.get_image(584,203,121,201),
                                      self.game.spritesheet.get_image(678,651,121,207)]
                self.walk_frames_l = []
                for frame in self.walk_frames_r:
                    frame.set_colorkey(BLACK)
                    self.walk_frames_l.append(pg.transform.flip(frame, True, False))
        else:

            self.load_images()

        if self.jetpack:

            if pg.time.get_ticks()-self.jetpacktimer>self.jetpackduration:
                self.jetpack-=1
                if self.jetpack==0:
                    self.jetpack=False
                    for mob in self.game.mobs:
                        mob.kill()
                self.jetpacktimer=pg.time.get_ticks()

            else:
                if self.vel.y<0 and self.shield==False:
                    self.image=self.game.spritesheet.get_image(382,635,174,126)

                elif self.shield==False:
                    self.image=self.game.spritesheet.get_image(0,1879,206,107)

                else:
                    self.image=self.game.spritesheet.get_image(416,1660,150,181)

                self.image.set_colorkey(BLACK)
                self.rect=self.image.get_rect()
                self.rect.midbottom=self.pos

    def animate(self):
        now = pg.time.get_ticks()
        if self.vel.x != 0:
            self.walking = True
        else:
            self.walking = False
        # show walk animation
        if self.walking:
            if now - self.last_update > 180:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.walk_frames_l)
                bottom = self.rect.bottom
                if self.vel.x > 0:
                    self.image = self.walk_frames_r[self.current_frame]
                else:
                    self.image = self.walk_frames_l[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        # show idle animation
        if not self.jumping and not self.walking:
            if now - self.last_update > 350:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames)
                bottom = self.rect.bottom
                self.image = self.standing_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        self.mask = pg.mask.from_surface(self.image)

    def shoot(self):
        now=pg.time.get_ticks()
        if now-self.lastshot>self.timebeetweenshohts:
            if self.bulletdir=="right":
                dir=1
                diry=0
            elif self.bulletdir=="left":
                dir=-1
                diry=0
            elif self.bulletdir=="up":
                dir=0
                diry=-1
            else:
                dir=0
                diry=1
            if self.num_of_bullets>0:
                Bullet(self.game,dir,diry)
                self.num_of_bullets-=1
            else:
                print("NO BULLETS BRUH")
            self.lastshot=now


class Cloud(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = choice([CLOUD_LAYER,CLOUD_LAYER,CLOUD_LAYER,CLOUD_LAYER2])
        self.groups = game.clouds,game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = choice(self.game.cloud_images)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        scale = randrange(50, 101) / 100
        if self._layer==CLOUD_LAYER2:
             scale = randrange(100,120) / 100
        self.image = pg.transform.scale(self.image, (int(self.rect.width * scale),
                                                     int(self.rect.height * scale)))
        self.rect.x = randrange(WIDTH - self.rect.width)
        self.rect.y = randrange(-500, -50)
        self.movementspeedlist=[max(abs(self.game.player.vel.y)//2-5,2),max(abs(self.game.player.vel.y)//2,2),max(abs(self.game.player.vel.y)//2+6,2),max(abs(self.game.player.vel.y)*1.5,2),max(abs(self.game.player.vel.y)*1.5+7,2)]
        self.index=randrange(3,len(self.movementspeedlist))
        if self._layer==CLOUD_LAYER:
            self.index=randrange(0,3)
        self.move=False
        if randrange(0,101)<50:
            self.move=True
        if self.move:
             self.vlx=randrange(13,15)
             if self._layer==CLOUD_LAYER2:
                self.vlx=randrange(15,18)
             self.vlxorig=self.vlx
             if randrange(0,2)==1:
                self.vlx*=-1
             self.acc_x=self.vlx/(abs(self.vlx)*-1)
             if self._layer==CLOUD_LAYER2:
                 self.image=self.game.spritesheet.get_image(0,1152,260,134)
                 self.image.set_colorkey(BLACK)
                 self.rect = self.image.get_rect()
                 scale = randrange(100,120) / 100
                 self.image = pg.transform.scale(self.image, (int(self.rect.width * scale),int(self.rect.height * scale)))
                 self.rect.x = randrange(WIDTH - self.rect.width)
                 self.rect.y = randrange(-500, -50)


    def update(self):
        if self.rect.top > HEIGHT * 2:
            self.kill()
        self.movementspeedlist=[abs(self.game.player.vel.y)//2-3,abs(self.game.player.vel.y)//2,abs(self.game.player.vel.y)//2+6,abs(self.game.player.vel.y)*1.5,abs(self.game.player.vel.y)*1.5+5]
        if self.move:
            self.rect.centerx+=self.vlx
            self.vlx+=self.acc_x
            if self.vlx==self.vlxorig or self.vlx==self.vlxorig*-1:
                self.acc_x*=-1


class Platform(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = PLATFORM_LAYER
        self.groups = game.all_sprites, game.platforms
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.frame=0
        self.posibil=randrange(100)
        self.powpos=settings.POW_SPAWN_PCT
        if self.posibil<25:
            self.powpos+=6
            self.frame=1


        self.explodeframes=choice([[self.game.spritesheet.get_image(213, 1662, 201, 100),
                            self.game.spritesheet.get_image(382,204,200,100),
                            self.game.spritesheet.get_image(382,0,200,100),
                            self.game.spritesheet.get_image(382,102,200,100),
                            self.game.spritesheet.get_image(382,306,200,100)],[self.game.spritesheet.get_image(0, 288, 380, 94),
                            self.game.spritesheet.get_image(0,384,380,94),
                            self.game.spritesheet.get_image(0,864,380,94),
                            self.game.spritesheet.get_image(0,1056,380,94),
                            self.game.spritesheet.get_image(0,480,380,94)],[self.game.spritesheet.get_image(382,408,200,100),
                            self.game.spritesheet.get_image(232,1288,200,100),
                            self.game.spritesheet.get_image(262,1152,200,100),
                            self.game.spritesheet.get_image(382,102,200,100),
                            self.game.spritesheet.get_image(382,306,200,100)],[self.game.spritesheet.get_image(0,672,380,94),
                            self.game.spritesheet.get_image(0,1056,380,94),
                            self.game.spritesheet.get_image(0,768,380,94),
                            self.game.spritesheet.get_image(0,480,380,94),
                            self.game.spritesheet.get_image(0,768,380,94)],[self.game.spritesheet.get_image(208,1879,201,100),
                            self.game.spritesheet.get_image(382,102,200,100),
                            self.game.spritesheet.get_image(213,1764,201,100),
                            self.game.spritesheet.get_image(382,306,200,100),
                            self.game.spritesheet.get_image(213,1764,201,100)],[self.game.spritesheet.get_image(218,1456,201,100),
                            self.game.spritesheet.get_image(262,1152,200,100),
                            self.game.spritesheet.get_image(382,306,200,100),
                            self.game.spritesheet.get_image(213,1764,201,100),
                            self.game.spritesheet.get_image(382,306,200,100)]])

        self.speedx=0
        self.accx=0
        if randrange(100)<18:
            self.accx=choice([-1,1])
        self.speedlimit=randrange(12,21)
        self.movmenttime=0
        self.stay=1
        self.time=100
        self.image=self.explodeframes[self.frame]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.image.set_colorkey(BLACK)
        self.animate()
        if randrange(100) < self.powpos:
            Pow(self.game, self)
        else:
            if randrange(100) < 3:
                movexby=randrange(-self.rect.width//2+2,self.rect.width//2-2)
                self.rect.centery-=(self.rect.height//2+10)
                self.rect.centerx+=movexby
                Jetpack(self.game,self.rect,self)
                self.rect.centery+=(self.rect.height//2+10)
                self.rect.centerx-=movexby



    def update(self):
        if pg.time.get_ticks()-self.movmenttime>20:
            self.rect.centerx+=self.speedx
            self.speedx+=self.accx
            if self==self.game.player.plat:
                self.game.player.pos.x+=self.speedx
            for jetpack in self.game.jetpacks:
                if self==jetpack.plat:
                    jetpack.rect.centerx+=self.speedx
            if self.speedx==self.speedlimit or self.speedx==-self.speedlimit:
                self.accx*=-1
            self.movmenttime=pg.time.get_ticks()
            if self.rect.centery<0-self.rect.width//2:
                self.rect.centerx=HEIGHT+self.rect.width//2
            elif self.rect.centerx>HEIGHT+self.rect.width//2:
                self.rect.centerx=0-self.rect.width//2
            if self.stay==2:
                if pg.time.get_ticks()-self.staytime>602:
                    self.kill()
                elif pg.time.get_ticks()-self.staytime>self.time:
                    self.frame+=1
                    self.time+=200
            self.animate()



    def animate(self):
        rect = self.rect.center
        self.image = self.explodeframes[self.frame]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = rect

class Pow(pg.sprite.Sprite):
    def __init__(self, game, plat):
        self._layer = POW_LAYER
        self.groups = game.all_sprites, game.powerups
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.plat = plat
        self.type = choice(['boost'])
        self.image = self.game.spritesheet.get_image(820, 1805, 71, 70)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top - 5
        self.boostpower=BOOST_POWER
        if randrange(100)<21:
            self.boostpower*=1.7
        self.boostpower//=1
        self.newltopl=0
        now=randrange(0,100)
        if now<25:
            self.newltopl=2
        elif now<50:
            self.newltopl=1

    def update(self):
        self.rect.bottom = self.plat.rect.top - 5
        self.rect.centerx=self.plat.rect.centerx
        if not self.game.platforms.has(self.plat):
            self.kill()

class Mob(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image_up = self.game.spritesheet.get_image(566, 510, 122, 139)
        self.image_up.set_colorkey(BLACK)
        self.image_down = self.game.spritesheet.get_image(568, 1534, 122, 135)
        self.image_down.set_colorkey(BLACK)
        self.image = self.image_up
        self.rect = self.image.get_rect()
        self.rect.centerx = choice([-100, WIDTH + 100])
        self.vx = randrange(1, 4)
        if self.rect.centerx > WIDTH:
            self.vx *= -1
        self.rect.y = randrange(HEIGHT / 2)
        self.vy = 0
        self.dy = choice([-0.5,0.5])
        self.ymovement=randrange(5,9)
        self.hitstaken=0
        self.hitsneededtobetaken=randrange(1,3)


    def update(self):
        self.rect.x += self.vx
        self.vy += self.dy
        if self.vy == self.ymovement or self.vy == -self.ymovement:
            self.dy *= -1
        center = self.rect.center
        if self.vy < 0:
            self.image = self.image_up
        else:
            self.image = self.image_down
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)
        self.rect.center = center
        self.rect.y += self.vy
        if self.rect.left > WIDTH + 100 or self.rect.right < -100:
            self.kill()

class Bullet(pg.sprite.Sprite):

    def __init__(self,game,dir,diry):
        self.groups=game.bullets,game.all_sprites
        pg.sprite.Sprite.__init__(self,self.groups)
        self.game=game
        self.imageorig= self.game.spritesheet.get_image(814,1661,78,70)
        self.imageorig=pg.transform.scale(self.imageorig,(50,50))
        self.image=self.imageorig
        self.rect= self.image.get_rect()
        self.image.set_colorkey(BLACK)
        self.rect.centerx=self.game.player.pos.x
        self.rect.centery=self.game.player.pos.y-self.game.player.rect.height//2
        self.vlx=8*dir
        self.rotateamount=0
        self.rotateincreaser=randrange(-10,11)
        self.lastrotated=0
        self.timebeetweenrotates=15
        self.vly=8*diry


    def update(self):
        self.rotate()
        self.rect.centerx+=self.vlx
        self.rect.centery+=self.vly

    def rotate(self):
        now=pg.time.get_ticks()
        if now-self.lastrotated>self.timebeetweenrotates:
            self.lastrotated=now
            self.rotateamount+=self.rotateincreaser
            self.rotateamount=self.rotateamount%360
            centerx=self.rect.centerx
            centery=self.rect.centery
            self.image=pg.transform.rotate(self.imageorig,self.rotateamount)
            self.image.set_colorkey(BLACK)
            self.rect=self.image.get_rect()
            self.rect.centerx=centerx
            self.rect.centery=centery
            print()

class Jetpack(pg.sprite.Sprite):
    def __init__(self,game,rect,plat):
        self.game=game
        self.groups=self.game.jetpacks,self.game.all_sprites
        pg.sprite.Sprite.__init__(self,self.groups)
        self.image=self.game.spritesheet.get_image(563,1843,133,160)
        self.image=pg.transform.scale(self.image,(25,50))
        self.vel=vec(0,0)
        self.acc=vec(0,0.5)
        self.rect=self.image.get_rect()
        self.image.set_colorkey(BLACK)
        self.rect.centerx=rect.centerx
        self.rect.centery=rect.centery
        self.plat=plat

    def update(self):
        if self.plat:
            self.acc.y=0
            self.vel.y=0
            self.rect.centery=self.plat.rect.centery-50
            if not self.plat.alive():
                self.kill()
        self.vel.x+=self.acc.x
        self.vel.y+=self.acc.y
        self.rect.centerx+=self.vel.x
        self.rect.centery+=self.vel.y
        if self.rect.centery>HEIGHT+self.rect.width:
            self.kill()

class Meteor(pg.sprite.Sprite):
    def __init__(self,game):
        self.game=game
        self.groups=self.game.meteors,self.game.all_sprites
        pg.sprite.Sprite.__init__(self,self.groups)
        self.imageOrig=self.game.spritesheet.get_image(421,1390,148,142)
        self.size=110
        self.image=pg.transform.scale(self.imageOrig,(self.size,self.size))
        self.image.set_colorkey(BLACK)
        self.vel=vec(0,0)
        self.acc=vec(choice([-0.1,0.1,-0.2,0.2]),0.5)
        self.rect=self.image.get_rect()
        self.rect.centerx=randrange(0,WIDTH-self.rect.width+1)
        self.rect.centery=randrange(-200,-(self.rect.height-1))
        self.timebeetweenupdates=15
        self.lastupdated=pg.time.get_ticks()-self.timebeetweenupdates
        self.type=choice(["killbe","notkillible"])
        if type=="killble":
            self.hitsaken=0
            self.hitsneededtobetaken=randrange(1,3)
        self.type2=choice(["canriPshield","cannotriPshield"])
        self.burnincreaser=randrange(2,5)
        self.smokesize=3
        self.smokesizeincreaser=7
        self.speedLimit=randrange(15,19)
        self.timebeetweensmokes=37
        self.smokeleavetimer=-self.timebeetweensmokes+3
        self.burnout=1600
        self.burntimer=pg.time.get_ticks()
        if self.rect.centerx<WIDTH//4+self.rect.width//2 or self.rect.centery>WIDTH//1.5-self.rect.width//2:
            self.acc.x=0


    def update(self):

        self.vel.x+=self.acc.x
        self.vel.y+=self.acc.y

        if self.vel.y>=self.speedLimit:
            self.vel.y=self.speedLimit

        self.rect.centery+=self.vel.y

        if self.vel.x>5:
            self.vel.x=5

        elif self.vel.x<-5:
            self.vel.x=-5

        self.rect.centerx+=self.vel.x

        if self.rect.centery>=HEIGHT+self.rect.height//2 or self.rect.centerx>=WIDTH+self.rect.height//2 or\
        self.rect.centerx<=-(self.rect.centerx//2) or self.rect.centery<-250:
            self.kill()

        if pg.time.get_ticks()-self.lastupdated>self.timebeetweenupdates:

            self.lastupdated=pg.time.get_ticks()

            if self.rect.centery>self.rect.height//2:
                self.burn()

        if pg.time.get_ticks()-self.smokeleavetimer>self.timebeetweensmokes:

            self.smokeleavetimer=pg.time.get_ticks()
            self.leave_smoke()

        if pg.time.get_ticks()-self.burntimer>self.burnout:
            self.kill()
            self.burnout=pg.time.get_ticks()
            if not self.game.player.jetpack and self.game.player.shield:
                bruh=20
            elif self.game.player.shield:
                bruh=10
            elif not self.game.player.jetpack:
                bruh=15
            else:
                bruh=5
            if randrange(0,100)<bruh:
                Meteor(self.game)

        print(self.vel.y)

    def burn(self):
        oldcenter=self.rect.center

        self.size-=self.burnincreaser
        if self.size<=65:
            self.size=65

        self.image=pg.transform.scale(self.imageOrig,(self.size,self.size))
        self.rect=self.image.get_rect()
        self.rect.width=self.size
        self.rect.height=self.size
        self.image.set_colorkey(BLACK)
        self.rect.center=oldcenter

    def leave_smoke(self):
        self.smokesize+=self.smokesizeincreaser
        Smoke(self.game,self.rect,self.smokesize)

    def go(self):
        self.vel.y=0
        self.acc.y*=-1

class Smoke(pg.sprite.Sprite):
    def __init__(self,game,rect,size):
        self.game=game
        self.groups=self.game.smokes,self.game.all_sprites
        pg.sprite.Sprite.__init__(self,self.groups)
        self.image=self.game.spritesheet.get_image(879,1364,51,48)
        self.size=size
        self.maxbig=110
        if self.size>self.maxbig:
            self.size=self.maxbig
        self.image=pg.transform.scale(self.image,(self.size,self.size))
        self.rect=self.image.get_rect()
        self.rect.centerx=rect.centerx
        self.rect.centery=rect.centery
        self.timebeetweenupdates=choice([90,100,110])
        self.lastupdated=pg.time.get_ticks()-self.timebeetweenupdates
        self.sizedeacreaser=randrange(5,10)
        self.image.set_colorkey(BLACK)
        self.disapear=False

    def update(self):
        if pg.time.get_ticks()-self.lastupdated>self.timebeetweenupdates:
            self.size-=self.sizedeacreaser

            if self.disapear:
                self.kill()

            if self.size<=0:
                self.size=1
                self.disapear=True

            rect=self.rect
            self.image=pg.transform.scale(self.image,(self.size,self.size))
            self.image.set_colorkey(BLACK)
            self.rect=self.image.get_rect()
            self.rect.centerx=rect.centerx
            self.rect.centery=rect.centery
            self.lastupdated=pg.time.get_ticks()










