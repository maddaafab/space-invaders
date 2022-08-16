import pygame
from pygame.locals import *
import random
from pygame import mixer #per gli effetti sonori

#inizializzo pygame
pygame.init()
pygame.mixer.pre_init(44100, -16, 2, 512) #valori di default
mixer.init()

clock=pygame.time.Clock()
fps=60

#schermo
screen_width=600
screen_height=700

screen=pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Space invaders")

#definisco il font
font20=pygame.font.SysFont("Constantia", 20)
font40=pygame.font.SysFont("Constantia", 40)

#score
score_val=0 ####################


alien_pause=1000 #pausa tra un proiettile e l'altro
last_alien_shot=pygame.time.get_ticks()
countdown=3
last_count=pygame.time.get_ticks()
game_over=0 #0 sto giocando, 1 il giocatore ha vinto, -1 il giocatore ha perso

red=(255,0,0)
green=(0,255,0)
white=(255,255,255)

#load immagine sfondo
bg=pygame.transform.scale(pygame.image.load("immagini/sfondo.jpg"),(600, 650))

#load sounds
explosion_fx = pygame.mixer.Sound("suoni/explosion.wav")
explosion_fx.set_volume(0.25)

explosion2_fx = pygame.mixer.Sound("suoni/explosion2.wav")
explosion2_fx.set_volume(0.25)

laser_fx = pygame.mixer.Sound("suoni/laser.wav")
laser_fx.set_volume(0.25)

def draw_bg():
    screen.blit(bg, (0,50)) #blitto l'immagine 50 in basso per aggiungere in alto lo score ecc

def draw_text(text,  font, text_col, x, y):
    img=font.render(text, True, text_col)
    screen.blit(img, (x,y))

def show_score():
    draw_text("SCORE:", font20, white, int(screen_width/2-100), 20)
    
#creo la navicella
class Spaceship(pygame.sprite.Sprite): #documentazione sprite (da mettere nella bibliografia del gioco): https://www.pygame.org/docs/ref/sprite.html
    def __init__(self, x, y, health):          #è una sottoclasse di un generico oggetto
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.image.load("immagini/navicella.png")
        self.rect=self.image.get_rect() #creo un rettangolo dall'immagine
        self.rect.center=[x,y]
        self.health_start= health
        self.health_remaining= health
        self.last_shot=pygame.time.get_ticks()

    def update(self): #sovrascrivo update della classe originale
        #velocità del movimento
        speed=8
        time=500 #millisecondi, tempo minimo tra uno sparo e l'altro
        game_over=0
        #get key press
        key= pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.rect.left>0:
            self.rect.x-=speed
        if key[pygame.K_RIGHT] and self.rect.right<screen_width:
            self.rect.x+=speed
        #record current time
        time_now=pygame.time.get_ticks() #per vedere quanto è passato da quando è stato sparato l'ultimo proiettile
        #shoot
        if key[pygame.K_SPACE] and time_now-self.last_shot>time:
            laser_fx.play()
            bullet=Bullets(self.rect.centerx, self.rect.top)
            bullet_group.add(bullet)
            self.last_shot=time_now
        #creo una "maschera" per la collisione ( per ignorare ciò che non è trasparente)
        self.mask= pygame.mask.from_surface(self.image) 
        
        #draw health bar
        pygame.draw.rect(screen, red, (self.rect.x, (self.rect.bottom+10), self.rect.width, 10))
        if self.health_remaining>0:
            pygame.draw.rect(screen, green, (self.rect.x, (self.rect.bottom+10), int(self.rect.width*(self.health_remaining/self.health_start)), 10)) #(self.rect.width*(self.health_remaining/self.health_start))
        elif self.health_remaining<=0:                                                                                                              #il rapporto serve per accorciare la barra verde man mano che la spaceship viene colpita
            explosion=Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)
            self.kill()
            game_over=-1
        return game_over


class Bullets(pygame.sprite.Sprite): 
    def __init__(self, x, y):  
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.image.load("immagini/proiettile_navicella.png")
        self.rect=self.image.get_rect()
        self.rect.center=[x,y]
        
    def update(self):
        self.rect.y-=5 #si muove verso l'alto
        if self.rect.bottom<50: #se il proiettile raggiunge la parte alta dello schermo viene eliminato
            self.kill()
            
        if pygame.sprite.spritecollide(self, alien_group, True):
            self.kill() #dopo la collisione il proiettile viene distrutto
            explosion_fx.play()
            explosion=Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)
            ###aggiungere lo score in base alle collisioni con diversi alieni
            
        if pygame.sprite.spritecollide(self, flying_saucer_group, True):
            self.kill() #dopo la collisione il proiettile viene distrutto
            explosion_fx.play()
            explosion=Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)
            #TUTTI GLI ALIENI VENGONO DISTRUTTI E IL GIOCATORE HA VINTO!!

            

            
#creo la classe alieno
class Aliens(pygame.sprite.Sprite): 
    def __init__(self, x, y, n):  
        pygame.sprite.Sprite.__init__(self)
        self.alien_type=n #n è per l'immagine
        self.image=pygame.image.load("immagini/alieno"+str(n)+".png")
        self.rect=self.image.get_rect()
        self.rect.center=[x,y]
        self.move_counter=0
        self.move_direction=1 #>0 perché iniziano muovendosi verso destra
        
    def update(self):
        self.rect.x+=self.move_direction
        self.move_counter+=1
        if abs(self.move_counter)>75: #si muovono di 75 pixel
            self.move_direction*=-1 #cambia direzione
            self.move_counter*=self.move_direction
        #AGGIUNGERE IL MOVIMENTO VERSO IL BASSO


