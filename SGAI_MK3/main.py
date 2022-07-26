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
while running:
    P = PF.run(GameBoard, hospital)
    if self_play:        
        # Event a
        for event in P:
            if event.type == pygame.MOUSEBUTTONUP:
                x, y = pygame.mouse.get_pos()
                action = PF.get_action(GameBoard, x, y)                     # Can only return "heal", coordinate of grid clicked, or None. 
                if action == "heal":                                        # Process a "heal" intention if take_action is currently empty
                    if take_action == []:
                        take_action.append("heal")
                elif action == "kill":                                        # Process a "heal" intention if take_action is currently empty
                    if take_action == []:
                        take_action.append("kill")
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
                if len(take_action) > 2:        #Makes sure the second coordinate is clicked
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
                take_action = []
            elif take_action[0] == "kill":
                result = GameBoard.kill(take_action[1])
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
            
            if player_role == "Government":
                GameBoard.zombie_move()
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
    else:
        if epochs_ran % 20 == 0:
            print("Board Reset!")
            GameBoard = Original_Board  # reset environment        
        pygame.time.wait(AI_PLAY_WAITTIME_MS)        
        i = 0
        r = rd.uniform(0.0, 1.0)
        st = rd.randint(0, len(GameBoard.States) - 1)
        state = GameBoard.QTable[st]
        randomization = False
        if r < gamma:
            #print("random!!!")
            randomization = True
            while GameBoard.States[st].person is None:
                st = rd.randint(0, len(GameBoard.States) - 1)
                state = GameBoard.QTable[st]
                    #print(st)
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
            #print(state)
        b = 0
        j = 0
        ind = 0
        for v in state:
            if v > b and player_role == "Government":
                b = v
                ind = j
            elif v < b and player_role != "Government":
                b = v
                ind = j
            j += 1
        action_to_take = ACTION_SPACE[ind] #actual action e.g. cure bite etc
        print(state)
        print(action_to_take)
        old_qval = b #updates old q-val
        if randomization == True:
            old_state = st
        else:
            old_state = i
        
        # Update
        # Q(S, A) = Q(S, A) + alpha[R + gamma * max_a Q(S', A) - Q(S, A)]
        reward = GameBoard.act(old_state, action_to_take)
        ns = reward[1] #what state (0-35)
        if GameBoard.num_zombies() is 1 or GameBoard.num_zombies is 0:
            reward[0] = 10000
        #UPDATE 
        statecor = GameBoard.toCoord(ns)
        print(statecor)
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
        #pygame.display.update()
        NewStateAct = GameBoard.QGreedyat(ns) # action_index, qvalue
        NS = GameBoard.QTable[ns][NewStateAct[0]] #state, action_index
        #qtable
        GameBoard.QTable[old_state][NewStateAct[0]] = GameBoard.QTable[old_state][NewStateAct[0]] + alpha * (reward[0] + gamma * NS) - GameBoard.QTable[old_state][NewStateAct[0]]
        print(GameBoard.QTable[old_state][NewStateAct[0]])

        #GameBoard.QTable[i] = GameBoard.QTable[i] + alpha * (reward[0] + gamma * NS) - GameBoard.QTable[i]
        if GameBoard.num_zombies() == 0:
            print("winCase")
            GameBoard = Original_Board
            break

        take_action = []
        print("Enemy turn")
        ta = ""
        if player_role == "Government":
            GameBoard.zombie_move()
            GameBoard.update()
        else:
            r = rd.randint(0, 4)
            ta = ACTION_SPACE[r]
            poss = GameBoard.get_possible_moves(ta, "Zombie")        
            if len(poss) > 0:
                r = rd.randint(0, len(poss) - 1)
                a = poss[r]
                if ta == "moveUp":
                    GameBoard.moveUp(a)
                elif ta == "moveDown":
                    GameBoard.moveDown(a)
                elif ta == "moveLeft":
                    GameBoard.moveLeft(a)
                elif ta == "moveRight":
                    GameBoard.moveRight(a)
                elif ta == "bite":
                    GameBoard.bite(a)
                elif ta == "heal":
                    GameBoard.heal(a)
                elif ta == "kill":
                    GameBoard.kill(a)
        print(GameBoard.num_zombies())
        print(GameBoard.population)
        print(GameBoard.num_humans())
        if GameBoard.num_humans() is 0:
            print("loseCase")
            break
        for event in P:
            if event.type == pygame.QUIT:
                running = False
                break 
                
        # Update the display
        pygame.display.update()
        epochs_ran += 1
