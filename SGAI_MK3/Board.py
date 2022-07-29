import random as rd
import numpy as np
from Person import Person
from copy import deepcopy

MOVE_ACTIONS = ["move_up", "move_down", "move_left", "move_right"]
MOVE_COORDS = [(1, 0), (-1, 0), (0, -1), (0, 1)]

# CONSISTENT COORDINATE SYSTEM, (rows, columns) so "move_up" increases row
# Dont think of this as (x, y), it's (rows, columns)

class Action:
    def __init__(self, player, act, row, col):
        self.player = player
        self.act = act
        self.row = row
        self.col = col

    def __eq__(self, other):
        return self.player == other.player and self.act == other.act and self.row == other.row and self.col == other.col
    
    def __hash__(self):
        return hash((self.player, self.act, self.row, self.col))

    def __str__(self):
        return self.act + " " + str((self.row, self.col))

class Board:
    def __init__(self, hospital=True, board=None):
        self.current_player = 1
        self.rows = 6
        self.columns = 6                        
        self.hasHospital = hospital
        self.player_turn = 1  # 1 is government, -1 is zombie
        self.states = np.ndarray((self.rows, self.columns), dtype=Person)
        self.num_humans = 0
        self.num_zombies = 4
        for r in range(self.rows):
            for c in range(self.columns):
                self.states[r][c] = None            
        self.populate()        

    def isValidCoordinate(self, row, col):
        return (
            row < self.rows
            and row >= 0
            and col < self.columns
            and col >= 0 )

    def isAdjacentTo(self, row, col, is_zombie):
        for i in range(4):            
            if (
                self.isValidCoordinate(row+MOVE_COORDS[i][0], col+MOVE_COORDS[i][1])
                and self.states[row+MOVE_COORDS[i][0]][col+MOVE_COORDS[i][1]] is not None
                and not self.states[row+MOVE_COORDS[i][0]][col+MOVE_COORDS[i][1]].isStunned
                and self.states[row+MOVE_COORDS[i][0]][col+MOVE_COORDS[i][1]].isZombie == is_zombie
            ):
                return True                                            
        return False

    def getCurrentPlayer(self):
        return self.current_player

    def getPossibleActions(self):
        ret = []

        is_zombie = self.current_player != 1
        for i in range(4):
            for index, val in np.ndenumerate(self.states):
                if val is not None and val.isZombie == is_zombie:                    
                    if self.isValidCoordinate(index[0]+MOVE_COORDS[i][0], index[1]+MOVE_COORDS[i][1]):
                        ret.append(Action(self.current_player, MOVE_ACTIONS[i], index[0], index[1]))        

        if self.player_turn == 1:
            for row in range(self.rows):
                for col in range(self.columns):
                    if self.states[row][col] is not None and self.states[row][col].isZombie:
                        if self.isAdjacentTo(row, col, False):                        
                            ret.append(Action(self.current_player, "kill", row, col))

            for row in range(self.rows):
                for col in range(self.columns):
                    if self.states[row][col] is not None and not self.states[row][col].isVaccinated:
                        if self.isAdjacentTo(row, col, False):                      
                            ret.append(Action(self.current_player, "heal", row, col))
        else:
            for row in range(self.rows):
                for col in range(self.columns):
                    if self.states[row][col] is not None and not self.states[row][col].isZombie:
                        if self.isAdjacentTo(row, col, True):
                            ret.append(Action(self.current_player, "bite", row, col))

        return ret

    def takeAction(self, action):
        new_board = deepcopy(self)
        if new_board.current_player == -1:
            new_board.update_effects()
        new_board.current_player *= -1
        
        if action.act == "move_up":
            new_board.moveUp(action.row, action.col)
        elif action.act == "move_down":
            new_board.moveDown(action.row, action.col)
        elif action.act == "move_left":
            new_board.moveLeft(action.row, action.col)
        elif action.act == "move_right":
            new_board.moveRight(action.row, action.col)
        elif action.act == "kill":
            new_board.auto_kill(action.row, action.col)
        elif action.act == "heal":
            new_board.auto_heal(action.row, action.col)
        elif action.act == "bite":
            new_board.auto_bite(action.row, action.col)

        return new_board

    def isTerminal(self):
        return self.num_humans == 0 or self.num_zombies == 0

    def getReward(self):
        return self.num_humans - self.num_zombies

    def __str__(self):
        ret = ""
        for row in self.states:
            for p in row:
                if p is None: ret += "."
                elif p.isZombie:
                    if p.halfCured: ret += "h"
                    else: ret += "z"
                else:
                    if p.isVaccinated: ret += "v"
                    else: ret += "p"
            ret += "\n"
        return ret                              

    def move(self, row, col, nrow, ncol):                
        if not self.isValidCoordinate(nrow, ncol):
            return False                
        if self.states[nrow][ncol] is None:
            self.states[nrow][ncol] = deepcopy(self.states[row][col])
            self.states[row][col] = None
            return True
        return False        

    def moveUp(self, row, col):        
        return self.move(row, col, row+1, col)    
    def moveDown(self, row, col):        
        return self.move(row, col, row-1, col)
    def moveLeft(self, row, col):        
        return self.move(row, col, row, col-1)    
    def moveRight(self, row, col):        
        return self.move(row, col, row, col+1)

