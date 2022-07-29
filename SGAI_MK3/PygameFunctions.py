import pygame

BACKGROUND = "#b0b0b0"
BACKGROUND1 = "#63666A"
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CELL_COLOR = (176, 176, 176)
HOSPITAL_COLOR = (191, 209, 255)
LINE_WIDTH = 5
DISPLAY_BORDER = 150
DISPLAY_CELL_DIMENSIONS = (100,100)

image_assets = [
    "person_normal.png",
    "person_vax.png",
    "person_zombie.png",
    "person_half_zombie.png",
    "kill_background.png",
]

# Initialize pygame
screen = pygame.display.set_mode((1200, 800))
pygame.display.set_caption("Outbreak!")
pygame.font.init()
game_window_dimensions = (1400, 800)
person_dimensions = (20, 60)
pygame.display.set_caption("Outbreak!")
screen.fill(BACKGROUND)

board = None  

def get_action(GameBoard, pixel_x, pixel_y):
    """
    Get the action that the click represents.
    If the click was on the heal button, returns "heal"
    Else, returns the board coordinates of the click (board_x, board_y) if valid
    Return None otherwise
    """
    # Check if the user clicked on the "heal" icon, return "heal" if so

    # Get the grid (x,y) where the user clicked
    if pixel_x > DISPLAY_BORDER and pixel_y > DISPLAY_BORDER:   # Clicking to the top or left of the border will result in a grid value of 0, which is valid
        board_x = int((pixel_x - DISPLAY_BORDER) / DISPLAY_CELL_DIMENSIONS[0])
        board_y = int((pixel_y - DISPLAY_BORDER) / DISPLAY_CELL_DIMENSIONS[1])
        # Return the grid position if it is a valid position on the board
        if (board_x >= 0 and board_x < GameBoard.columns and board_y >= 0 and board_y < GameBoard.rows):
            return (board_y, board_x)
    return None

def run(GameBoard, hasHospital, heal_button, kill_button):
    """
    Draw the screen and return any events.
    """

    if GameBoard is None: return
    screen.fill(BACKGROUND)
    build_grid(GameBoard, hasHospital) # Draw the grid
    display_buttons(heal_button, kill_button)
    display_people(GameBoard)            

def display_buttons(heal_button, kill_button):
    display_image(screen, "Assets/kill_" + kill_button + ".png", (), (800, 50))         # draws specified kill button asset
    display_image(screen, "Assets/heal_" + heal_button + ".png", (), (800, 200))        # draws specified heal button asset

def get_events():
    return pygame.event.get()

def display_image(screen, itemStr, dimensions, position):
    """
    Draw an image on the screen at the indicated position.
    """
    v = pygame.image.load(itemStr).convert_alpha()    
    if len(dimensions) != 0:
        v = pygame.transform.scale(v, dimensions)
    screen.blit(v, position)

