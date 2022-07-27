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
AI_PLAY_WAITTIME_MS = 300

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
            if event.type == pygame.MOUSEBUTTONUP:
                x, y = pygame.mouse.get_pos()
                action = PF.get_action(GameBoard, x, y)                     # returns move if the thing pressed is a human game piece
                if HealButton.collidepoint(pygame.mouse.get_pos()):         # if heal button is clicked, action is heal and updates UI to show selected healbutton
                    take_action.append("heal")
                    heal_button = "select"
                    if len(take_action) > 1:
                        if take_action[0] == take_action[1]:
                            heal_button = "button"                          # if heal button is pressed again, turns heal button back to normal
                            take_action = []
                elif KillButton.collidepoint(pygame.mouse.get_pos()):       # if kill button is clicked, action is kill and updates UI to show selected kill button
                    take_action.append("kill")
                    kill_button = "select"
                    if len(take_action) > 1:
                        if take_action[0] == take_action[1]:
                            kill_button = "button"                          # if kill button is pressed again, turns kill button back to normal
                            take_action = []
                elif action != None:                                        # Otherwise, get the coordinate of a valid grid cell that was clicked
                    idx = GameBoard.toIndex(action)                         # Get the corresponding 1D index from the 2D grid location that was clicked
                    if take_action == []:                                   # Check that the click corresponds to an intention to move a player
                        # Returns true if the space is not empty and it is a piece belonging to the player.
                        if ( (GameBoard.States[idx].person is not None) and (GameBoard.States[idx].person.isZombie == roleToRoleBoolean[player_role]) ):
                            take_action.append("move")
                    if take_action != []:                                   # Only append a coordinate if there is a pending "heal" or "move" intention
                        take_action.append(action)
                        if len(take_action) > 2:
                            if take_action[1] == take_action[2]:
                                take_action = []
            elif event.type == pygame.MOUSEBUTTONDOWN:                      # if mouse is pressed down
                if HealButton.collidepoint(pygame.mouse.get_pos()):         # if press down happens over heal button, update heal button image
                    heal_button = "press"
                if KillButton.collidepoint(pygame.mouse.get_pos()):         # if press down happens over kill button, update kill button image
                    kill_button = "press"
            elif event.type == pygame.MOUSEMOTION: 
                if heal_button != "select":
                    if HealButton.collidepoint(pygame.mouse.get_pos()):
                        heal_button = "hover"
                    else:
                        heal_button = "button"
                if kill_button != "select":
                    if KillButton.collidepoint(pygame.mouse.get_pos()) and kill_button != "select":
                        kill_button = "hover"
                    else:
                        kill_button = "button"
            if event.type == pygame.QUIT:
                running = False
        # Display the current action
        PF.screen.blit(
            font.render("Your move is currently:", True, PF.WHITE),
            (800, 400),
        )
        PF.screen.blit(font.render(f"{take_action}", True, PF.WHITE), (800, 450))

        # Draws selection box
        if len(take_action) == 2:
            PF.select(take_action[1])
        # Action handling
        if len(take_action) > 1:
            if take_action[0] == "move":
                if len(take_action) > 2:                                    #Makes sure the second coordinate is clicked
                    directionToMove = PF.direction(take_action[1], take_action[2])
                    result = [False, None]
                    if directionToMove == "moveUp":
                        result = GameBoard.moveUp(take_action[1])
                    elif directionToMove == "moveDown":
                        result = GameBoard.moveDown(take_action[1])                                 
                    elif directionToMove == "moveLeft":
                        result = GameBoard.moveLeft(take_action[1])
                    elif directionToMove == "moveRight":
                        result = GameBoard.moveRight(take_action[1])
                    if result[0] != False:
                        playerMoved = True
                    take_action = []
            elif take_action[0] == "heal":
                result = GameBoard.heal(take_action[1])
                if result[0] != False:
                    playerMoved = True
                    heal_button = "button"                                  # turns heal button back to normal
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
                result = GameBoard.kill(take_action[1])
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
            
            if player_role == "Government":
                GameBoard.zombie_random_move()
            else:
                # Make a list of all possible actions that the computer can take
                # This huge chunk is only for AI as government, might not be worth it to keep since we will be training a smarter AI
                possible_actions = [
                    ACTION_SPACE[i]
                    for i in range(6)
                    if (i != 4 and player_role == "Government") or (i != 5 and player_role == "Zombie")
                ]
                
                # Figure out all possible moves and select an action
                possible_move_coords = []
                while len(possible_move_coords) == 0 and len(possible_actions) != 0:
                    action = rd.choice(possible_actions)
                    possible_move_coords = GameBoard.get_possible_moves(action, "Government" if player_role == "Zombie" else "Zombie")
                    possible_actions.remove(action)
                
                # No valid moves, player wins
                if len(possible_actions) == 0 and len(possible_move_coords) == 0:
                    PF.display_win_screen()
                    running = False
                    continue
                
                # Select the destination coordinates
                move_coord = rd.choice(possible_move_coords)
                
                # Implement the selected action
                if action == "moveUp":
                    GameBoard.moveUp(move_coord)
                elif action == "moveDown":
                    GameBoard.moveDown(move_coord)
                elif action == "moveLeft":
                    GameBoard.moveLeft(move_coord)
                elif action == "moveRight":
                    GameBoard.moveRight(move_coord)
                elif action == "bite":
                    GameBoard.bite(move_coord)
                elif action == "heal":
                    GameBoard.heal(move_coord)
                elif action == "kill":
                    GameBoard.kill(move_coord)
            
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
        pygame.time.wait(AI_PLAY_WAITTIME_MS)        
        i = 0
        r = rd.uniform(0.0, 1.0)
        st = rd.randint(0, len(GameBoard.States) - 1)
        state = GameBoard.QTable[st]
        randomization = False

        # Chooses random action - exploration
        if r < gamma:            
            randomization = True
            while GameBoard.States[st].person is None:
                st = rd.randint(0, len(GameBoard.States) - 1)
                state = GameBoard.QTable[st]                    

        # Chooses best action - exploitation
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
                elif biggest > exp and player_role != "Government":
                    biggest = exp
                    i = x
            state = GameBoard.QTable[i]
            
        b = -1000
        j = 0
        ind = 0
        for v in state:
            if v >= b and player_role == "Government":
                b = v
                ind = j
            elif v < b and player_role != "Government":
                b = v
                ind = j
            j += 1
        action_to_take = ACTION_SPACE[ind] #actual action e.g. cure bite etc
        
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
            reward[0] = 10000
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
            GameBoard.QTable[old_state][NewStateAct[0]] = GameBoard.QTable[old_state][NewStateAct[0]] + alpha * (reward[0] + gamma * NS) - GameBoard.QTable[old_state][NewStateAct[0]]            

            #GameBoard.QTable[i] = GameBoard.QTable[i] + alpha * (reward[0] + gamma * NS) - GameBoard.QTable[i]

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
