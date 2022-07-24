import pygame
from Board import Board
import PygameFunctions as PF
import random as rd 

# Constants
ROWS = 6
COLUMNS = 6
BORDER = 150                    # Number of pixels to offset grid to the top-left side
CELL_DIMENSIONS = (100,100)     # Number of pixels (x,y) for each cell
ACTION_SPACE = ["moveUp", "moveDown", "moveLeft", "moveRight", "heal", "bite"]
SELF_PLAY = True
AI_PLAY_WAITTIME_MS = 300

# Player role variables
player_role = "Government"      # Valid options are "Government" and "Zombie"
roleToRoleNum = {"Government": 1, "Zombie": -1}
roleToRoleBoolean = {"Government": False, "Zombie": True}       # False means Human, True means Zombie. Switching this would turn Humans to Zombies, and vice versa. 

#Create the game board
GameBoard = Board((ROWS,COLUMNS), BORDER, CELL_DIMENSIONS, roleToRoleNum[player_role])
GameBoard.populate()

# Self play variables
alpha = 0.1
gamma = 0.6
epsilon = 0.1
epochs = 1000
epochs_ran = 0
Original_Board = GameBoard.clone(GameBoard.States)

# Initialize variables
running = True
take_action = []
playerMoved = False
font = pygame.font.SysFont("Comic Sans", 20)
hospital = False

# Option menu
AIYesHosButton = pygame.Rect(150, 480, 400, 250)
AINoHosButton = pygame.Rect(500, 480, 400, 250)
govtButton = pygame.Rect(300, 300, 200, 100)
zomButton = pygame.Rect(650, 300, 200, 100)

proceed = False
while proceed == False:
    for event in pygame.event.get():
        PF.display_options_screen()
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if AIYesHosButton.collidepoint(pygame.mouse.get_pos()):
                SELF_PLAY = False
                hospital = True
                proceed = True
            elif AINoHosButton.collidepoint(pygame.mouse.get_pos()):
                SELF_PLAY = False
                hospital = False
                proceed = True
            elif govtButton.collidepoint(pygame.mouse.get_pos()):
                SELF_PLAY = True
                player_role = "Government"
                proceed = True
            elif zomButton.collidepoint(pygame.mouse.get_pos()):
                SELF_PLAY = True
                player_role = "Zombie"
                proceed = True
        elif event.type == pygame.QUIT:
            pygame.quit()


while running:
    P = PF.run(GameBoard, hospital)

    if SELF_PLAY:
        
        # Event Handling
        for event in P:
            if event.type == pygame.MOUSEBUTTONUP:
                x, y = pygame.mouse.get_pos()
                action = PF.get_action(GameBoard, x, y)                     # Can only return "heal", coordinate of grid clicked, or None. 
                if action == "heal":                                        # Process a "heal" intention if take_action is currently empty
                    if take_action == []:
                        take_action.append("heal")
                elif action != None:                                        # Otherwise, get the coordinate of a valid grid cell that was clicked
                    idx = GameBoard.toIndex(action)                         # Get the corresponding 1D index from the 2D grid location that was clicked
                    if take_action == []:                                   # Check that the click corresponds to an intention to move a player
                        # Returns true if the space is not empty and it is a piece belonging to the player.
                        if ( (GameBoard.States[idx].person is not None) and (GameBoard.States[idx].person.isZombie == roleToRoleBoolean[player_role]) ):
                            take_action.append("move")
                    if take_action != []:                                   # Only append a coordinate if there is a pending "heal" or "move" intention
                        take_action.append(action)
            if event.type == pygame.QUIT:
                running = False
        
        # Display the current action
        PF.screen.blit(
            font.render("Your move is currently:", True, PF.WHITE),
            (800, 400),
        )
        PF.screen.blit(font.render(f"{take_action}", True, PF.WHITE), (800, 450))

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

        # Update the display
        pygame.display.update()

    else:
        if epochs_ran % 100 == 0:
            print("Board Reset!")
            GameBoard = Original_Board  # reset environment        
        pygame.time.wait(AI_PLAY_WAITTIME_MS)        
        i = 0
        r = rd.uniform(0.0, 1.0)
        st = rd.randint(0, len(GameBoard.States) - 1)
        state = GameBoard.QTable[st]

        if r < gamma:
            while GameBoard.States[st].person is None:
                st = rd.randint(0, len(GameBoard.States) - 1)
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
        action_to_take = ACTION_SPACE[ind]
        old_qval = b
        old_state = i
        
        # Update
        # Q(S, A) = Q(S, A) + alpha[R + gamma * max_a Q(S', A) - Q(S, A)]
        reward = GameBoard.act(old_state, action_to_take)
        ns = reward[1]
        NewStateAct = GameBoard.QGreedyat(ns)
        NS = GameBoard.QTable[ns][NewStateAct[0]]
        #GameBoard.QTable[i] = GameBoard.QTable[i] + alpha * (reward[0] + gamma * NS) - GameBoard.QTable[i]
        if GameBoard.num_zombies() == 0:
            print("winCase")
            break

        take_action = []
        print("Enemy turn")
        ta = ""
        if player_role == "Government":
            GameBoard.zombie_move()
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

        if GameBoard.num_zombies() == GameBoard.population:
            print("loseCase")
            break
        for event in P:
            if event.type == pygame.QUIT:
                running = False
                break 
                
        # Update the display
        pygame.display.update()
