import pygame
from Board import Board
#import PygameFunctions as PF
import random as rd 

from MCTS import *

# Constants
AI_PLAY_WAITTIME_MS = 5000

# Initialize variables
running = True
take_action = []
playerMoved = False
#font = pygame.font.SysFont("Comic Sans", 20)
self_play = False
hospital = True

"""
# Option menu
SelfPlayButton = pygame.Rect(350, 250, 100, 100)
HospitalOnButton = pygame.Rect(700, 250, 100, 100)
ProceedButton = pygame.Rect(1050, 650, 100, 100)


proceed = False
hover = False
while proceed == False:
    for event in pygame.event.get():
        PF.display_options_screen(self_play, hospital, hover)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if SelfPlayButton.collidepoint(pygame.mouse.get_pos()):
                self_play = not self_play
            elif HospitalOnButton.collidepoint(pygame.mouse.get_pos()):
                hospital = not hospital
            elif ProceedButton.collidepoint(pygame.mouse.get_pos()):
                proceed = True
        elif event.type == pygame.MOUSEMOTION:
            if ProceedButton.collidepoint(pygame.mouse.get_pos()):
                hover = True
            else:
                hover = False
        elif event.type == pygame.QUIT:
            pygame.quit()
"""

#Create the game board
board = Board()

# Self play variables
#clock = pygame.time.Clock()
frame = 0

mcts = MCTS()
while running:
    #P = PF.run(board, hospital)
    if self_play:        
        # Event a
        for event in P:
            if event.type == pygame.MOUSEBUTTONUP:
                x, y = pygame.mouse.get_pos()
                action = PF.get_action(board, x, y)                     # Can only return "heal", coordinate of grid clicked, or None. 
                if action == "heal":                                        # Process a "heal" intention if take_action is currently empty
                    if take_action == []:
                        take_action.append("heal")
                elif action == "kill":                                        # Process a "heal" intention if take_action is currently empty
                    if take_action == []:
                        take_action.append("kill")
                elif action != None:                                        # Otherwise, get the coordinate of a valid grid cell that was clicked                                                                 
                    if take_action == []:                                   # Check that the click corresponds to an intention to move a player
                        # Returns true if the space is not empty and it is a piece belonging to the player.
                        if ((board.states[action[0]][action[1]] is not None) and (board.states[action[0]][action[1]].isZombie == False)):
                            take_action.append("move")
                    if take_action != []:                                   # Only append a coordinate if there is a pending "heal" or "move" intention
                        take_action.append(action)
                        if len(take_action) > 2:
                            if take_action[1] == take_action[2]:
                                take_action = []
            if event.type == pygame.QUIT:
                running = False

        # Draws selection box
        if len(take_action) == 2:
            PF.select(take_action[1])
        # Action handling
        if len(take_action) > 1:
            if take_action[0] == "move":
                if len(take_action) > 2:        #Makes sure the second coordinate is clicked
                    directionToMove = PF.direction(take_action[1], take_action[2])
                    result = [False, None]
                    if directionToMove == "moveUp":
                        result = board.moveUp(take_action[1])
                    elif directionToMove == "moveDown":
                        result = board.moveDown(take_action[1])
                    elif directionToMove == "moveLeft":
                        result = board.moveLeft(take_action[1])
                    elif directionToMove == "moveRight":
                        result = board.moveRight(take_action[1])
                    if result[0] != False:
                        playerMoved = True
                    take_action = []
            elif take_action[0] == "heal":
                result = board.heal(take_action[1])
                if result[0] != False:
                    playerMoved = True
                    if result[2] == "half":
                        # Half heal animation
                        while frame < 12:
                            PF.half_heal_animation(frame)
                            pygame.display.update()
                            # clock.tick(12) sets frames per second to 12
                            clock.tick(12)
                            frame += 1
                        frame = 0
                    elif result[2] == "full":
                        while frame < 16:
                            PF.full_heal_animation(frame)
                            pygame.display.update()
                            # clock.tick(12) sets frames per second to 12
                            clock.tick(12)
                            frame += 1
                        frame = 0
                take_action = []
            elif take_action[0] == "kill":
                result = board.kill(take_action[1])
                if result[0] != False:
                    playerMoved = True
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
                        
            board.zombie_move()                        
            board.update()

            if board.num_zombies() == 0:
                print("You won! Your score is: " + str(board.total_score()))
                break
            if board.num_humans() == 0:
                print("You lost!")
                break


        # Update the display
        pygame.display.update()

    # AI Algorithm        
    else:        
        #pygame.time.wait(AI_PLAY_WAITTIME_MS)

        best_move_next_board = mcts.search(board)
        board = best_move_next_board.board        

        print(" Human (AI): ")
        print(board)

        if board.num_zombies() == 0:
            print("Humans Win")
            board.clean_board()
            board.populate()            
            print("\n\n\n")

        # Zombies turn        
        board = board.zombie_move()
        board.update()
        
        print(" Zombie: ")
        print(board)

        if board.num_humans() == 0:
            print("Zombies Win")            
            board.clean_board()
            board.populate()              
            print("\n\n\n")                    

        """
        for event in P:
            if event.type == pygame.QUIT:
                running = False
                break 
        
        # Update the display
        pygame.display.update()                
        """
