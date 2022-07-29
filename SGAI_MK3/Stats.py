import matplotlib.pyplot as plt
import numpy as np
import pickle
from MCTS import *

class Stats:
    def __init__(self):
        self.mcts = MCTS()
        self.total_runs = 0

    def rewardsChart(self):
        try:
            with open("mcts.pickle", "rb") as f:
                self.mcts = pickle.load(f)
        except:
            pass

        x = []
        y = []
        for k in self.mcts.tree.keys():
            node = self.mcts.tree[k]
            x.append(node.score)
            y.append(node.visits)

        plt.bar(x,y)
        plt.title("Visits and Scores for MCTS")
        plt.xlabel("scores")
        plt.ylabel("visits")
        plt.show()