def build_grid(GameBoard, hasHospital):
    """
    Draw the grid on the screen.
    """
    grid_width = GameBoard.columns * DISPLAY_CELL_DIMENSIONS[0]
    grid_height = GameBoard.rows * DISPLAY_CELL_DIMENSIONS[1]
    pygame.draw.rect(screen, BLACK, [DISPLAY_BORDER - LINE_WIDTH, DISPLAY_BORDER - LINE_WIDTH, LINE_WIDTH, grid_height + (2 * LINE_WIDTH)])  # left
    pygame.draw.rect(screen, BLACK, [DISPLAY_BORDER + grid_width, DISPLAY_BORDER - LINE_WIDTH, LINE_WIDTH, grid_height + (2 * LINE_WIDTH)])  # right
    pygame.draw.rect(screen, BLACK, [DISPLAY_BORDER - LINE_WIDTH, DISPLAY_BORDER + grid_height, grid_width + (2 * LINE_WIDTH), LINE_WIDTH])  # bottom
    pygame.draw.rect(screen, BLACK, [DISPLAY_BORDER - LINE_WIDTH, DISPLAY_BORDER - LINE_WIDTH, grid_width + (2 * LINE_WIDTH), LINE_WIDTH])   # top
    pygame.draw.rect(screen, CELL_COLOR, [DISPLAY_BORDER, DISPLAY_BORDER, grid_width, grid_height]) # Fill the inside wioth the cell color
    
    if hasHospital == True:
        pygame.draw.rect(screen, HOSPITAL_COLOR, [150, 150, 300, 300])

    # Draw the vertical lines
    i = DISPLAY_BORDER + DISPLAY_CELL_DIMENSIONS[0]
    while i < DISPLAY_BORDER + grid_width:
        pygame.draw.rect(screen, BLACK, [i, DISPLAY_BORDER, LINE_WIDTH, grid_height])
        i += DISPLAY_CELL_DIMENSIONS[0]
    # Draw the horizontal lines
    i = DISPLAY_BORDER + DISPLAY_CELL_DIMENSIONS[1]
    while i < DISPLAY_BORDER + grid_height:
        pygame.draw.rect(screen, BLACK, [DISPLAY_BORDER, i, grid_width, LINE_WIDTH])
        i += DISPLAY_CELL_DIMENSIONS[1]

def display_people(GameBoard):
    """
    Draw the people (government, vaccinated, and zombies) on the grid.
    """
    for r in range(GameBoard.rows):
        for c in range(GameBoard.columns):
            if GameBoard.states[r][c] is not None:
                p = GameBoard.states[r][c]
                char = "Assets/" + image_assets[0]
                if p.isVaccinated:
                    char = "Assets/" + image_assets[1]
                elif p.isZombie and p.halfCured == False:
                    char = "Assets/" + image_assets[2]
                elif p.isZombie and p.halfCured:
                    char = "Assets/" + image_assets[3]
                coords = (
                    c * DISPLAY_CELL_DIMENSIONS[1] + DISPLAY_BORDER + 10,
                    r * DISPLAY_CELL_DIMENSIONS[0] + DISPLAY_BORDER + 10,
                )
                display_image(screen, char, (80, 80), coords)

def display_win_screen():
    screen.fill(BACKGROUND)
    screen.blit(
        pygame.font.SysFont("Comic Sans", 32).render("You win!", True, WHITE),
        (500, 400),
    )
    pygame.display.update()

    # catch quit event
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

def display_lose_screen():
    screen.fill(BACKGROUND)
    screen.blit(
        pygame.font.SysFont("Comic Sans", 32).render("You lose lol!", True, WHITE),
        (500, 500),
    )
    pygame.display.update()

    # catch quit event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return
def display_start_screen(starthover):
    screen.fill(BACKGROUND1)
    my_font = pygame.font.Font("Assets/Minecraft.ttf", 100)
    text_image = my_font.render("Outbreak", True, WHITE)
    screen.blit(
         text_image, (375, 100),
    )
    image = pygame.image.load("Assets/person_normal_big.png")
    screen.blit(image, (900,350))
    image = pygame.image.load("Assets/person_zombie_big.png")
    screen.blit(image, (700,350))
    if starthover == "start":
        display_image(screen, "Assets/start_img_2.png", (300, 100), (455, 500))
    else:
        display_image(screen, "Assets/start_img.png", (300, 100), (455, 500))
    pygame.display.update()

