class DataCollector:    

    hospital = False
    zombies_killed = 0
    zombies_cured = 0
    zombies_cured_in_hospital = 0
    human_vaccinated = 0
    turns_taken = 0
    humans_remaining = 0

    @staticmethod
    def reset():
        DataCollector.zombies_killed = 0
        DataCollector.zombies_cured = 0
        DataCollector.zombies_cured_in_hospital = 0
        DataCollector.human_vaccinated = 0
        DataCollector.turns_taken = 0
        DataCollector.humans_remaining = 0

    @staticmethod
    def save_player_data(self):
        with open("previous_game_data.txt", "w") as f:
            lines = [
                "Has hospital: " + str(self.hospital) + "\n",
                "Zombies killed: " + str(self.zombies_killed) + "\n",
                "Zombies cured: " + str(self.zombies_cured) + "\n",
                "Zombies cured in hospital: " + str(self.zombies_cured_in_hospital) + "\n",
                "Humans vaccinated: " + str(self.human_vaccinated) + "\n",
                "Humans remaining: " + str(self.humans_remaining) + "\n",
                "Number of turns taken: " + str(self.turns_taken) + "\n"
            ]
            f.writelines(lines)

    @staticmethod
    def save_ai_data(self):
        pass