#creo una classe per i proiettili degli alieni
class Alien_Bullets(pygame.sprite.Sprite): 
    def __init__(self, x, y):  
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.image.load("immagini/proiettile.png")
        self.rect=self.image.get_rect()
        self.rect.center=[x,y]
        
    def update(self):
        self.rect.y+=2 #si muove verso il basso
        if self.rect.top>screen_height: #se il proiettile raggiunge la parte bassa dello schermo viene eliminato
            self.kill()
        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
            self.kill() #così dopo la collisione il proiettile viene distrutto
            explosion2_fx.play()       #riduco la barra verde
            spaceship.health_remaining-=1
            explosion=Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)

#creo la classe disco volante
class Flying_Saucer(pygame.sprite.Sprite):
    def __init__(self, x, y): 
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.image.load("immagini/navicella_mistero.png")
        self.rect=self.image.get_rect()
        self.rect.center=[x,y]
        #self.move_counter=0
        self.move_direction=6 #>0 perché iniziano muovendosi verso destra

    def update(self): #############################################################
        self.rect.x+=self.move_direction
        #self.move_counter+=1
        if self.rect.x>screen_width or self.rect.x<0: 
            self.move_direction*=-1 #cambia direzione
            #self.move_counter*=self.move_direction
        

        
        
#creo la classe esplosione
class Explosion(pygame.sprite.Sprite): 
    def __init__(self, x, y, size):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f"immagini/exp{num}.png")
            if size == 1:
                img = pygame.transform.scale(img, (20, 20))
            if size == 2:
                img = pygame.transform.scale(img, (40, 40))
            if size == 3:
                img = pygame.transform.scale(img, (160, 160))
            #add the image to the list
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.counter = 0

    def update(self):
        explosion_speed=3
        #update explosion animation
        self.counter+=1
        if self.counter>=explosion_speed and self.index < len(self.images)-1:
            self.counter=0
            self.index+=1
            self.image=self.images[self.index]
        #se l'animazione è completa elimino l'esplosione
        if self.index>=len(self.images)-1 and self.counter >=explosion_speed:
            self.kill()
        
#creo uno sprite groups (per aggiungere funzionalità)
spaceship_group=pygame.sprite.Group()
bullet_group=pygame.sprite.Group()
alien_group=pygame.sprite.Group()
alien_bullet_group=pygame.sprite.Group()
flying_saucer_group=pygame.sprite.Group()
explosion_group=pygame.sprite.Group()

def create_aliens():
    i=1
    while i<=3:
        righe=2
        colonne=9
        for riga in range(0,righe):
            for item in range(0,colonne):
                alien=Aliens(100+(item)*50, 50+(riga+2*i)*30, i) #3*i è per evitare d sovrascrivere le immagini
                alien_group.add(alien)
        i=i+1
create_aliens() #non li creo nel while (altrimenti continua a disegnarli)

def create_FlyingSaucer(): #####################################################################
    flyingsaucer=Flying_Saucer(int(screen_width/2), 70)
    flying_saucer_group.add(flyingsaucer)

create_FlyingSaucer() ######################################
    

#creo il giocatore
spaceship=Spaceship(int(screen_width/2), screen_height-100, 3) #3= posso essere colpito 3 volte
spaceship_group.add(spaceship)
run=True
while run:
    clock.tick(fps)
    
    #draw background
    draw_bg()
    if countdown==0:
        #creo proiettili casuali per gli alieni (regolati da un timer)
        time_now=pygame.time.get_ticks()
        #sparo
        if time_now - last_alien_shot > alien_pause and len(alien_bullet_group) < 5 and len(alien_group) > 0:
            attacking_alien = random.choice(alien_group.sprites())
            alien_bullet = Alien_Bullets(attacking_alien.rect.centerx, attacking_alien.rect.bottom)
            alien_bullet_group.add(alien_bullet)
            last_alien_shot = time_now
        #controllo se tutti gli alieni sono morti
        if len(alien_group)==0:
            game_over=1 #il giocatore ha vinto
        if game_over==0: #sto giocando
            #update spaceship
            game_over=spaceship.update()
            #update sprite groups
            bullet_group.update()
            alien_group.update()
            alien_bullet_group.update()
            flying_saucer_group.update()
            
        else:
            if game_over==-1: #il giocatore ha perso
                draw_text("GAME OVER!", font40, white, int(screen_width/2-100), int(screen_height/2+50))
            if game_over==1: #il giocatore ha vinto
                draw_text("YOU WIN!", font40, white, int(screen_width/2-100), int(screen_height/2+50))         

    if countdown>0:
        draw_text("GET READY!", font40, white, int(screen_width/2-110), int(screen_height/2+50))
        draw_text(str(countdown), font40, white, int(screen_width/2-10), int(screen_height/2+100))
        count_timer=pygame.time.get_ticks()
        if count_timer-last_count>1000:
            countdown-=1
            last_count=count_timer
            
    #update explosion group
    explosion_group.update()

    #draw sprite group
    spaceship_group.draw(screen)
    bullet_group.draw(screen)
    alien_group.draw(screen)
    alien_bullet_group.draw(screen)
    flying_saucer_group.draw(screen) #######
    explosion_group.draw(screen)

    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            run=False

    pygame.display.update()

pygame.quit()
