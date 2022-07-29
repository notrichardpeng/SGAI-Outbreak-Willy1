class DataCollector:
    def __init__(self, hospital=False):
        self.hospital = hospital
        self.reset()

    def reset(self):
        self.zombies_killed = 0
        self.zombies_cured = 0
        self.zombies_cured_in_hospital = 0
        self.human_vaccinated = 0
        self.turns_taken = 0
        self.humans_remaining = 0

    def save_player_data(self):
        with open("previous_game_data.txt", "w") as f:
            lines = [
                "Has hospital: " + str(self.hospital) + "\n",
                "Zombies killed: " + str(self.zombies_killed) + "\n",
                "Zombies cured: " + str(self.zombies_cured) + "\n",
                "Zombies cured in hospital: " + str(self.zombies_cured_in_hospital) + "\n",
                "Humans vaccinated: " + str(self.human_vaccinated) + "\n",
                "Humans remaining: " + str(self.humans_remaining) + + "\n",
                "Number of turns taken: " + str(self.turns_taken) + + "\n"
            ]
            f.writelines(lines)

    def save_ai_data(self):
        pass
