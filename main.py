# Art from Kenney.nl
# Happy Tune by http://opengameart.org/users/syncopika
# Yippee by http://opengameart.org/users/snabisch


import pygame as pg
import random
from settings import *
import settings
from sprites import *
from os import path


class Game:
    def __init__(self):
        # initialize game window, etc
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.font_name = pg.font.match_font(FONT_NAME)
        self.load_data()

    def load_data(self):
        # load high score
        self.dir = path.dirname(__file__)
        with open(path.join(self.dir, HS_FILE), 'r') as f:
            try:
                self.highscore = int(f.read())
            except:
                self.highscore = 0
        # load spritesheet image
        img_dir = path.join(self.dir, 'img')
        self.spritesheet = Spritesheet(path.join(img_dir, SPRITESHEET))
        # cloud images
        self.cloud_images = []
        for i in range(1, 4):
            self.cloud_images.append(pg.image.load(path.join(img_dir, 'cloud{}.png'.format(i))).convert())
        # load sounds
        self.snd_dir = path.join(self.dir, 'snd')
        self.jump_sound = pg.mixer.Sound(path.join(self.snd_dir, 'Jumpsnd.wav'))
        self.boost_sound = pg.mixer.Sound(path.join(self.snd_dir, 'Powerup31.wav'))

    def new(self):
        # start a new game
        self.score = 0
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.platforms = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.clouds = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.jetpacks=pg.sprite.Group()
        self.smokes=pg.sprite.Group()
        self.meteors=pg.sprite.Group()
        self.player = Player(self)
        for plat in PLATFORM_LIST:
            platt=Platform(self, *plat)
            if PLATFORM_LIST.index(plat)==0:
                platt.posibil=26
                platt.frame=0
                platt.accx=0

        self.mob_timer = 0
        self.meteortimer=0
        self.randomer=random.choice([-1000, -500, 0, 500, 1000])
        pg.mixer.music.load(path.join(self.snd_dir, 'Minuet in D.wav'))
        for i in range(8):
            c = Cloud(self)
            c.rect.y += 500


        self.run()


    def run(self):
        # Game Loop
        pg.mixer.music.play(loops=-1)
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
        pg.mixer.music.fadeout(500)

    def update(self):
        # Game Loop - Update
        self.all_sprites.update()

        # spawn a mob?
        now = pg.time.get_ticks()
        if not self.player.jetpack:
            if now - self.mob_timer > 3000 + random.choice([-1000, -500, 0, 500, 1000]):
                self.mob_timer = now
                Mob(self)
                settings.POW_SPAWN_PCT = 4
        else:
            if now - self.mob_timer > 1000 + random.choice([-1000, -500, 0, 500, 1000]):
                self.mob_timer = now
                Mob(self)
                settings.POW_SPAWN_PCT = 12

        if now-self.meteortimer>2675 + self.randomer:
            self.meteortimer=now
            self.randomer=random.choice([-1000, -500, 0, 500, 1000])
            if not self.player.jetpack and not self.player.shield:
                meteorspawner=random.randrange(1,3)
            elif self.player.jetpack and not self.player.shield:
                meteorspawner=random.randrange(0,2)
            elif self.player.jetpack and self.player.shield:
                meteorspawner=random.randrange(1,4)
            else:meteorspawner=random.randint(3,5)
            for i in range(meteorspawner):
                Meteor(self)

        # hit mobs?
        if not self.player.jetpack:

            mob_hits = pg.sprite.spritecollide(self.player, self.mobs, True, pg.sprite.collide_mask)
            if mob_hits and mob_hits[0].rect.centerx<WIDTH-25 and mob_hits[0].rect.centerx>25 and self.player.shield==False:
                self.player.lives-=1
                if self.player.lives<=0:
                    self.playing = False
                    self.jump_sound.play()
                else:
                    self.boost_sound.play()

        elif self.player.jetpack:

            mob_hits = pg.sprite.spritecollide(self.player, self.mobs, False)
            if mob_hits:
                mob_hits = pg.sprite.spritecollide(self.player, self.mobs, True,pg.sprite.collide_mask)
                if mob_hits:
                    if mob_hits[0].rect.centerx<WIDTH-25 and mob_hits[0].rect.centerx>25 and self.player.shield==False:
                        self.player.lives-=1
                        if self.player.lives<=0:
                            self.playing = False
                            self.jump_sound.play()
                        else:
                            self.boost_sound.play()

        self.player.plat=False
        # check if player hits a platform - only if falling
        if self.player.vel.y >= 0:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                lowest = hits[0]
                for hit in hits:
                    if hit.rect.bottom > lowest.rect.bottom:
                        lowest = hit
                if self.player.pos.x < lowest.rect.right + 10 and \
                   self.player.pos.x > lowest.rect.left - 10:
                    if self.player.pos.y < lowest.rect.centery:
                        self.player.pos.y = lowest.rect.top
                        self.player.jumping = False
                        self.player.plat=lowest
                        self.player.vel.y = 0
                        if lowest.stay==1:
                            if lowest.posibil<25:
                                lowest.stay = 2
                                lowest.staytime = pg.time.get_ticks()
                            else:
                                lowest.stay=0

        clouds=[]
        for i in self.clouds:
            if i.rect.centery<HEIGHT+i.rect.width//2:
                clouds.append(i)

        while len(clouds)<25:
            bruh=Cloud(self)
            clouds.append(bruh)

        # if player reaches top 1/4 of screen
        if self.player.rect.top <= HEIGHT / 4:
            self.player.pos.y += max(abs(self.player.vel.y), 2)
            for cloud in self.clouds:
                cloud.rect.y+=max(cloud.movementspeedlist[cloud.index],2)
            for mob in self.mobs:
                if self.player.jetpack==False:
                    mob.rect.y += max(abs(self.player.vel.y), 2)
                else: mob.rect.y += abs(self.player.vel.y)//3
            for plat in self.platforms:
                plat.rect.y += max(abs(self.player.vel.y), 2)
                if plat.rect.top >= HEIGHT:
                    plat.kill()
                    self.score += 10
            for smoke in self.smokes:
                if smoke.rect.centery>0:
                    smoke.rect.centery+=max(abs(self.player.vel.y), 2)
            for meteor in self.meteors:
                if meteor.rect.centery>meteor.rect.height//2:
                    meteor.rect.centery+=max(abs(self.player.vel.y),2)

        # if player hits powerup
        pow_hits = pg.sprite.spritecollide(self.player, self.powerups, True)
        for pow in pow_hits:
            if pow.type == 'boost':
                self.boost_sound.play()
                self.player.vel.y = -pow.boostpower
                self.player.num_of_bullets+=pow.boostpower//10
                self.player.jumping = False
                self.player.lives+=pow.newltopl


                if self.player.shield:
                    self.player.shield+=1
                else:
                    self.player.shield=1
                    self.player.shieldtimer=pg.time.get_ticks()

                if self.player.lives>5:
                    self.player.lives=5

        mobbulhits=pg.sprite.groupcollide(self.mobs,self.bullets,False,True)
        for mob_hit in mobbulhits:
            mob_hit.hitstaken+=1
            if mob_hit.hitstaken==mob_hit.hitsneededtobetaken:
                Jetpack(self,mob_hit.rect,False)
                mob_hit.kill()

        for jetpack in self.jetpacks:
            jet_plat_col_check=pg.sprite.spritecollide(jetpack,self.platforms,False)
            if jet_plat_col_check:
                lowest=jet_plat_col_check[0]
            for plat in jet_plat_col_check:
                if plat.rect.centery>lowest.rect.centery:
                    lowest=plat
            if jet_plat_col_check:
                if jetpack.rect.centery<lowest.rect.centery:
                    jetpack.plat=lowest

        jetpack_pl_hit_check=pg.sprite.spritecollide(self.player,self.jetpacks,True)
        if jetpack_pl_hit_check:
            if self.player.jetpack:
                 self.player.jetpack+=1
            else:
                self.player.jetpack=1
                if not self.player.shield:
                    for meteor in self.meteors:
                        meteor.go()
                self.player.jetpacktimer=pg.time.get_ticks()
            self.player.jetpackduration=5350
            self.boost_sound.play()

        # Die!
        if self.player.rect.bottom > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 10)
                if sprite.rect.bottom < 0:
                    sprite.kill()
            for sprite in self.clouds:
                sprite.rect.y -= max(sprite.movementspeedlist[sprite.index], 10)
                if sprite.rect.bottom < 0:
                    sprite.kill()
        if len(self.platforms) == 0:
            self.playing = False

        # spawn new platforms to keep same average number
        while len(self.platforms) < 6:
            width = random.randrange(50, 100)
            Platform(self, random.randrange(0, WIDTH - width),
                     random.randrange(-75, -30))

        hits=pg.sprite.spritecollide(self.player,self.meteors,True)
        for hit in hits:
            if not self.player.shield or hit.type2=="canriPshield":
                self.player.lives-=1
                if self.player.lives<=0:
                    self.playing=False

        hits=pg.sprite.groupcollide(self.meteors,self.bullets,False,True)
        for hit in hits:
            if hit.type=="killble":
                hit.hitstaken+=1
                if hit.hitsneededtobetaken==hit.hitstaken:
                    Jetpack(self,hit.rect,False)
                    hit.kill()
            else:
                print("nanana")

    def events(self):
        # Game Loop - events
        for event in pg.event.get():
            # check for closing window
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.player.jump()
            if event.type == pg.KEYUP:
                if event.key == pg.K_SPACE and self.player.vel.y>=-PLAYER_JUMP:
                    self.player.jump_cut()

    def draw(self):
        # Game Loop - draw
        if self.score>5000:
            self.screen.fill(BGCOLOR3)
        elif self.score>3000:
            self.screen.fill(BGCOLOR2)
        else:
           self.screen.fill(BGCOLOR)

        self.all_sprites.draw(self.screen)
        self.draw_text("BULLETTS "+str(self.player.num_of_bullets), 25,YELLOW,( WIDTH / 2)+140, HEIGHT-30)
        self.draw_text("SCORE "+str(self.score)+" !!!", 40,YELLOW,( WIDTH / 2)-50, 15)
        self.draw_text("LIVES : "+str(self.player.lives)+" !!!", 40, GREEN, WIDTH / 2 + 130, 12)
        # *after* drawing everything, flip the display
        pg.display.flip()

    def show_start_screen(self):
        # game splash/start screen
        pg.mixer.music.load(path.join(self.snd_dir, 'Minuet in D.wav'))
        pg.mixer.music.play(loops=-1)
        self.screen.fill(BGCOLOR)
        self.draw_text(TITLE, 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Arrows to move, Space to jump", 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Press a key to play", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        self.draw_text("High Score: " + str(self.highscore), 22, WHITE, WIDTH / 2, 15)
        pg.display.flip()
        self.wait_for_key()
        pg.mixer.music.fadeout(500)

    def show_go_screen(self):
        # game over/continue
        if not self.running:
            return
        pg.mixer.music.load(path.join(self.snd_dir, 'Minuet in D.wav'))
        pg.mixer.music.play(loops=-1)
        self.screen.fill(BGCOLOR)
        self.draw_text("GAME OVER", 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Score: " + str(self.score), 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Press a key to play again", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text("NEW HIGH SCORE!", 22, WHITE, WIDTH / 2, HEIGHT / 2 + 40)
            with open(path.join(self.dir, HS_FILE), 'w') as f:
                f.write(str(self.score))
        else:
            self.draw_text("High Score: " + str(self.highscore), 22, WHITE, WIDTH / 2, HEIGHT / 2 + 40)
        pg.display.flip()
        self.wait_for_key()
        pg.mixer.music.fadeout(500)

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.KEYUP:
                    waiting = False

    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()

pg.quit()
