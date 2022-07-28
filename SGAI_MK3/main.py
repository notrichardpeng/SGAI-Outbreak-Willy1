from numpy import isin
import pygame
from Board import Board
import PygameFunctions as PF
import random as rd 

# Constants
ROWS = 6
COLUMNS = 6
BORDER = 150                    # Number of pixels to offset grid to the top-left side
CELL_DIMENSIONS = (100,100)     # Number of pixels (x,y) for each cell
ACTION_SPACE = ["moveUp", "moveDown", "moveLeft", "moveRight", "heal", "bite", "kill"]
SELF_PLAY = True
AI_PLAY_WAITTIME_MS = 50

# Player role variables
player_role = "Government"      # Valid options are "Government" and "Zombie"
roleToRoleNum = {"Government": 1, "Zombie": -1}
roleToRoleBoolean = {"Government": False, "Zombie": True}       # False means Human, True means Zombie. Switching this would turn Humans to Zombies, and vice versa. 

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
GameBoard = Board((ROWS,COLUMNS), BORDER, CELL_DIMENSIONS, roleToRoleNum[player_role], hospital)
GameBoard.populate()

# Self play variables
alpha = 0.1
gamma = 0.6
epsilon = 0.1
epochs = 1000
epochs_ran = 0
Original_Board = GameBoard.clone(GameBoard.States)
clock = pygame.time.Clock()
frame = 0 
hovering = ""
action_type = ""

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
                        idx = GameBoard.toIndex(action)
                        if take_action == []:                                   # If take_action is empty, check if selected tile is empty. If so, add selected tile as target
                            if ( (GameBoard.States[idx].person is not None) and (GameBoard.States[idx].person.isZombie == roleToRoleBoolean[player_role]) ):
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
                directionToMove = PF.direction(take_action[0], take_action[1])
                result = [False, None]
                if directionToMove == "moveUp":
                    result = GameBoard.moveUp(take_action[0])
                elif directionToMove == "moveDown":
                    result = GameBoard.moveDown(take_action[0])                                 
                elif directionToMove == "moveLeft":
                    result = GameBoard.moveLeft(take_action[0])
                elif directionToMove == "moveRight":
                    result = GameBoard.moveRight(take_action[0])
                if result[0] != False:
                    playerMoved = True
                take_action = []
            elif take_action[0] == "heal":
                result = GameBoard.heal(take_action[1])
                if result[0] != False:
                    playerMoved = True
                    heal_button = "button"
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
                            clock.tick(8)
                            frame += 1
                        frame = 0
                    elif result[2] == "vaccine": 
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
                print(result)
                if result[0] != False:
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

            if GameBoard.num_zombies() == 0:
                print("You won! Your score is: " + str(GameBoard.total_score()))
                break
            if GameBoard.num_humans() == 0:
                print("You lost!")
                break


        # Update the display
        pygame.display.update()

    # AI Algorithm        
    else:             
        #pygame.time.wait(AI_PLAY_WAITTIME_MS)        
        i = 0
        r = rd.uniform(0.0, 1.0)
        st = rd.randint(0, len(GameBoard.States) - 1)
        state = GameBoard.QTable[st]
        randomization = False

        # Chooses random action - exploration
        if r < gamma:            
            randomization = True
            while True:
                st = rd.randint(0, len(GameBoard.States) - 1)
                state = GameBoard.QTable[st]                    
                # Chooses best action - exploitation
                action_to_take_id = GameBoard.choose_action(st, -1)
                action_to_take = ACTION_SPACE[action_to_take_id]
                b = GameBoard.QTable[st][action_to_take_id]
                posmoves = GameBoard.get_possible_moves(action_to_take, "Government")
                curcoords = GameBoard.toCoord(st)
                coordtuple = []
                coordlist = []
                healnotkill = False
                if action_to_take == "moveup":
                    coordtuple = GameBoard.moveUpCoords(curcoords)
                elif action_to_take == "movedown":
                    coordtuple = GameBoard.moveDownCoords(curcoords)
                elif action_to_take == "moveleft":
                    coordtuple = GameBoard.moveLeftCoords(curcoords)
                elif action_to_take == "moveright":
                    coordtuple = GameBoard.moveRightCoords(curcoords)
                elif action_to_take == "heal":
                    coordlist = GameBoard.healCoords(curcoords)
                    healnotkill = True
                elif action_to_take == "kill":
                    coordlist = GameBoard.killCoords(curcoords)
                   #print(coordlist[2] in posmoves)
                #print(coordlist[0])
                
                if(not GameBoard.States[st].person is None) and (not GameBoard.States[st].person.isZombie):
                    if healnotkill:
                        if (not bool(coordtuple) or coordtuple in posmoves) and (not bool(coordlist) or (coordlist[0] in posmoves or coordlist[1] in posmoves or coordlist[2] in posmoves or coordlist[3] in posmoves or coordlist[4] in posmoves)):
                            break
                        elif (not bool(coordtuple) or coordtuple in posmoves) and (not bool(coordlist) or (coordlist[0] in posmoves or coordlist[1] in posmoves or coordlist[2] in posmoves or coordlist[3] in posmoves)):
                            break
                else:
                    reward = 0
                    GameBoard.QTable[st][action_to_take_id] = GameBoard.QTable[st][action_to_take_id] + alpha * (reward) - GameBoard.QTable[st][action_to_take_id]

        else:
            biggest = None
            for x in range(len(GameBoard.States)):
                arr = GameBoard.QTable[x]
                exp = sum(arr) / len(arr)
                if biggest is None:
                    biggest = exp
                    i = x
                elif biggest < exp and player_role == "Government":
                    biggest = exp
                    i = x
            state = GameBoard.QTable[i]
            b = GameBoard.QTable[i][0]
            j = 0
            ind = 0
            for v in state:
                if j == 5:
                    continue
                elif v >= b and player_role == "Government":
                    b = v
                    ind = j
                elif v < b and player_role != "Government":
                    b = v
                    ind = j
                j += 1
            action_to_take = ACTION_SPACE[ind] #actual action e.g. cure bite etc
            moveIndex = ind
            b = GameBoard.QTable[i][j]
        
        print("AI's current action: " + str(action_to_take))        
        old_qval = b #updates old q-val
        if randomization == True:
            old_state = st
        else:
            old_state = i
        
        # Update
        # Q(S, A) = Q(S, A) + alpha[R + gamma * max_a Q(S', A) - Q(S, A)]
        reward = GameBoard.act(old_state, action_to_take)
        ns = reward[1] #what state (0-35)
        if GameBoard.num_zombies() == 1 or GameBoard.num_zombies == 0:
            reward[0] = 1000
        #UPDATE 
        statecor = GameBoard.toCoord(ns)
        print("AI's action coord: " + str(statecor))
        if action_to_take == "moveUp":
            GameBoard.moveUp(statecor)
        elif action_to_take == "moveDown":
            GameBoard.moveDown(statecor)
        elif action_to_take == "moveLeft":
            GameBoard.moveLeft(statecor)
        elif action_to_take == "moveRight":
            GameBoard.moveRight(statecor)
        elif action_to_take == "bite":
            GameBoard.bite(statecor)
        elif action_to_take == "heal":
            GameBoard.heal(statecor)
        elif action_to_take == "kill":
            GameBoard.kill(statecor)
                
        #In case of error
        if (ns > 35 or ns < 0):
            GameBoard.population = 0
            GameBoard.populate()
            print(GameBoard.QTable)
            print("Game ended due to invalid move")
            print("\n\n\n\n\n\n")
        else:
            NewStateAct = GameBoard.QGreedyat(ns) # action_index, qvalue
            NS = GameBoard.QTable[ns][NewStateAct[0]] #state, action_index
            
            #Update QTable
            GameBoard.QTable[old_state][moveIndex] = GameBoard.QTable[old_state][moveIndex] + alpha * (reward[0] + gamma * NS - GameBoard.QTable[old_state][moveIndex]) 
            #GameBoard.QTable[i] = GameBoard.QTable[i] + alpha * (reward[0] + gamma * NS - GameBoard.QTable[i])

            if GameBoard.num_zombies() == 0:
                print("Humans Win!")            
                # reset people
                GameBoard.clean_board()
                GameBoard.populate() 
                print(GameBoard.QTable)
                print("\n\n\n\n\n\n")

            # Zombies turn
            take_action = []        
            GameBoard.zombie_random_move()
            GameBoard.update()


            if GameBoard.num_humans() == 0:
                print("Zombies Win")
                # reset people
                GameBoard.clean_board()
                GameBoard.populate()
                print(GameBoard.QTable)
                print("\n\n\n\n\n\n")   

            for event in P:
                if event.type == pygame.QUIT:
                    running = False
                    break
                    
            # Update the display
            pygame.display.update()    

            print("\n")        
