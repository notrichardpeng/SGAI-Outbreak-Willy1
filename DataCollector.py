class DataCollector:    

    hospital = False
    zombies_killed = 0
    zombies_cured = 0
    zombies_cured_in_hospital = 0
    humans_vaccinated = 0
    humans_remaining = 0
    humans_infected = 0
    turns_taken = 0
    
    @staticmethod
    def reset_data():
        DataCollector.zombies_killed = 0
        DataCollector.zombies_cured = 0
        DataCollector.zombies_cured_in_hospital = 0
        DataCollector.humans_vaccinated = 0
        DataCollector.humans_remaining = 0
        DataCollector.humans_infected = 0
        DataCollector.turns_taken = 0

    @staticmethod
    def save_player_data(filename="previous_game_data.txt"):
        with open(filename, "w") as f:
            lines = [
                "Winner: " + ("Human" if DataCollector.humans_remaining > 0 else "Zombie") + "\n",
                "Has hospital: " + str(DataCollector.hospital) + "\n",
                "Zombies killed: " + str(DataCollector.zombies_killed) + "\n",
                "Zombies cured: " + str(DataCollector.zombies_cured) + "\n",
                "Zombies cured in hospital: " + str(DataCollector.zombies_cured_in_hospital) + "\n",
                "Humans vaccinated: " + str(DataCollector.humans_vaccinated) + "\n",
                "Humans remaining: " + str(DataCollector.humans_remaining) + "\n",
                "Humans infected: " + str(DataCollector.humans_infected) + "\n",
                "Number of turns taken: " + str(DataCollector.turns_taken) + "\n"
            ]
            f.writelines(lines)

    @staticmethod
    def clear_ai_data():
        with open("ai_games_data.txt", "w") as f:
            f.write("")

    @staticmethod
    def save_ai_data_of_one_game(game_number, filename="ai_games_data.txt"):
        with open(filename, "a") as f:
            lines = [
                "---\n",
                "Game Number: " + str(game_number) + "\n",
                "Winner: " + ("Human" if DataCollector.humans_remaining > 0 else "Zombie") + "\n",
                "Has hospital: " + str(DataCollector.hospital) + "\n",
                "Zombies killed: " + str(DataCollector.zombies_killed) + "\n",
                "Zombies cured: " + str(DataCollector.zombies_cured) + "\n",
                "Zombies cured in hospital: " + str(DataCollector.zombies_cured_in_hospital) + "\n",
                "Humans vaccinated: " + str(DataCollector.humans_vaccinated) + "\n",
                "Humans remaining: " + str(DataCollector.humans_remaining) + "\n",
                "Humans infected: " + str(DataCollector.humans_infected) + "\n",
                "Number of turns taken: " + str(DataCollector.turns_taken) + "\n"
            ]
            f.writelines(lines)
    
    @staticmethod
    def save_stats_data(self_play, game_number):
        if  DataCollector.hospital:
            if self_play:
                DataCollector.save_player_data("SelfPlayData_Hospital.txt")
            else:
                DataCollector.save_ai_data_of_one_game(game_number, "AiData_Hospital.txt")
        else:
            if self_play:
                DataCollector.save_player_data("SelfPlayData_NoHospital.txt")
            else:
                DataCollector.save_ai_data_of_one_game(game_number, "AiData_NoHospital.txt")



