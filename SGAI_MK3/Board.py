from tracemalloc import start
from State import State
import random as rd
from Person import Person

VACCINE_DURATION = 5
MOVE_ACTIONS = ["moveUp", "moveDown", "moveLeft", "moveRight"]

class Board:
    def __init__(self, dimensions, border, cell_dimensions, pr, h):
        self.rows = dimensions[0]
        self.columns = dimensions[1]
        self.display_border = border
        self.display_cell_dimensions = cell_dimensions
        self.Player_Role = pr
        self.hasHospital = h
        self.population = 0
        self.States = []
        self.QTable = []
        self.total_score = 0
        for s in range(dimensions[0] * dimensions[1]):
            self.States.append(State(None, s))
            self.QTable.append([0] * 6)

    def num_zombies(self):
        r = 0
        for state in self.States:
            if state.person != None:
                if state.person.isZombie:
                    r += 1
        return r

    def num_humans(self):
        r = 0
        for state in self.States:
            if state.person != None:
                if not state.person.isZombie:
                    r += 1
        return r
        
    def act(self, oldstate, givenAction):
        cell = self.toCoord(oldstate)
        f = []
        if givenAction == "moveUp":
            f = self.moveUp(cell)
        elif givenAction == "moveDown":
            f = self.moveDown(cell)
        elif givenAction == "moveLeft":
            f = self.moveLeft(cell)
        elif givenAction == "moveRight":
            f = self.moveRight(cell)
        elif givenAction == "heal":
            f = self.heal(cell)
        elif givenAction == "bite":
            f = self.bite(cell)
        elif givenAction == "kill":
            f = self.kill(cell)
        reward = self.States[oldstate].evaluate(givenAction, self)
        if f[0] == False:
            reward = -1000
        return [reward, f[1]]

    def get_possible_moves(self, action, role):
        """
        Get the coordinates of people (or zombies) that are able
        to make the specified move.
        @param action - the action to return possibilities for (options are 'bite', 'moveUp', 'moveDown','moveLeft', 'moveRight', and 'heal')
        @param role - either 'Zombie' or 'Government'; helps decide whether an action
        is valid and which people/zombies it applies to
        """
        poss = []
        B = self.clone(self.States)     #Clone a new board

        if role == "Zombie":
            for idx in range(len(self.States)):
                B.States = [self.States[i].clone() for i in range(len(self.States))]
                state = self.States[idx]
                if state.person is not None:
                    if action == "bite":
                        # if the current space isn't a zombie and it is adjacent to a space that is a zombie
                        if not state.person.isZombie and not state.person.isVaccinated and self.isAdjacentTo(
                            self.toCoord(idx), True
                        ):
                            poss.append(B.toCoord(state.location))
                    else:
                        if state.person.isZombie:
                            if action == "moveUp":
                                if B.moveUp(B.toCoord(state.location))[0]:
                                    poss.append(B.toCoord(state.location))
                            elif action == "moveDown":
                                if B.moveDown(B.toCoord(state.location))[0]:
                                    poss.append(B.toCoord(state.location))
                            elif action == "moveLeft":
                                if B.moveLeft(B.toCoord(state.location))[0]:
                                    poss.append(B.toCoord(state.location))
                            elif action == "moveRight":
                                if B.moveRight(B.toCoord(state.location))[0]:
                                    poss.append(B.toCoord(state.location))

        elif role == "Government":
            for state in self.States:
                if state.person != None:
                    if action == "heal":
                        if state.person.isZombie or state.person.isVaccinated == False:
                            poss.append(B.toCoord(state.location))
                    elif action == "kill":
                        if state.person.isZombie:
                            poss.append(B.toCoord(state.location))
                    else:
                        if state.person.isZombie:
                            if action == "moveUp":
                                if B.moveUp(B.toCoord(state.location)):
                                    poss.append(B.toCoord(state.location))
                            elif action == "moveDown":
                                if B.moveDown(B.toCoord(state.location)):
                                    poss.append(B.toCoord(state.location))
                            elif action == "moveLeft":
                                if B.moveLeft(B.toCoord(state.location)):
                                    poss.append(B.toCoord(state.location))
                            elif action == "moveRight":
                                if B.moveRight(B.toCoord(state.location)):
                                    poss.append(B.toCoord(state.location))
        return poss

    def toCoord(self, i):
        return (int(i % self.columns), int(i / self.rows))

    def toIndex(self, coordinates):
        return int(coordinates[1] * self.columns) + int(coordinates[0])

    def isValidCoordinate(self, coordinates):
        return (
            coordinates[1] < self.rows
            and coordinates[1] >= 0
            and coordinates[0] < self.columns
            and coordinates[0] >= 0
        )

    def clone(self, L: list):
        NB = Board((self.rows, self.columns), self.display_border, self.display_cell_dimensions, self.Player_Role, self.hasHospital)
        NB.States = L.copy()
        return NB

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
                and self.States[self.toIndex(coord)].person is not None
                and not self.States[self.toIndex(coord)].person.isStunned
                and self.States[self.toIndex(coord)].person.isZombie == is_zombie
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
        # Get the start and destination index (1D)
        start_idx = self.toIndex(from_coords)
        destination_idx = self.toIndex(new_coords)
        
        # Check if the new coordinates are valid
        if not self.isValidCoordinate(new_coords):
            return [False, destination_idx]
        
        # Check if the destination is currently occupied
        if self.States[destination_idx].person is None:
            self.States[destination_idx].person = self.States[start_idx].person
            self.States[start_idx].person = None
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

    def QGreedyat(self, state_id):
        biggest = self.QTable[state_id][0] * self.Player_Role
        ind = 0
        A = self.QTable[state_id]
        i = 0
        for qval in A:
            if (qval * self.Player_Role) > biggest:
                biggest = qval
                ind = i
            i += 1
        return [ind, self.QTable[ind]]  # action_index, qvalue

    def choose_action(self, state_id, lr):
        L = lr * 100
        r = rd.randint(0, 100)
        if r < L:
            return self.QGreedyat(state_id)
        else:
            if self.Player_Role == 1:  # Player is Govt
                d = rd.randint(0, 4)
            else:
                d = rd.randint(0, 5)
                while d != 4:
                    d = rd.randint(0, 4)
            return d

    def choose_state(self, lr):
        L = lr * 100
        r = rd.randint(0, 100)
        if r < L:
            biggest = None
            sid = None
            for x in range(len(self.States)):
                if self.States[x].person != None:
                    q = self.QGreedyat(x)
                    if biggest is None:
                        biggest = q[1]
                        sid = x
                    elif q[1] > biggest:
                        biggest = q[1]
                        sid = x
            return self.QGreedyat(sid)
        else:
            if self.Player_Role == -1:  # Player is Govt
                d = rd.randint(0, len(self.States))
                while self.States[d].person is None or self.States[d].person.isZombie:
                    d = rd.randint(0, len(self.States))
            else:
                d = rd.randint(0, len(self.States))
                while (
                    self.States[d].person is None
                    or self.States[d].person.isZombie == False
                ):
                    d = rd.randint(0, len(self.States))
            return d

    def bite(self, coords):
        i = self.toIndex(coords)
        if self.States[i] is None:
            return False
        chance = 100
        p = self.States[i].person
        if p.isVaccinated:
            chance = 0
        elif p.wasVaccinated != p.wasCured:
            chance = 75
        elif p.wasVaccinated and p.wasCured:
            chance = 50
        r = rd.randint(0, 100)
        if r < chance:            
            self.States[i].person = Person(True)
        return [True, i]

    def heal(self, coords):
        """
        Heals the person at the stated coordinates
        If no person is selected, then return [False, None]
        if a person is vaccined, then return [True, index]
        """
        i = self.toIndex(coords)
        if self.States[i].person is None:
            return [False, None]
        p = self.States[i].person        

        if p.isZombie:
            # If not adjacent to a human, then we cannot cure the zombie
            if not self.isAdjacentTo(self.toCoord(i), False):     
                print("Invalid Move! Can only heal zombies adjacent to humans.")           
                return [False, None]
            # Was the zombie already half-cured?
            if p.halfCured == False and (p.isInHospital(coords) == False or self.hasHospital == False):
                p.halfCured = True
                p.isStunned = True
            elif (p.halfCured == True or (p.isInHospital(coords) == True and self.hasHospital == True)):
                p.isZombie = False
                p.wasCured = True                
        elif p.isZombie == False:
            # If the person is already vaccinated, don't make the player lose a turn
            if p.isVaccinated:
                return [False, None]
            p.isVaccinated = True            
        return [True, i]

    def kill(self, coords):
        i = self.toIndex(coords)
        # Ensures we cannot kill empty spaces or humans, only zombies
        if self.States[i].person is None or self.States[i].person.isZombie == False:
            return [False, None]
        # If not adjacent to a human, then we cannot kill the zombie
        if not self.isAdjacentTo(self.toCoord(i), False):
            print("Invalid Moves! Can only kill zombies adjacent to humans.")
            return [False, None]  
        p = self.States[i].person
        newP = p.clone()
        # Gets rid of zombie
        if newP.isZombie:
            newP = None
        self.States[i].person = newP
        return [True, i]

    def get_possible_states(self, rn):
        indexes = []
        i = 0
        for state in self.States:
            if state.person != None and not state.person.isStunned:
                if rn == 1 and state.person.isZombie == False:
                    indexes.append(i)
                elif rn == -1 and state.person.isZombie:
                    indexes.append(i)
            i += 1
        return indexes

    def get_possible_human_targets(self):
        coords = []
        i = 0
        for state in self.States:
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
        for state in self.States:
            c = self.toCoord(i)
            if (state.person is not None 
                and state.person.isZombie 
                and not state.person.isStunned 
                and not self.isAdjacentTo(c, False)
                ):
                coords.append(c)
            i += 1
        return coords

    def step(self, role_number, learningRate):
        P = self.get_possible_states(role_number)
        r = rd.uniform(0, 1)
        if r < learningRate:
            rs = rd.randrange(0, len(self.States) - 1)
            if role_number == 1:
                while (
                    self.States[rs].person is not None
                    and self.States[rs].person.isZombie
                ):
                    rs = rd.randrange(0, len(self.States) - 1)
            else:
                while (
                    self.States[rs].person is not None
                    and self.States[rs].person.isZombie == False
                ):
                    rs = rd.randrange(0, len(self.States) - 1)

            # random state and value
        # old_value = QTable[state][acti]
        # next_max = np.max(QTable[next_state])
        # new_value = (1 - alpha) * old_value + alpha * (reward + gamma * next_max)
        # QTable[state][acti] = new_value

    def populate(self):
        total = rd.randint(7, ((self.rows * self.columns) / 3))
        poss = []
        for x in range(len(self.States)):
            r = rd.randint(0, 100)
            if r < 60 and self.population < total:
                p = Person(False)
                self.States[x].person = p
                self.population = self.population + 1
                poss.append(x)
            else:
                self.States[x].person = None
        used = []
        for x in range(4):
            s = rd.randint(0, len(poss) - 1)
            while s in used:
                s = rd.randint(0, len(poss) - 1)
            self.States[poss[s]].person.isZombie = True
            used.append(s)    

    #Zombie AI logic
    def zombie_move(self):
        # First check if any zombie can bite
        possible_move_coords = self.get_possible_moves("bite", "Zombie")
        if len(possible_move_coords) > 0:                
            coord = rd.choice(possible_move_coords)
            self.bite(coord)
            print("Bite " + str(coord))
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
                for i in range(len(self.States)):
                    state = self.States[i]
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
                
                print("Move " + str(selected_zombie))

                # Top Left corner is (0, 0)
                if abs(diff_y) > abs(diff_x):
                    if diff_y > 0: self.moveDown(selected_zombie)
                    else: self.moveUp(selected_zombie)
                else:
                    if diff_x > 0: self.moveRight(selected_zombie)
                    else: self.moveLeft(selected_zombie)

    def update_effects(self):        
        for state in self.States:
            if state.person is not None:
                if state.person.isStunned: state.person.isStunned = False                
                if state.person.isVaccinated:
                    state.person.turnsVaccinated += 1
                    if state.person.turnsVaccinated >= VACCINE_DURATION:
                        state.person.turnsVaccinated = 0
                        state.person.isVaccinated = False
                        state.person.wasVaccinated = True                

