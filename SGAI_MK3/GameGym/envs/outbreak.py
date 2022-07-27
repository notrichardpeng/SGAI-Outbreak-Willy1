from re import I
import gym
from gym import spaces
import numpy as np
from typing import Optional
from gym.utils.renderer import Renderer

INVALID_ACTION_REWARD = -10
VALID_ACTION_REWARD = -10
WIN_REWARD = 100
LOSS_REWARD = -100


class OutbreakEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array", "single_rgb_array"], "render_fps": 30}

    def __init__(self, render_mode: Optional[str] = None, size: int = 6):
        self.render_mode = render_mode
        self.size = size
        self.window_size = 1024
        self.max_moves = 100

        self.observation_space = spaces.Box(-1, 1, (size, size), dtype=int)

        # up, left, down, right, heal, kill
        self.action_space = spaces.Discrete(size * size * 6)

        self._action_to_direction = {
            0: np.array([1, 0]),
            1: np.array([0, 1]),
            2: np.array([-1, 0]),
            3: np.array([0, -1]),
        }

        if self.render_mode == "human":
            import pygame

            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode((self.window_size, self.window_size))
            self.clock = pygame.time.Clock()

        self.renderer = Renderer(self.render_mode, self._render_frame)



    def reset(self, seed=None, return_info=False, options=None):        
        super().reset(seed=seed)

        self.states = np.zeros(shape=(self.size*self.size))

        total_human = self.np_random.integers(7, 10, size=1)
        for _ in range(total_human):
            r = self.np_random.integers(0, self.size-1, size=1)
            while self.states[r] != 0: r = self.np_random.integers(0, self.size-1, size=1)
            self.states[r] = 1
        
        for _ in range(4):
            r = self.np_random.integers(0, self.size-1, size=1)
            while self.states[r] != 0: r = self.np_random.integers(0, self.size-1, size=1)
            self.states[r] = -1        
        
        self.renderer.reset()
        self.renderer.render_step()    
        
        return self.states

    def step(self, action):
        if self.move_count >= self.max_moves:
            return (self.state, 0.0, True, self.info)
        
        reward = INVALID_ACTION_REWARD
        self.state, move_reward, self.done = self.player_move(action)

        # Zombies move
        

    