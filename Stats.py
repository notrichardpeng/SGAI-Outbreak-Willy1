import matplotlib.pyplot as plt
import numpy as np
from DataCollector import DataCollector

class Stats:
    def __init__(self):
        print("stat method")

    def loadData(self, filename):
        try:
            file1 = open(filename, "r") 

            line = file1.readline()
            x = line.split(": ")
            winner = (x[1])
            #print(winner)

            line = file1.readline()
            x = line.split(": ")
            DataCollector.hospital = x[1]
            #print(DataCollector.hospital)

            line = file1.readline()
            x = line.split(": ")
            DataCollector.zombies_killed = int(x[1])
            #print(DataCollector.zombies_killed)

            line = file1.readline()
            x = line.split(": ")
            DataCollector.zombies_cured= int(x[1])
            #print(DataCollector.zombies_cured)

            line = file1.readline()
            x = line.split(": ")
            DataCollector.zombies_cured_in_hospital = int(x[1])
            #print(DataCollector.zombies_cured_in_hospital)

            line = file1.readline()
            x = line.split(": ")
            DataCollector.humans_vaccinated = int(x[1])
            #print(DataCollector.humans_vaccinated)

            line = file1.readline()
            x = line.split(": ")
            DataCollector.humans_remaining = int(x[1])
            #print(DataCollector.humans_remaining)

            line = file1.readline()
            x = line.split(": ")
            DataCollector.humans_infected = int(x[1])
            #print(DataCollector.humans_infected)

            line = file1.readline()
            x = line.split(": ")
            DataCollector.turns_taken = int(x[1])
            #print(DataCollector.turns_taken)

            file1.close()
        except:
            print("Data File Issue: File not found or file format invalid")

    def calculatePercents(self):

        total_zombie_interaction = DataCollector.zombies_killed + DataCollector.zombies_cured
        timesZombiesCured = 0
        timesZombiesKilled = 0
        if total_zombie_interaction != 0:
            timesZombiesCured = (DataCollector.zombies_cured / total_zombie_interaction) * 100
            timesZombiesKilled = (DataCollector.zombies_killed / total_zombie_interaction) * 100
        else:
            print("No Data to Plot")

        return timesZombiesCured, timesZombiesKilled


    def ethicsChart(self):
        plt.clf()

        x = ["Yes Hospital", "No Hospital"]
        y_cured = [0,0]
        y_killed = [0,0]

        # load self play hospital data
        self.loadData("SelfPlayData_Hospital.txt")
        values = self.calculatePercents()
        y_cured[0] = values[0]
        y_killed[0] = values[1]
        DataCollector.reset_data()

        # load self play no hospital data
        self.loadData("SelfPlayData_NoHospital.txt")
        values = self.calculatePercents()
        y_cured[1] = values[0]
        y_killed[1] = values[1]
        DataCollector.reset_data()

        plt.bar(x, y_killed, 0.5, label='Percent of Turns Killing Zombies', color='r')
        plt.bar(x, y_cured, 0.5, bottom=y_killed, label='Percent of Turns Curing Zombies', color='b')

        plt.title("Decisions made")
        plt.xlabel("Whether there was a hospital on the board")
        plt.ylabel("Percent of turns interacting with zombies")
        plt.legend(["Killed", "Cured"])
        plt.show()



