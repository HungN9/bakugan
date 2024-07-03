import pygame
import pymunk
import pymunk.pygame_util
import math

pygame.init()

SCREEN_WIDTH = 678
SCREEN_HEIGHT = 800
BOTTOM_PANEL = 50

#game window
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT+BOTTOM_PANEL))
pygame.display.set_caption("Bakugan")

#pymunk space
space = pymunk.Space()
static_body = space.static_body
draw_option = pymunk.pygame_util.DrawOptions(screen)

#game variables
dia = 40
taking_shot = True
game_running = True
force = 0
max_force = 8000
force_direction = 1
powering_up = False
potted_balls = []
lives = 5
onGateCard = False

#clock
clock = pygame.time.Clock()
FPS = 120

# colors 
BG = (50,50,50)
RED = (255, 0, 0)
WHITE = (255,255,255)

#fonts
font = pygame.font.SysFont("Lato", 30)
large_font = pygame.font.SysFont("Lato", 60)

#load images
cue_image = pygame.image.load("assets/cue.png").convert_alpha()
aquB1 = pygame.image.load("assets/M01_AQU_B.png").convert_alpha()
ShieldLeoness = pygame.image.load("assets/Shield_Leoness.png").convert_alpha()
ShieldLeoness = pygame.transform.scale(ShieldLeoness, (90, 90))
ShieldLeonessOpen = pygame.image.load("assets/Shield_Leoness_Ball.png").convert_alpha()
ShieldLeonessOpen = pygame.transform.scale(ShieldLeonessOpen, (150, 150))


#function for outputting text on the screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

#function for creating gate cards
def create_gate_cards(pos):
    body = pymunk.Body


#function for creating balls
def create_ball(radius, pos):
    body = pymunk.Body()
    body.position = pos
    shape = pymunk.Circle(body, radius)
    shape.mass = 5
    shape.elasticity = 0.8
    #use pivot joint to add friction
    pivot = pymunk.PivotJoint(static_body, body, (0,0), (0,0))
    pivot.max_bias = 0 #diable joint correction
    pivot.max_force = 1000 #emulate linear friction

    space.add(body, shape, pivot)
    return shape

#setup game balls
balls = []

#test ball
new_ball = create_ball(dia, (SCREEN_WIDTH / 2, 600 + dia + 20))
balls.append(new_ball)

#create power bars to show how hard the cue ball will be hit
power_bar = pygame.Surface((10,20))
power_bar.fill(RED)

#create pool cue
class Cue():
    def __init__(self, pos):
        self.original_image = cue_image
        self.angle = 0
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = pos

    def update(self, angle):
        self.angle = angle
    
    def draw(self, surface):
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        surface.blit(self.image, (self.rect.centerx - self.image.get_width() / 2, self.rect.centery - self.image.get_height() / 2))
    
def create_boundaries(space, SCREEN_WIDTH, SCREEN_HEIGHT):
    rects = [
        [(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 10), (SCREEN_WIDTH, 20)],
        [(SCREEN_WIDTH / 2, 10), (SCREEN_WIDTH, 20)],
        [(10, SCREEN_HEIGHT / 2), (20, SCREEN_HEIGHT)],
        [(SCREEN_WIDTH - 10, SCREEN_HEIGHT / 2), (20, SCREEN_HEIGHT)]
    ]

    for pos, size in rects:
        body = pymunk.Body(body_type = pymunk.Body.STATIC)
        body.position = pos
        shape = pymunk.Poly.create_box(body, size)
        shape.elasticity = 0.4
        shape.friction = 0.5
        space.add(body, shape)

create_boundaries(space, SCREEN_WIDTH, SCREEN_HEIGHT)
cue = Cue(balls[-1].body.position)

#game loop
run = True
while run:

    clock.tick(FPS)
    space.step(1 / FPS)

    #fill background
    screen.fill(BG)

    #draw a gate card
    screen.blit(aquB1, (SCREEN_WIDTH / 2 - 100,0))

    #gate card location
    gatecards = [(SCREEN_WIDTH / 2 + 15, 150)]

    #check if all the balls have stopped moving
    taking_shot = True
    for ball in balls:
        if int(ball.body.velocity[0]) != 0 or int(ball.body.velocity[1]) != 0:
            taking_shot = False

    #draw pool cue
    if taking_shot == True and game_running == True and onGateCard == False:
        #calculate pool cue angle
        mouse_pos = pygame.mouse.get_pos()
        cue.rect.center = balls[-1].body.position
        x_dist = balls[-1].body.position[0] - mouse_pos[0]
        y_dist = -(balls[-1].body.position[1] - mouse_pos[1]) # negative because pygame y coordiantes increase downwards
        cue_angle = math.degrees(math.atan2(y_dist, x_dist))
        cue.update(cue_angle)
        cue.draw(screen)  

    #power up pool cue
    if powering_up == True and game_running == True:
        force += 100 * force_direction
        if (force >= max_force or force <= 0):
            force_direction *= -1
        #draw power bars
        for b in range(math.ceil(force / 2000)):
            screen.blit(power_bar, ((balls[-1].body.position[0] - 30 + (b * 15)), (balls[-1].body.position[1] + 30)))
    elif powering_up == False and taking_shot == True:
        x_impulse = math.cos(math.radians(cue_angle))
        y_impulse = math.sin(math.radians(cue_angle))
        balls[-1].body.apply_impulse_at_local_point((force * -x_impulse, force * y_impulse), (0,0))
        force = 0
        force_direction = 1

    # draw bottom panel
    pygame.draw.rect(screen, WHITE, (0, 0, 0, BOTTOM_PANEL))
    draw_text("LIVES: " +str(lives), font, WHITE, 0, SCREEN_HEIGHT + 10)

    #checking if a Bakugan is on a Gate Card
    ball_x_dist = abs(new_ball.body.position[0] - gatecards[0][0])
    ball_y_dist = abs(new_ball.body.position[1] - gatecards[0][1])
    ball_dist = math.sqrt((ball_x_dist ** 2) + (ball_y_dist ** 2))
    if ball_dist <= 128 :
        screen.blit(ShieldLeonessOpen, (new_ball.body.position[0] - 80, new_ball.body.position[1] - 80))
        new_ball.body.velocity = (0.0, 0.0)
        onGateCard = True
        taking_shot = False
    else:
        #drawing a bakugan
        screen.blit(ShieldLeoness, (new_ball.body.position[0] - 45, new_ball.body.position[1] - 45))

    #event handler
    for event in pygame.event.get():
        if onGateCard == False and taking_shot == True:
            #shooting a bakugan forward
            if event.type == pygame.MOUSEBUTTONDOWN:
                powering_up = True
            if event.type == pygame.MOUSEBUTTONUP:
                powering_up = False
        elif onGateCard == True and taking_shot == False:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    #reposition cue ball
                    balls[-1].body.position = (SCREEN_WIDTH / 2, 600 + dia + 20)
                    onGateCard = False
                    taking_shot = True
        if event.type == pygame.QUIT:
            run = False
        #space.debug_draw(draw_option)
        pygame.display.update()
    
pygame.quit()