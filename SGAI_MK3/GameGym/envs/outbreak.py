import gym
from gym import spaces
import numpy as np
from typing import Optional
from gym.utils.renderer import Renderer

class OutbreakEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array", "single_rgb_array"], "render_fps": 30}

    def __init__(self, render_mode: Optional[str] = None, size: int = 6):
        self.render_mode = render_mode
        self.size = size
        self.window_size = 1024

        self.observation_space = spaces.Box(-1, 1, (size, size))

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
        # We need the following line to seed self.np_random
        super().reset(seed=seed)

        

        # Choose the agent's location uniformly at random
        self._agent_location = self.np_random.integers(0, self.size, size=2)

        # We will sample the target's location randomly until it does not coincide with the agent's location
        self._target_location = self._agent_location
        while np.array_equal(self._target_location, self._agent_location):
            self._target_location = self.np_random.integers(0, self.size, size=2)

        # clean the render collection and add the initial frame
        self.renderer.reset()
        self.renderer.render_step()

        observation = self._get_obs()
        info = self._get_info()
        return (observation, info) if return_info else observation