def display_options_screen(self_play, hospital, hover):
    screen.fill(BACKGROUND)

    screen.blit(
        pygame.font.SysFont("Calibri", 40).render("OPTIONS", True, WHITE), (500, 100),
    )
    screen.blit(
        pygame.font.SysFont("Calibri", 32).render("Self Play?", True, WHITE), (325, 200),
    )
    screen.blit(
        pygame.font.SysFont("Calibri", 32).render("Hospital On?", True, WHITE), (675, 200),
    )
    screen.blit(
        pygame.font.SysFont("Calibri", 24).render("Proceed to game...", True, WHITE), (975, 600),
    )
    screen.blit(
        pygame.font.SysFont("Calibri", 24).render("Show Stats", True, WHITE), (500, 450),
    )

    if hover == "proceed":
        display_image(screen, "Assets/checked_box.png", (100, 100), (1050, 650))
    else:
        display_image(screen, "Assets/unchecked_box.png", (100, 100), (1050, 650))
    if hover == "hospital":
        display_image(screen, "Assets/checked_box.png", (100, 100), (700, 250))
    else:
        if hospital:
            display_image(screen, "Assets/checked_box.png", (100, 100), (700, 250))
        else:
            display_image(screen, "Assets/unchecked_box.png", (100, 100), (700, 250))
    if hover == "self":
        display_image(screen, "Assets/checked_box.png", (100, 100), (350, 250))
    else:
        if self_play: 
            display_image(screen, "Assets/checked_box.png", (100, 100), (350, 250))
        else:
            display_image(screen, "Assets/unchecked_box.png", (100, 100), (350, 250))
    
    # Show Stats button
    display_image(screen, "Assets/DefaultButton.png", (100, 100), (500, 500))
    
    pygame.display.update()

def select(coord):
    left = coord[1] * 100 + 150
    top = coord[0] * 100 + 150
    color = (232, 232, 232)
    # Drawing Rectangle
    pygame.draw.rect(screen, color, pygame.Rect(left, top, 100 + LINE_WIDTH, 100 + LINE_WIDTH),  LINE_WIDTH+3)
    pygame.display.update()

def kill_animation(frame):
    char = "Assets/" + image_assets[4]
    # Draws background first and then draws the specified frame. The animations have the same number of frames and are already made to be synched up
    display_image(screen, char, (), (0,0))
    display_image(screen, "Assets/zombiedeath/sprite_" + str(frame) + ".png", (200, 200), (400, 350))
    display_image(screen, "Assets/watergun/sprite_" + str(frame) + ".png", (200, 200), (600, 350))

def half_heal_animation(frame):
    image = str(frame)
    if frame < 10:
        image = "0" + str(frame)
    display_image(screen, "Assets/heal1_background.png", (), (0, 200))
    display_image(screen, "Assets/heal1_zombie/sprite_" + image + ".png", (200, 200), (428, 350))    
    display_image(screen, "Assets/heal1_human/sprite_" + image + ".png", (200, 200), (572, 350))

def full_heal_animation(frame):
    image = str(frame)
    if frame < 10:
        image = "0" + str(frame)
    display_image(screen, "Assets/heal2_background.png", (), (0, 200))
    display_image(screen, "Assets/heal2_zombie/sprite_" + image + ".png", (200, 200), (428, 350))    
    display_image(screen, "Assets/heal2_human/sprite_" + image + ".png", (200, 200), (572, 350))

def vaccine_animation(frame):
    display_image(screen, "Assets/heal2_background.png", (), (0, 200))
    display_image(screen, "Assets/vaccine/sprite_" + str(frame) + ".png", (200, 200), (428, 350))    
    display_image(screen, "Assets/heal2_human/sprite_0" + str(frame) + ".png", (200, 200), (572, 350))

def zombie_bite(frame):
    image = str(frame)
    if frame < 10:
        image = "0" + str(frame)
    # Draws background first and then draws the specified frame. The animations have the same number of frames and are already made to be synched up
    display_image(screen, "Assets/zombie_bite_background.png", (), (0,0))
    display_image(screen, "Assets/zombie_bite/sprite_" + image + ".png", (250, 200), (500, 350))

def direction(coord1, coord2):
    if coord2[0] > coord1[0]:
        return "moveUp"
    elif coord2[0] < coord1[0]:
        return "moveDown"
    elif coord2[1] > coord1[1]:
        return "moveRight"
    elif coord2[1] < coord1[1]:
        return "moveLeft"