#############

# Functions for AI that are quicker

    def auto_bite(self, row, col):                         
        chance = 100
        if self.states[row][col].isVaccinated:
            chance = 0
        elif self.states[row][col].wasVaccinated != self.states[row][col].wasCured:
            chance = 75
        elif self.states[row][col].wasVaccinated and self.states[row][col].wasCured:
            chance = 50
        r = rd.randint(0, 100)
        if r < chance:            
            self.states[row][col] = Person(True)
            self.num_humans -= 1
            self.num_zombies += 1        

    def auto_heal(self, row, col):                                
        if self.states[row][col].isZombie:                                    
            if self.states[row][col].halfCured == False and (self.states[row][col].isInHospital((row, col)) == False or self.hasHospital == False):
                self.states[row][col].halfCured = True
                self.states[row][col].isStunned = True                              
            elif (self.states[row][col].halfCured == True or (self.states[row][col].isInHospital((row, col)) == True and self.hasHospital == True)):
                self.states[row][col] = Person(False)                
                self.states[row][col].wasCured = True
                self.num_zombies -= 1
                self.num_humans += 1                          
        else:            
            self.states[row][col].isVaccinated = True            

    def auto_kill(self, row, col):                                
        self.states[row][col] = None
        self.num_zombies -= 1            

#############

    def bite(self, row, col):                
        if self.states[row][col] is None:
            return False

        chance = 100
        if self.states[row][col].isVaccinated:
            chance = 0
        elif self.states[row][col].wasVaccinated != self.states[row][col].wasCured:
            chance = 75
        elif self.states[row][col].wasVaccinated and self.states[row][col].wasCured:
            chance = 50
        r = rd.randint(0, 100)
        if r < chance:            
            self.states[row][col] = Person(True)
            self.num_humans -= 1
            self.num_zombies += 1
        return True

    def heal(self, row, col):                
        if self.states[row][col] is None:            
            return (False, None)
        
        if self.states[row][col].isZombie:
            # If not adjacent to a human, then we cannot cure the zombie
            if not self.isAdjacentTo(row, col, False):                                
                return (False, None)
            # Was the zombie already half-cured?
            if self.states[row][col].halfCured == False and (not self.hasHospital or not self.is_in_hospital(row, col)):
                self.states[row][col].halfCured = True
                self.states[row][col].isStunned = True
                return (True, "half" )               
            elif (self.states[row][col].halfCured == True or (self.hasHospital and self.is_in_hospital(row, col))):
                self.states[row][col] = Person(False)                
                self.states[row][col].wasCured = True
                self.num_zombies -= 1
                self.num_humans += 1
                return (True, "full")                           
        else:
            # If the person is already vaccinated, don't make the player lose a turn
            if self.states[row][col].isVaccinated:
                return (False, None)            
            self.states[row][col].isVaccinated = True
            return (True, "vaccine")

    def kill(self, row, col):        
        # Ensures we cannot kill empty spaces or humans, only zombies        
        if self.states[row][col] is None or not self.states[row][col].isZombie:            
            return False
        # If not adjacent to a human, then we cannot kill the zombie
        if not self.isAdjacentTo(row, col, False):            
            return False
        
        self.states[row][col] = None
        self.num_zombies -= 1
        return True

    def get_possible_human_targets(self):
        coords = []
        for r in range(self.rows):
            for c in range(self.columns):
                if (
                    self.states[r][c] is not None 
                    and not self.states[r][c].isZombie
                    and not self.isAdjacentTo(r, c, True)
                ):                    
                    coords.append((r, c))            
        return coords

    def is_in_hospital(self, row, col):
        return row < 3 and col < 3

    def get_possible_zombies_to_move(self):
        coords = []        
        for r in range(self.rows):
            for c in range(self.columns):                            
                if (
                    self.states[r][c] is not None 
                    and self.states[r][c].isZombie 
                    and not self.states[r][c].isStunned 
                    and not self.isAdjacentTo(r, c, False)
                ):
                    coords.append((r, c))    
        return coords        

    def clean_board(self):
        self.states = [[None for _ in range(self.columns)] for _ in range(self.rows)]

    def populate(self):
        self.num_humans = rd.randint(7, 11)
        for _ in range(self.num_humans):
            r = rd.randint(0, self.rows-1)
            c = rd.randint(0, self.columns-1)
            while self.states[r][c] is not None:
                r = rd.randint(0, self.rows-1)
                c = rd.randint(0, self.columns-1)
            self.states[r][c] = Person(False)
        
        for _ in range(self.num_zombies):
            r = rd.randint(0, self.rows-1)
            c = rd.randint(0, self.columns-1)
            while self.states[r][c] is not None:
                r = rd.randint(0, self.rows-1)
                c = rd.randint(0, self.columns-1)
            self.states[r][c] = Person(True)                

    # Dumb Zombie
    def zombie_random_move(self):        
        move_zombies = []
        possible_bite = []
        vaccine_bite = []
        
        for r in range(self.rows):
            for c in range(self.columns):
                if self.states[r][c] is not None:
                    if self.states[r][c].isZombie:
                        if not self.states[r][c].isStunned:
                            move_zombies.append((r, c))
                    elif self.isAdjacentTo(r, c, True):
                        if self.states[r][c].isVaccinated:
                            vaccine_bite.append((r, c))
                        else:
                            possible_bite.append((r, c))                

        action = "bite"
        cnt = 100
        has_moved = False

        if len(move_zombies) == 0 and len(possible_bite) == 0 and len(vaccine_bite) == 0:
            return

        while not has_moved and cnt > 0:
            r = rd.randint(0, 5)
            if (r < 4 or (len(possible_bite) == 0 and len(vaccine_bite) == 0)) and len(move_zombies) > 0: 
                action = rd.choice(MOVE_ACTIONS)                
            else:
                action = "bite"
            
            coord = rd.choice(move_zombies)            
            if action == "bite":
                bite_coord = rd.choice(possible_bite) if len(possible_bite) > 0 else rd.choice(vaccine_bite)
                has_moved = self.bite(bite_coord[0], bite_coord[1])
            elif action == "move_up":
                has_moved = self.moveUp(coord[0], coord[1])                
            elif action == "move_down":
                has_moved = self.moveDown(coord[0], coord[1])                                
            elif action == "move_left":
                has_moved = self.moveLeft(coord[0], coord[1])                    
            elif action == "move_right":
                has_moved = self.moveRight(coord[0], coord[1])                

            cnt -= 1

        self.current_player *= -1

    # Zombie AI logic
    def zombie_move(self):
        # First check if any zombie can bite

        list_return = []
        possible_bite = []        
        vaccine_bite = []
        for r in range(self.rows):
            for c in range(self.columns):
                p = self.states[r][c]            
                if (
                    p is not None 
                    and not p.isZombie
                    and self.isAdjacentTo(r, c, True)
                ):
                    if not p.isVaccinated: possible_bite.append((r, c))
                    else: vaccine_bite.append((r, c))
        
        if len(possible_bite) > 0:
            coord = rd.choice(possible_bite)
            self.bite(coord[0], coord[1])
            print("Zombie: Bite " + str(coord))
            list_return.append("bite")
        else:            
            # No zombies can bite, move the zombie that is nearest to a person.
            # Get all coordinates
            human_coords = self.get_possible_human_targets()
            zombie_coords = self.get_possible_zombies_to_move()
            min_dist = 9999999
            selected_human, selected_zombie = (-1, -1), (-1, -1)

            # Find the zombie and human with minimum move distance
            for human in human_coords:
                for zombie in zombie_coords:
                    dist = abs(human[0] - zombie[0]) + abs(human[1] - zombie[1])
                    if dist < min_dist and dist > 1: # if distance is 1, then the person can already be bitten, so let's move another zombie
                        min_dist = dist
                        selected_human, selected_zombie = human, zombie
            
            # If not moving is the best option, then move a random zombie not threatening a person
            if selected_zombie == (-1, -1): 
                bored_zombies = [] # Zombies not adjacent to a person
                for r in range(self.rows):
                    for c in range(self.columns):                                
                        state = self.states[r][c]
                        if state is not None and state.isZombie and not state.isStunned:                            
                            if not self.isAdjacentTo(r, c, False):
                                bored_zombies.append((r, c))

                if len(bored_zombies) > 0:                    
                    # Repeat until a valid move is found
                    has_moved = False
                    count = 10
                    while len(bored_zombies) > 0 and not has_moved and count > 0:                    
                        zombie = rd.choice(bored_zombies)
                        action = rd.choice(["move_up", "move_down", "move_left", "move_right"])
                        if action == "moveUp":
                            has_moved = self.moveUp(zombie[0], zombie[1])
                        elif action == "moveDown":
                            has_moved = self.moveDown(zombie[0], zombie[1])
                        elif action == "moveLeft":
                            has_moved = self.moveLeft(zombie[0], zombie[1])
                        elif action == "moveRight":
                            has_moved = self.moveRight(zombie[0], zombie[1])

                        # If we tried so many times and there's still not a valid move, there probably just isn't any,
                        # perhaps because all the zombies are surrounded by vaccinated humans. In that case, we don't
                        # want the loop to keep running and crash the game.
                        count -= 1                 
                    
                    print("Zombie: Random Move")

            else: 
                diff_y = selected_human[0] - selected_zombie[0]
                diff_x = selected_human[1] - selected_zombie[1]
                
                print("Zombie: Move " + str(selected_zombie))

                # Top Left corner is (0, 0)
                if abs(diff_y) > abs(diff_x):
                    if diff_y > 0: self.moveDown(selected_zombie[0], selected_zombie[1])
                    else: self.moveUp(selected_zombie[0], selected_zombie[1])
                else:
                    if diff_x > 0: self.moveRight(selected_zombie[0], selected_zombie[1])
                    else: self.moveLeft(selected_zombie[0], selected_zombie[1])
        
        self.current_player *= -1
        return list_return    

    def update_effects(self):        
        # Update effects of vaccination and stun
        for r in range(self.rows):
            for c in range(self.columns):
                if self.states[r][c] is not None:
                    if self.states[r][c].isStunned: self.states[r][c].isStunned = False                
                    if self.states[r][c].isVaccinated:
                        self.states[r][c].turnsVaccinated += 1
                        if self.states[r][c].turnsVaccinated >= 5: # Vaccine Duration = 5 turns
                            self.states[r][c].turnsVaccinated = 0
                            self.states[r][c].isVaccinated = False
                            self.states[r][c].wasVaccinated = True        
        
