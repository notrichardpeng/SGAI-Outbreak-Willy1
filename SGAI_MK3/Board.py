import random as rd
from Person import Person

from copy import deepcopy

VACCINE_DURATION = 5
MOVE_ACTIONS = ["move_up", "move_down", "move_left", "move_right"]
UTIL_ACTIONS = ["heal", "kill"]
ROWS = 6
COLUMNS = 6
BORDER = 150                    # Number of pixels to offset grid to the top-left side
CELL_DIMENSIONS = (100,100)     # Number of pixels (x,y) for each cell
HAS_HOSPITAL = True

class Board:
    def __init__(self, board=None):
        if board is not None:
            self.__dict__ = deepcopy(board.__dict__)
            self.player_turn *= -1
        else:
            self.rows = ROWS
            self.columns = COLUMNS
            self.display_border = BORDER
            self.display_cell_dimensions = CELL_DIMENSIONS
            self.hasHospital = HAS_HOSPITAL
            self.states = [[None for _ in range(COLUMNS)] for _ in range(ROWS)]
            self.player_turn = 1  # 1 is government, -1 is zombie
            self.populate()

    def __str__(self):
        ret = ""
        for row in self.rows:
            for p in row:
                if p is None: ret += "."
                elif p.isZombie:
                    if p.halfCured: ret += "h"
                    else: ret += "z"
                else:
                    if p.isVaccinated: ret += "v"
                    else: ret += "p"
        return ret
    
    def num_humans(self):
        ret = 0
        for row in self.states:
            for person in row:
                if person is not None and not person.isZombie:
                    ret += 1
        return ret

    def num_zombies(self):
        ret = 0
        for row in self.states:
            for person in row:
                if person is not None and person.isZombie:
                    ret += 1
        return ret                

    def isValidCoordinate(self, coordinates):
        return (
            coordinates[0] < self.rows
            and coordinates[0] >= 0
            and coordinates[1] < self.columns
            and coordinates[1] >= 0 )     

    def isAdjacentTo(self, coord, is_zombie: bool):        
        vals = [
            (coord[0], coord[1] + 1),
            (coord[0], coord[1] - 1),
            (coord[0] + 1, coord[1]),
            (coord[0] - 1, coord[1]),
        ]
        for coord in vals:
            if (
                self.isValidCoordinate(coord)
                and self.states[coord[0]][coord[1]] is not None
                and not self.states[coord[0]][coord[1]].isStunned
                and self.states[coord[0]][coord[1]].isZombie == is_zombie
            ):
                return True

        return False

    def move(self, from_coords, new_coords):
        """
        Check if the move is valid.
        If valid, then implement the move and return [True, destination_idx]
        If invalid, then return [False, None]
        If the space is currently occupied, then return [False, destination_idx]
        """
        # Check if the new coordinates are valid
        if not self.isValidCoordinate(new_coords):
            return False
        
        # Check if the destination is currently occupied
        if self.states[new_coords[0]][new_coords[1]] is None:
            self.states[new_coords[0]][new_coords[1]] = deepcopy(self.states[from_coords[0]][from_coords[1]])
            del self.states[from_coords[0]][from_coords[1]]
            return True

        return False        

    def moveUp(self, coords):
        new_coords = (coords[0], coords[1] - 1)
        return self.move(coords, new_coords)

    def moveDown(self, coords):
        new_coords = (coords[0], coords[1] + 1)
        return self.move(coords, new_coords)

    def moveLeft(self, coords):
        new_coords = (coords[0] - 1, coords[1])
        return self.move(coords, new_coords)

    def moveRight(self, coords):
        new_coords = (coords[0] + 1, coords[1])
        return self.move(coords, new_coords)   

    def bite(self, coords):
        i = self.toIndex(coords)
        if self.states[i] is None:
            return False
        chance = 100
        p = self.states[i].person
        if p.isVaccinated:
            chance = 0
        elif p.wasVaccinated != p.wasCured:
            chance = 75
        elif p.wasVaccinated and p.wasCured:
            chance = 50
        r = rd.randint(0, 100)
        if r < chance:            
            self.states[i].person = Person(True)
        return [True, i]

    def heal(self, coords):                
        if self.states[coords[0]][coords[1]] is None:
            return False

        p = self.states[coords[0]][coords[1]]

        if p.isZombie:
            # If not adjacent to a human, then we cannot cure the zombie
            if not self.isAdjacentTo(coords, False):
                print("Invalid Move! Can only heal zombies adjacent to humans.")           
                return False
            # Was the zombie already half-cured?
            if p.halfCured == False and (p.isInHospital(coords) == False or self.hasHospital == False):
                p.halfCured = True
                p.isStunned = True                
            elif (p.halfCured == True or (p.isInHospital(coords) == True and self.hasHospital == True)):
                p.isZombie = False
                p.wasCured = True                              
        else:
            # If the person is already vaccinated, don't make the player lose a turn
            if p.isVaccinated:
                return False
            p.isVaccinated = True                        
            
        return True

    def kill(self, coords):        
        # Ensures we cannot kill empty spaces or humans, only zombies
        if self.states[coords[0]][[coords[1]]] is None or self.states[coords[0]][[coords[1]]].person.isZombie == False:
            return False
        # If not adjacent to a human, then we cannot kill the zombie
        if not self.isAdjacentTo(coords, False):
            print("Invalid Moves! Can only kill zombies adjacent to humans.")
            return False
        
        del self.states[coords[0]][coords[1]]
        return True

    def get_possible_human_targets(self):
        coords = []
        i = 0
        for state in self.states:
            c = self.toCoord(i)
            if (
                state.person is not None 
                and not state.person.isZombie
                and not self.isAdjacentTo(c, True)
            ):
                coords.append(c)
            i += 1
        return coords

    def get_possible_zombies_to_move(self):
        coords = []
        i = 0
        for state in self.states:
            c = self.toCoord(i)
            if (state.person is not None 
                and state.person.isZombie 
                and not state.person.isStunned 
                and not self.isAdjacentTo(c, False)
                ):
                coords.append(c)
            i += 1
        return coords        

    def populate(self):
        total_human = rd.randint(7, 11)
        for _ in range(total_human):
            r = rd.randint(0, self.rows-1)
            c = rd.randint(0, self.columns-1)
            while self.states[r][c] is not None:
                r = rd.randint(0, self.rows-1)
                c = rd.randint(0, self.columns-1)
            self.states[r][c] = Person(False)
        
        for _ in range(4):
            r = rd.randint(0, self.rows-1)
            c = rd.randint(0, self.columns-1)
            while self.states[r][c] is not None:
                r = rd.randint(0, self.rows-1)
                c = rd.randint(0, self.columns-1)
            self.states[r][c] = Person(True)

    # Zombie AI logic TODO: Fix skipping turns
    def zombie_move(self):
        # First check if any zombie can bite
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

        if len(possible_bite) > 0:
            coord = rd.choice(possible_bite)
            self.bite(coord)
            print("Zombie: Bite " + str(coord))
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
                busy_zombies = []  # Zombies adjacent to a person
                for i in range(len(self.states)):
                    state = self.states[i]
                    if state.person is not None and state.person.isZombie and not state.person.isStunned:
                        c = self.toCoord(i)
                        if not self.isAdjacentTo(c, False):
                            bored_zombies.append(c)
                        else:
                            busy_zombies.append(c)

                if len(bored_zombies) == 0:
                    bored_zombies = busy_zombies
                
                # Repeat until a valid move is found
                has_moved = False
                count = 5
                while len(bored_zombies) > 0 and not has_moved and count > 0:                    
                    zombie = rd.choice(bored_zombies)
                    action = rd.choice(MOVE_ACTIONS)                    
                    if action == "moveUp":
                        has_moved = self.moveUp(zombie)[0]
                    elif action == "moveDown":
                        has_moved = self.moveDown(zombie)[0]
                    elif action == "moveLeft":
                        has_moved = self.moveLeft(zombie)[0]
                    elif action == "moveRight":
                        has_moved = self.moveRight(zombie)[0]

                    # If we tried so many times and there's still not a valid move, there probably just isn't any,
                    # perhaps because all the zombies are surrounded by vaccinated humans. In that case, we don't
                    # want the loop to keep running and crash the game.
                    count -= 1 

            else: 
                diff_x = selected_human[0] - selected_zombie[0]
                diff_y = selected_human[1] - selected_zombie[1]
                
                print("Zombie: Move " + str(selected_zombie))

                # Top Left corner is (0, 0)
                if abs(diff_y) > abs(diff_x):
                    if diff_y > 0: self.moveDown(selected_zombie)
                    else: self.moveUp(selected_zombie)
                else:
                    if diff_x > 0: self.moveRight(selected_zombie)
                    else: self.moveLeft(selected_zombie)

    def update(self):
        if self.base_score > 100: self.base_score -= 25 # Winning the game quicker means higher score

        # Update effects of vaccination and stun
        for state in self.states:
            if state.person is not None:
                if state.person.isStunned: state.person.isStunned = False                
                if state.person.isVaccinated:
                    state.person.turnsVaccinated += 1
                    if state.person.turnsVaccinated >= VACCINE_DURATION:
                        state.person.turnsVaccinated = 0
                        state.person.isVaccinated = False
                        state.person.wasVaccinated = True

    def make_move(self, action, row, col):
        board = Board(self)

        match action:
            case "move_up":
                if board.moveUp((row, col)): return (True, board)
            case "move_down":
                if board.moveDown((row, col)): return (True, board)
            case "move_left":
                if board.moveLeft((row, col)): return (True, board)
            case "move_right":
                if board.moveRight((row, col)): return (True, board)
            case "kill":
                if board.kill((row, col)): return (True, board)
            case "heal":
                if board.heal((row, col)): return (True, board)

        return (False, None)


    def generate_states(self):
        new_states = []

        for action in MOVE_ACTIONS:
            for row in range(self.rows):
                for col in range(self.columns):
                    if self.states[row][col] is not None and not self.states[row][col].isZombie:
                        result = self.make_move(action, row, col)
                        if result[0]: new_states.append(result[1])

        for row in range(self.rows):
            for col in range(self.columns):
                if self.states[row][col] is not None and self.states[row][col].isZombie:
                    result = self.make_move("kill", row, col)
                    if result[0]: new_states.append(result[1])

        for row in range(self.rows):
            for col in range(self.columns):
                if self.states[row][col] is not None and not self.states[row][col].isVaccinated:
                    result = self.make_move("heal", row, col)
                    if result[0]: new_states.append(result[1])
        
        return new_states
