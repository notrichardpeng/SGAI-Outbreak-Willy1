import matplotlib.pyplot as plt
import numpy as np
import pickle
from MCTS import *

class Stats:
    def __init__(self):
        self.mcts = MCTS()
        self.total_runs = 0

    def rewardsChart(self):
        with open("mcts.pickle", "r") as f:
            pickle.dump(self.mcts, f)

        x = np.array(["A", "B", "C", "D"])
        y = np.array([3, 8, 1, 10])

        plt.bar(x,y)
        plt.show()