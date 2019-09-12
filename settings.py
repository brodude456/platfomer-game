# game options/settings
TITLE = "Jumpy!"
WIDTH = 480
HEIGHT = 600
FPS = 60
FONT_NAME = 'arial'
HS_FILE = "highscore.txt"
SPRITESHEET = "spritesheet_jumper.png"

# Player properties
PLAYER_ACC = 0.68
PLAYER_FRICTION = -0.125
PLAYER_GRAV = 0.8
PLAYER_JUMP = 25

# Game properties
BOOST_POWER = 60
POW_SPAWN_PCT = 4
MOB_FREQ = 5000
PLAYER_LAYER = 2
PLATFORM_LAYER = 1
POW_LAYER = 1
MOB_LAYER = 2
CLOUD_LAYER = 0
CLOUD_LAYER2 = 3

# Starting platforms
PLATFORM_LIST = [(0, HEIGHT - 60),
                 (WIDTH / 2 - 50, HEIGHT * 3 / 4 - 50),
                 (125, HEIGHT - 350),
                 (350, 200),
                 (175, 100)]

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLUE2 = (0, 0, 128)
YELLOW = (255, 255, 0)
LIGHTBLUE = (51, 153, 255)
BGCOLOR = LIGHTBLUE
BGCOLOR2 = BLUE
BGCOLOR3 = BLUE2
