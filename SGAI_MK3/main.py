import pygame
from Board import Board
#import PygameFunctions as PF
import random as rd 
import pickle
import PygameFunctions as PF
from MCTS import *

# Constants
AI_PLAY_WAITTIME_MS = 5000

# Initialize variables
running = True
take_action = []
playerMoved = False
font = pygame.font.SysFont("Comic Sans", 20)
self_play = False
hospital = False

# Option menu
SelfPlayButton = pygame.Rect(350, 250, 100, 100)
HospitalOnButton = pygame.Rect(700, 250, 100, 100)
ProceedButton = pygame.Rect(1050, 650, 100, 100)


proceed = False
hover = ""
while proceed == False:
    for event in pygame.event.get():
        PF.display_options_screen(self_play, hospital, hover)
        hover = ""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if SelfPlayButton.collidepoint(pygame.mouse.get_pos()):
                self_play = not self_play
            elif HospitalOnButton.collidepoint(pygame.mouse.get_pos()):
                hospital = not hospital
            elif ProceedButton.collidepoint(pygame.mouse.get_pos()):
                proceed = True
        elif event.type == pygame.MOUSEMOTION:
            if ProceedButton.collidepoint(pygame.mouse.get_pos()):
                hover = "proceed"
            elif HospitalOnButton.collidepoint(pygame.mouse.get_pos()):
                hover = "hospital"
            elif SelfPlayButton.collidepoint(pygame.mouse.get_pos()):
                hover = "self" 
        elif event.type == pygame.QUIT:
            pygame.quit()
#Create the game board
GameBoard = Board()

# Self play variables
clock = pygame.time.Clock()
frame = 0

mcts = MCTS()

try:
    with open("mcts.pickle", "rb") as f:
        mcts = pickle.load(f)
except:
    pass

# Buttons
kill_img = pygame.image.load("Assets/kill_button.png").convert_alpha()
KillButton = kill_img.get_rect(topleft=(800, 50))

heal_img = pygame.image.load("Assets/heal_button.png").convert_alpha()
HealButton = heal_img.get_rect(topleft=(800, 200))

kill_button = "button"
heal_button = "button"

