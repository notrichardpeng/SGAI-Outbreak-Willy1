import random as rd
import numpy as np
from Person import Person
from copy import deepcopy

class Board:
    def __init__(self, hospital=True, board=None):
        if board is not None:
            self.__dict__ = deepcopy(board.__dict__)
            self.player_turn *= -1
        else:
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

    def isValidCoordinate(self, coordinates):
        return (
            coordinates[0] < self.rows
            and coordinates[0] >= 0
            and coordinates[1] < self.columns
            and coordinates[1] >= 0 )     

    def isAdjacentTo(self, coord, is_zombie):        
        vals = [
            (coord[0], coord[1] + 1),
            (coord[0], coord[1] - 1),
            (coord[0] + 1, coord[1]),
            (coord[0] - 1, coord[1]),
        ]
        for c in vals:
            if (
                self.isValidCoordinate(c)
                and self.states[c[0]][c[1]] is not None
                and not self.states[c[0]][c[1]].isStunned
                and self.states[c[0]][c[1]].isZombie == is_zombie                
            ):
                return True                        
        return False

    def move(self, from_coords, new_coords):        
        # Check if the new coordinates are valid
        if not self.isValidCoordinate(new_coords):
            return False
        
        # Check if the destination is currently occupied
        if self.states[new_coords[0]][new_coords[1]] is None:
            self.states[new_coords[0]][new_coords[1]] = deepcopy(self.states[from_coords[0]][from_coords[1]])
            self.states[from_coords[0]][from_coords[1]] = None
            return True

        return False        

    def moveUp(self, coords):
        new_coords = (coords[0], coords[1] - 1)
        return self.move(coords, new_coords)
    def moveUpCoords(self, coords):
        return (coords[0], coords[1]-1)
    def moveDown(self, coords):
        new_coords = (coords[0], coords[1] + 1)
        return self.move(coords, new_coords)
    def moveDownCoords(self, coords):
        return (coords[0], coords[1] + 1)
    def moveLeft(self, coords):
        new_coords = (coords[0] - 1, coords[1])
        return self.move(coords, new_coords)
    def moveLeftCoords(self, coords):
        return (coords[0] - 1, coords[1])
    def moveRight(self, coords):
        new_coords = (coords[0] + 1, coords[1])
        return self.move(coords, new_coords)   

    def bite(self, coords):                
        if self.states[coords[0]][coords[1]] is None:
            return False

        chance = 100
        if self.states[coords[0]][coords[1]].isVaccinated:
            chance = 0
        elif self.states[coords[0]][coords[1]].wasVaccinated != self.states[coords[0]][coords[1]].wasCured:
            chance = 75
        elif self.states[coords[0]][coords[1]].wasVaccinated and self.states[coords[0]][coords[1]].wasCured:
            chance = 50
        r = rd.randint(0, 100)
        if r < chance:            
            self.states[coords[0]][coords[1]] = Person(True)
            self.num_humans -= 1
            self.num_zombies += 1
        return True

    def heal(self, coords):                
        if self.states[coords[0]][coords[1]] is None:            
            return (False, None)
        
        if self.states[coords[0]][coords[1]].isZombie:
            # If not adjacent to a human, then we cannot cure the zombie
            if not self.isAdjacentTo(coords, False):                                
                return (False, None)
            # Was the zombie already half-cured?
            if self.states[coords[0]][coords[1]].halfCured == False and (self.states[coords[0]][coords[1]].isInHospital(coords) == False or self.hasHospital == False):
                self.states[coords[0]][coords[1]].halfCured = True
                self.states[coords[0]][coords[1]].isStunned = True
                return (True, "half" )               
            elif (self.states[coords[0]][coords[1]].halfCured == True or (self.states[coords[0]][coords[1]].isInHospital(coords) == True and self.hasHospital == True)):
                self.states[coords[0]][coords[1]] = Person(False)                
                self.states[coords[0]][coords[1]].wasCured = True
                self.num_zombies -= 1
                self.num_humans += 1
                return (True, "full")                           
        else:
            # If the person is already vaccinated, don't make the player lose a turn
            if self.states[coords[0]][coords[1]].isVaccinated:
                return (False, None)            
            self.states[coords[0]][coords[1]].isVaccinated = True
            return (True, "vaccine")


    def kill(self, coords):        
        # Ensures we cannot kill empty spaces or humans, only zombies        
        if self.states[coords[0]][coords[1]] is None or not self.states[coords[0]][coords[1]].isZombie:            
            return False
        # If not adjacent to a human, then we cannot kill the zombie
        if not self.isAdjacentTo(coords, False):            
            return False
        
        self.states[coords[0]][coords[1]] = None
        self.num_zombies -= 1
        return True

    def get_possible_human_targets(self):
        coords = []
        for r in range(self.rows):
            for c in range(self.columns):
                if (
                    self.states[r][c] is not None 
                    and not self.states[r][c].isZombie
                    and not self.isAdjacentTo((r, c), True)
                ):                    
                    coords.append((r, c))            
        return coords

    def get_possible_zombies_to_move(self):
        coords = []        
        for r in range(self.rows):
            for c in range(self.columns):                            
                if (
                    self.states[r][c] is not None 
                    and self.states[r][c].isZombie 
                    and not self.states[r][c].isStunned 
                    and not self.isAdjacentTo((r, c), False)
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
                    and self.isAdjacentTo((r, c), True)
                ):
                    if not p.isVaccinated: possible_bite.append((r, c))
                    else: vaccine_bite.append((r, c))

        board = Board(board=self)

        if len(possible_bite) > 0:
            coord = rd.choice(possible_bite)
            board.bite(coord)
            print("Zombie: Bite " + str(coord))
            list_return.append("bite")
        else:            
            # No zombies can bite, move the zombie that is nearest to a person.
            # Get all coordinates
            human_coords = board.get_possible_human_targets()
            zombie_coords = board.get_possible_zombies_to_move()
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
                for r in range(board.rows):
                    for c in range(board.columns):                                
                        state = board.states[r][c]
                        if state is not None and state.isZombie and not state.isStunned:                            
                            if not board.isAdjacentTo((r, c), False):
                                bored_zombies.append((r, c))

                if len(bored_zombies) > 0:                    
                    # Repeat until a valid move is found
                    has_moved = False
                    count = 10
                    while len(bored_zombies) > 0 and not has_moved and count > 0:                    
                        zombie = rd.choice(bored_zombies)
                        action = rd.choice(["move_up", "move_down", "move_left", "move_right"])                    
                        if action == "moveUp":
                            has_moved = board.moveUp(zombie)
                        elif action == "moveDown":
                            has_moved = board.moveDown(zombie)
                        elif action == "moveLeft":
                            has_moved = board.moveLeft(zombie)
                        elif action == "moveRight":
                            has_moved = board.moveRight(zombie)

                        # If we tried so many times and there's still not a valid move, there probably just isn't any,
                        # perhaps because all the zombies are surrounded by vaccinated humans. In that case, we don't
                        # want the loop to keep running and crash the game.
                        count -= 1                 
                    
                    print("Zombie: Random Move")

            else: 
                diff_x = selected_human[0] - selected_zombie[0]
                diff_y = selected_human[1] - selected_zombie[1]
                
                print("Zombie: Move " + str(selected_zombie))

                # Top Left corner is (0, 0)
                if abs(diff_y) > abs(diff_x):
                    if diff_y > 0: board.moveDown(selected_zombie)
                    else: board.moveUp(selected_zombie)
                else:
                    if diff_x > 0: board.moveRight(selected_zombie)
                    else: board.moveLeft(selected_zombie)
        list_return = [board] + list_return    
        return list_return

    # Dumb Zombie AI
    def zombie_random_move(self):
        possible_move_coords = []
        all_zombies = []
        vulnerable_humans = []
        
        for r in range(self.rows):
            for c in range(self.columns):
                if self.states[r][c] is not None and self.states[r][c].isZombie:
                    all_zombies.append((r, c))
        
        for r in range(self.rows):
            for c in range(self.columns):
                p = self.states[r][c]
                if p is not None and not p.isZombie and not p.isVaccinated and self.isAdjacentTo((r, c), True):
                    vulnerable_humans.append((r, c))            

        action = "bite"
        cnt = 30
        has_moved = False

        board = Board(board=self)
        while not has_moved and cnt > 0:
            r = rd.randint(0, 5)
            if r < 4: 
                action = ["move_up", "move_down", "move_left", "move_right"][r]
            else: 
                action = "bite"
            
            coord = rd.choice(all_zombies)
            bite_coord = rd.choice(vulnerable_humans) if len(vulnerable_humans) > 0 else (-1, -1)
            if action == "bite" and bite_coord != (-1, -1):
                has_moved = self.bite(bite_coord)                
            elif action == "moveUp":
                has_moved = self.moveUp(coord)                
            elif action == "moveDown":
                has_moved = self.moveDown(coord)                
            elif action == "moveLeft":
                has_moved = self.moveLeft(coord)                
            elif action == "moveRight":
                has_moved = self.moveRight(coord)                

            cnt -= 1

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

    def make_move(self, action, row, col):
        board = Board(board=self)

        if action == "move_up":
            if board.moveUp((row, col)): return (True, board)        
        elif action == "move_down":
            if board.moveDown((row, col)): return (True, board)
        elif action == "move_left":
            if board.moveLeft((row, col)): return (True, board)
        elif action == "move_right":
            if board.moveRight((row, col)): return (True, board)
        elif action == "kill":                
            if board.kill((row, col)): return (True, board)
        elif action == "heal":
            if board.heal((row, col))[0]: return (True, board)
        elif action == "bite":
            if board.bite((row, col)): return (True, board)        
            

        return (False, None)

    def gov_gen_states(self):
        new_states = []

        for action in ["move_up", "move_down", "move_left", "move_right"]:
            for row in range(self.rows):
                for col in range(self.columns):
                    if self.states[row][col] is not None and not self.states[row][col].isZombie:
                        result = self.make_move(action, row, col)
                        if result[0]: new_states.append(result[1])

        for row in range(self.rows):
            for col in range(self.columns):
                if self.states[row][col] is not None and self.states[row][col].isZombie:
                    result = self.make_move("kill", row, col)
                    if result[0]: 
                        new_states.append(result[1])                        

        for row in range(self.rows):
            for col in range(self.columns):
                if self.states[row][col] is not None:
                    result = self.make_move("heal", row, col)
                    if result[0]: 
                        new_states.append(result[1])                               

        return new_states

    def zombie_gen_states(self):
        new_states = []

        for action in ["move_up", "move_down", "move_left", "move_right"]:
            for row in range(self.rows):
                for col in range(self.columns):
                    if self.states[row][col] is not None and self.states[row][col].isZombie:
                        result = self.make_move(action, row, col)
                        if result[0]: new_states.append(result[1])

        for row in range(self.rows):
            for col in range(self.columns):
                if self.states[row][col] is not None and not self.states[row][col].isZombie:
                    result = self.make_move("bite", row, col)
                    if result[0]: new_states.append(result[1])
                
        return new_states

    def generate_states(self):
        if self.player_turn == 1:
            return self.gov_gen_states()
        else:
            return self.zombie_gen_states()
        
