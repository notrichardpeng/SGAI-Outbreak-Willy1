import matplotlib.pyplot as plt
import numpy as np

class Stats:
    def __init__(self):
        self.total_runs = 0

    def rewardsChart(self):

        x = []
        y = []

        plt.bar(x,y)
        plt.title("Visits and Scores for MCTS")
        plt.xlabel("scores")
        plt.ylabel("visits")
        plt.show()