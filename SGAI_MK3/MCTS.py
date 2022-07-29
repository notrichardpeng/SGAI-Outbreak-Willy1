# Monte Carlo Tree Search

import math
import random

class TreeNode():    
    def __init__(self, board, parent):        
        self.board = board
        
        # init is node terminal flag
        if self.board.num_humans() == 0 or self.board.num_zombies() == 0:
            self.is_terminal = True                
        else:            
            self.is_terminal = False
                
        self.is_fully_expanded = self.is_terminal
        self.parent = parent                
        self.visits = 0                
        self.score = 0                
        self.children = []

# MCTS class definition
class MCTS():

    def __init__(self):
        self.tree = {}

    # search for the best move in the current position
    def search(self, initial_state):
        # create root node        
        encoded = str(initial_state)        
        if encoded not in self.tree.keys():
            self.tree[encoded] = TreeNode(initial_state, None)        
        
        for _ in range(100):
            node = self.select(self.tree[encoded])
            score = self.rollout(node.board)
            self.backpropagate(node, score)
                
        return self.get_best_move(self.tree[encoded], 0)        
    
    def select(self, node):        
        while not node.is_terminal:            
            if node.is_fully_expanded:
                node = self.get_best_move(node, 2)                        
            else:
                # otherwise expand the node
                return self.expand(node)
               
        return node
    
    # expand node
    def expand(self, node):
        # generate legal states (moves) for the given node
        next_states = node.board.generate_states()
        
        # loop over generated states (moves)
        for state in next_states:
            # make sure that current state (move) is not present in child nodes
            new_encoded = str(state)
            if new_encoded not in node.children:
                # create a new node
                if new_encoded not in self.tree.keys():
                    self.tree[new_encoded] = TreeNode(state, node)                                    
                
                node.children.append(new_encoded)
                
                # case when node is fully expanded
                if len(next_states) == len(node.children):
                    node.is_fully_expanded = True                                

                # return newly created node
                return self.tree[new_encoded]

        print("?????")
    
    # simulate the game via making random moves until reach end of the game
    def rollout(self, board):
        # make random moves for both sides until terminal state of the game is reached        
        while board.num_humans() > 0 and board.num_zombies() > 0:
            board = random.choice(board.generate_states())            
        
        return board.num_humans() - board.num_zombies()        
                
    # backpropagate the number of visits and score up to the root node
    def backpropagate(self, node, score):
        # update nodes's up to root node
        while node is not None:
            # update node's visits
            node.visits += 1
            
            # update node's score
            node.score += score
            
            # set node to parent
            node = node.parent
    
    # select the best node basing on UCB1 formula
    def get_best_move(self, node, exploration_constant):        
        best_score = float('-inf')
        best_moves = []
        
        # loop over child nodes
        for child_code in node.children:                        
            
            child_node = self.tree[child_code]                        
            move_score = node.board.player_turn * child_node.score / child_node.visits + exploration_constant * math.sqrt(math.log(node.visits) / child_node.visits)
            
            if move_score > best_score:
                best_score = move_score
                best_moves = [child_node]
            elif move_score == best_score:
                best_moves.append(child_node)
            
        # return one of the best moves randomly
        return random.choice(best_moves)



