while running:
    P = PF.run(GameBoard, hospital, heal_button, kill_button)
    if self_play:        
        # Event a 
        for event in P:
            if HealButton.collidepoint(pygame.mouse.get_pos()):
                if event.type == pygame.MOUSEBUTTONUP:                          # If heal button is let go of, select heal and update heal button image to selected
                    take_action.append("heal")
                    heal_button = "select"
                elif event.type == pygame.MOUSEBUTTONDOWN:                      # If heal button is pressed, update heal button image to pressed
                    heal_button = "press"
                elif heal_button != "select":                                   # If mouse is over heal button, update heal button to hovering
                    heal_button = "hover"                       
            elif heal_button != "select":
                heal_button = "button"
            if KillButton.collidepoint(pygame.mouse.get_pos()):
                if event.type == pygame.MOUSEBUTTONUP:                          # If kill button is let go of, select kill and update kill button image to selected
                    take_action.append("kill")
                    kill_button = "select"
                elif event.type == pygame.MOUSEBUTTONDOWN:                      # If kill button is pressed, update kill button image to pressed
                    kill_button = "press"
                elif kill_button != "select":
                    kill_button = "hover"                                       # If mouse is over kill button, update kill button to hovering
            elif kill_button != "select":
                kill_button = "button"
            if event.type == pygame.MOUSEBUTTONUP:
                if len(take_action) < 2:                                        # Checks if list is less than 2
                    x, y = pygame.mouse.get_pos()                               
                    action = PF.get_action(GameBoard, x, y)                     # If it is, find position of tile
                    if action != None:
                        print(action)
                        if take_action == []:                                   # If take_action is empty, check if selected tile is empty. If so, add selected tile as target
                            if ((GameBoard.states[action[0]][action[1]] is not None) and (GameBoard.states[action[0]][action[1]].isZombie == False)):
                                take_action.append(action)
                        else:                                                   # Otherwise, add selected tile as destination
                            print(action)
                            take_action.append(action)
            if event.type == pygame.QUIT:
                running = False
        # Display the current action
        PF.screen.blit(
            font.render("Your move is currently:", True, PF.WHITE),
            (800, 400),
        )
        PF.screen.blit(font.render(f"{take_action}", True, PF.WHITE), (800, 450))

        # Deselects or overrides action button
        if len(take_action) == 2:
            if take_action[0] == take_action[1]:
                take_action = []
                kill_button, heal_button = "button", "button"
            elif isinstance(take_action[1], str):
                take_action.pop(0)
                if take_action[0] == "heal":
                    kill_button = "button"
                else:
                    heal_button = "button"

        # Draws selection of game piece
        if len(take_action) == 1:
            if not isinstance(take_action[0], str):
                PF.select(take_action[0])

        # Action handling
        if len(take_action) == 2:
            if not isinstance(take_action[0], str):
                result = None
                directionToMove = PF.direction(take_action[0], take_action[1])
                if directionToMove == "moveUp":
                    result = GameBoard.moveUp(take_action[0])
                elif directionToMove == "moveDown":
                    result = GameBoard.moveDown(take_action[0])                                 
                elif directionToMove == "moveLeft":
                    result = GameBoard.moveLeft(take_action[0])
                elif directionToMove == "moveRight":
                    result = GameBoard.moveRight(take_action[0])
                print(result)
                if result != False:
                    playerMoved = True
                take_action = []
            elif take_action[0] == "heal":
                result = GameBoard.heal(take_action[1])
                if result[0] != False:
                    playerMoved = True
                    heal_button = "button"
                    if result[1] == "half": 
                        # Half heal animation
                        while frame < 12:
                            PF.half_heal_animation(frame)
                            pygame.display.update()
                            # clock.tick(12) sets frames per second to 12
                            clock.tick(12)
                            frame += 1
                        frame = 0
                    elif result[1] == "full":
                        while frame < 16:
                            PF.full_heal_animation(frame)
                            pygame.display.update()
                            # clock.tick(12) sets frames per second to 12
                            clock.tick(8)
                            frame += 1
                        frame = 0
                    elif result[1] == "vaccine": 
                        while frame < 6:
                            PF.vaccine_animation(frame)
                            pygame.display.update()
                            # clock.tick(12) sets frames per second to 12
                            clock.tick(8)
                            frame += 1
                        frame = 0
                take_action = []
            elif take_action[0] == "kill":
                kill_button = "button"
                result = GameBoard.kill(take_action[1])
                if result != False:
                    playerMoved = True
                    kill_button = "button"                                  # turns kill button back to normal
                    # Plays kill animation
                    while frame < 9:
                        PF.kill_animation(frame)
                        pygame.display.update()
                        # clock.tick(8) sets frames per second to 8
                        clock.tick(8)
                        frame += 1
                    frame = 0
                take_action = []

        # Computer turn
        if playerMoved:
            pygame.display.update()
            playerMoved = False
            take_action = []
                        
            GameBoard.zombie_random_move()            
            GameBoard.update()
        pygame.display.update()

    # AI Algorithm        
    else:        
        #pygame.time.wait(AI_PLAY_WAITTIME_MS)

        best_move_next_board = mcts.search(GameBoard)
        GameBoard = best_move_next_board.board        

        print(" Human (AI): ")
        print(GameBoard)

        if GameBoard.num_zombies() == 0:
            with open("mcts.pickle", "wb") as f:
                pickle.dump(mcts, f)
            print("Humans Win")
            GameBoard.clean_board()
            GameBoard.populate()  
            print("\n\n\n")
            break

        # Zombies turn        
        GameBoard = GameBoard.zombie_move()
        GameBoard.update()
        
        print(" Zombie: ")
        print(GameBoard)

        if GameBoard.num_humans() == 0:
            with open("mcts.pickle", "wb") as f:
                pickle.dump(mcts, f)
            print("Zombies Win")            
            GameBoard.clean_board()
            GameBoard.populate()              
            print("\n\n\n")                    

        """
        for event in P:
            if event.type == pygame.QUIT:
                running = False
                break 
        
        # Update the display
        pygame.display.update()                
        """


