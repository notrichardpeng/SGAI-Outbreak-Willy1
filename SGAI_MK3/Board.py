import random as rd
from Person import Person

from copy import deepcopy

VACCINE_DURATION = 5
MOVE_ACTIONS = ["moveUp", "moveDown", "moveLeft", "moveRight"]
ROWS = 6
COLUMNS = 6
BORDER = 150                    # Number of pixels to offset grid to the top-left side
CELL_DIMENSIONS = (100,100)     # Number of pixels (x,y) for each cell
HAS_HOSPITAL = True

class Board:
    def __init__(self, board=None):
        if board is not None:
            self.__dict__ = deepcopy(board.__dict__)
        else:
            self.rows = ROWS
            self.columns = COLUMNS
            self.display_border = BORDER
            self.display_cell_dimensions = CELL_DIMENSIONS
            self.hasHospital = HAS_HOSPITAL
            self.states = [[None for _ in range(COLUMNS)] for _ in range(ROWS)]
            self.populate()
    
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
            and coordinates[1] >= 0
        )

    def isAdjacentTo(self, coord, is_zombie: bool) -> bool:
        ret = False
        vals = [
            (coord[0], coord[1] + 1),
            (coord[0], coord[1] - 1),
            (coord[0] + 1, coord[1]),
            (coord[0] - 1, coord[1]),
        ]
        for coord in vals:
            if (
                self.isValidCoordinate(coord)
                and self.states[self.toIndex(coord)].person is not None
                and not self.states[self.toIndex(coord)].person.isStunned
                and self.states[self.toIndex(coord)].person.isZombie == is_zombie
            ):
                ret = True
                break

        return ret

    def move(self, from_coords, new_coords):
        """
        Check if the move is valid.
        If valid, then implement the move and return [True, destination_idx]
        If invalid, then return [False, None]
        If the space is currently occupied, then return [False, destination_idx]
        """
        # Check if the new coordinates are valid
        if not self.isValidCoordinate(new_coords):
            return [False, self.toIndex(from_coords)]
        
        # Get the start and destination index (1D)
        start_idx = self.toIndex(from_coords)
        destination_idx = self.toIndex(new_coords)                
        
        # Check if the destination is currently occupied
        if self.states[destination_idx].person is None:
            self.states[destination_idx].person = self.states[start_idx].person
            self.states[start_idx].person = None
            return [True, destination_idx]
        return [False, destination_idx]

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
        """
        Heals the person at the stated coordinates
        If no person is selected, then return [False, None]
        if a person is vaccined, then return [True, index]
        """
        i = self.toIndex(coords)
        if self.states[i].person is None:
            return [False, None]
        p = self.states[i].person        
        action_type = ""
        if p.isZombie:
            # If not adjacent to a human, then we cannot cure the zombie
            if not self.isAdjacentTo(self.toCoord(i), False):     
                print("Invalid Move! Can only heal zombies adjacent to humans.")           
                return [False, None]
            # Was the zombie already half-cured?
            if p.halfCured == False and (p.isInHospital(coords) == False or self.hasHospital == False):
                p.halfCured = True
                p.isStunned = True
                action_type = "half"
            elif (p.halfCured == True or (p.isInHospital(coords) == True and self.hasHospital == True)):
                p.isZombie = False
                p.wasCured = True
                action_type = "full"                
        elif p.isZombie == False:
            # If the person is already vaccinated, don't make the player lose a turn
            if p.isVaccinated:
                return [False, None]
            p.isVaccinated = True   
            action_type = "vaccine"         
        return [True, i, action_type]

    def kill(self, coords):
        i = self.toIndex(coords)
        # Ensures we cannot kill empty spaces or humans, only zombies
        if self.states[i].person is None or self.states[i].person.isZombie == False:
            return [False, None]
        # If not adjacent to a human, then we cannot kill the zombie
        if not self.isAdjacentTo(self.toCoord(i), False):
            print("Invalid Moves! Can only kill zombies adjacent to humans.")
            return [False, None]  
        p = self.states[i].person
        newP = p.clone()
        # Gets rid of zombie
        if newP.isZombie:
            newP = None
        self.states[i].person = newP
        return [True, i]

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

    #Zombie AI logic
    def zombie_move(self):
        # First check if any zombie can bite
        possible_bite = []
        i = 0
        for state in self.states:
            if (
                state is not None 
                and not state.person.isZombie
                and not state.person.isVaccinated 
                and self.isAdjacentTo(self.toCoord(i), True)
            ):
                possible_bite.append(self.toCoord(i))
            i += 1

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