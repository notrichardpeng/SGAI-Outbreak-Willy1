import gym
import numpy as np
from gym import spaces
from typing import Optional
from gym.utils.renderer import Renderer

import Board

INVALID_ACTION_REWARD = -10
VALID_ACTION_REWARD = 10
WIN_REWARD = 100
LOSS_REWARD = -100
ACTION_SPACE = ["move_up", "move_down", "move_left", "move_right", "heal", "kill"]

class OutbreakEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array", "single_rgb_array"], "render_fps": 30}

    def __init__(self, render_mode: Optional[str] = None, size: int = 6):
        self.render_mode = render_mode
        self.size = size
        self.window_size = 1024
        self.max_moves = 100
        self.board = Board((size, size), 150, (100,100), False)

        self.observation_space = spaces.Box(-1, 1, (size, size), dtype=int)

        # up, left, down, right, heal, kill
        self.action_space = spaces.Discrete(size * size * 6)        

        if self.render_mode == "human":
            import pygame

            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode((self.window_size, self.window_size))
            self.clock = pygame.time.Clock()

        self.renderer = Renderer(self.render_mode, self._render_frame)

    def _get_info():
        return "abc"        

    def reset(self, seed=None, return_info=False, options=None):        
        super().reset(seed=seed)

        self.board = Board((self.ize, self.size), 150, (100,100), False)
        self.board.populate()         
        
        self.renderer.reset()
        self.renderer.render_step()    
        
        return self.board

    def player_move(self, action):
        move = ACTION_SPACE[action]
        
    
    def zombie_move(self, action):


    def step(self, action):
        assert action , "ACTION ERROR {}".format(action)

        if self.move_count >= self.max_moves:
            return (self.board, 0.0, True, self.info)
        
        # AI Move

        reward = 0
        move_reward = self.player_move(action)
        reward += move_reward        

        if self.board.num_zombies() == 0:
            reward += WIN_REWARD
            self.done = True
            return self.board, reward, self.done, self._get_info()

        # Zombies move

        self.board, move_reward, self.done = self.zombie_move()
        if self.board.num_humans() == 0:
            reward += LOSS_REWARD
            self.done = True
            return self.board, reward, self.done, self._get_info()

        self.board.update_effects()
        self.move_count += 1

        return self.board, reward, self.done, self._get_info()

    