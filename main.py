import numpy as np
import pygame
import random as rd 
import threading
from mod_mcts import mcts

import PygameFunctions as PF
import Tutorial as T
from DataCollector import DataCollector
from Board import Board
from Stats import Stats
#ctr-p
#>select interpreter

# Constants
AI_PLAY_WAITTIME_MS = 300

# Initialize variables
running = True
take_action = []
playerMoved = False
self_play = False
hospital = False

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.mixer.init()
click = pygame.mixer.Sound("Assets/click.wav")
#Start menu
StartButton = pygame.Rect(455, 600, 300, 100)
procstart = False
starthover = ""
while procstart == False:
    for event in pygame.event.get():
        PF.display_start_screen(starthover)
        starthover = ""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if StartButton.collidepoint(pygame.mouse.get_pos()):
                click.play()
                procstart = True
        elif event.type == pygame.MOUSEMOTION:
            if StartButton.collidepoint(pygame.mouse.get_pos()):
                starthover = "start"
        elif event.type == pygame.QUIT:
            pygame.quit()
# Option menu
SelfPlayButton = pygame.Rect(350, 250, 100, 100)
HospitalOnButton = pygame.Rect(700, 250, 100, 100)
ProceedButton = pygame.Rect(1050, 650, 100, 100)
StatsButton = pygame.Rect(500, 500, 100, 100)
TutorialButton = pygame.Rect(200, 600, 100, 100)

global GameBoard, ai_running

proceed = False
hover = ""
while proceed == False:
    for event in pygame.event.get():
        PF.display_options_screen(self_play, hospital, hover)
        hover = ""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if SelfPlayButton.collidepoint(pygame.mouse.get_pos()):
                click.play()
                self_play = not self_play
            elif HospitalOnButton.collidepoint(pygame.mouse.get_pos()):
                click.play()
                hospital = not hospital
            elif ProceedButton.collidepoint(pygame.mouse.get_pos()):
                click.play()
                proceed = True
            # Stats Button
            elif StatsButton.collidepoint(pygame.mouse.get_pos()):
                click.play()
                st = Stats()
                st.ethicsChart()
                st.AI_ethicsChart()
            elif TutorialButton.collidepoint(pygame.mouse.get_pos()):
                click.play()
                T.tutorial()
        elif event.type == pygame.MOUSEMOTION:
            if ProceedButton.collidepoint(pygame.mouse.get_pos()):
                hover = "proceed"
            elif HospitalOnButton.collidepoint(pygame.mouse.get_pos()):
                hover = "hospital"
            elif SelfPlayButton.collidepoint(pygame.mouse.get_pos()):
                hover = "self" 
        elif event.type == pygame.QUIT:
            pygame.quit()

GameBoard = Board(hospital=hospital)
ai_running = False
DataCollector.hospital = hospital

# Self play variables
clock = pygame.time.Clock()
frame = 0

# Buttons
kill_img = pygame.image.load("Assets/kill_button.png").convert_alpha()
KillButton = kill_img.get_rect(topleft=(785, 180))

heal_img = pygame.image.load("Assets/heal_button.png").convert_alpha()
HealButton = heal_img.get_rect(topleft=(850, 400))

kill_button = "button"
heal_button = "button"

# Monte Carlo!
searcher = mcts(timeLimit=500, explorationConstant=2.0)

def monte_carlo():
    global GameBoard, ai_running    
    ret = searcher.search(initialState=GameBoard, needDetails=True)
    action = ret["action"]
    reward = ret["expectedReward"]
    print(str(action) + ": " + str(reward))

    if action.act == "move_up":
        GameBoard.moveUp(action.row, action.col)        
    elif action.act == "move_down":
        GameBoard.moveDown(action.row, action.col)
    elif action.act == "move_left":
        GameBoard.moveLeft(action.row, action.col)
    elif action.act == "move_right":
        GameBoard.moveRight(action.row, action.col)
    elif action.act == "kill":
        GameBoard.auto_kill(action.row, action.col, simulation=False)
    elif action.act == "heal":
        GameBoard.auto_heal(action.row, action.col, simulation=False)
    elif action.act == "bite":
        raise "?????? why zombie???"    

    GameBoard.current_player *= -1    
    ai_running = False

score = 0
move = 0
game_number = 1
button_press = pygame.mixer.Sound("Assets/button_press.wav")
button_up = pygame.mixer.Sound("Assets/button_up.wav")
throw = pygame.mixer.Sound("Assets/throw.wav")
potion_break = pygame.mixer.Sound("Assets/potion_break.wav")
unfect = pygame.mixer.Sound("Assets/unfect.wav")
vaccine = pygame.mixer.Sound("Assets/vaccine.wav")
zombie_bite = pygame.mixer.Sound("Assets/zombie_bite.wav")
watergun = pygame.mixer.Sound("Assets/watergun.wav")
DataCollector.reset_data()
#if not self_play:
    #DataCollector.clear_ai_data()

WINDOWLESS = False
if WINDOWLESS:
    pygame.quit()

while running:        
    if not WINDOWLESS: PF.run(GameBoard, hospital, heal_button, kill_button)
    if self_play:                
        for event in pygame.event.get():
            if HealButton.collidepoint(pygame.mouse.get_pos()):
                if event.type == pygame.MOUSEBUTTONUP:                          # If heal button is let go of, select heal and update heal button image to selected
                    button_up.play()
                    take_action.append("heal")
                    heal_button = "select"
                elif event.type == pygame.MOUSEBUTTONDOWN:                      # If heal button is pressed, update heal button image to pressed
                    button_press.play()
                    heal_button = "press"
                elif heal_button != "select":                                   # If mouse is over heal button, update heal button to hovering
                    heal_button = "hover"                       
            elif heal_button != "select":
                heal_button = "button"
            if KillButton.collidepoint(pygame.mouse.get_pos()):
                if event.type == pygame.MOUSEBUTTONUP:                          # If kill button is let go of, select kill and update kill button image to selected
                    button_up.play()
                    take_action.append("kill")
                    kill_button = "select"
                elif event.type == pygame.MOUSEBUTTONDOWN:                      # If kill button is pressed, update kill button image to pressed
                    button_press.play()
                    kill_button = "press"
                elif kill_button != "select":
                    kill_button = "hover"                                       # If mouse is over kill button, update kill button to hovering
            elif kill_button != "select":
                kill_button = "button"
            if event.type == pygame.MOUSEBUTTONUP:
                if len(take_action) < 2:                                        # Checks if list is less than 2
                    x, y = pygame.mouse.get_pos()                               
                    action = PF.get_action(GameBoard, x, y)                     # If it is, find position of tile                    
                    if action != None:                                                
                        if take_action == []:                                   # If take_action is empty, check if selected tile is empty. If so, add selected tile as target
                            if ((GameBoard.states[action[0]][action[1]] is not None) and (GameBoard.states[action[0]][action[1]].isZombie == False)):
                                click.play()
                                take_action.append(action)
                        else:                                                   # Otherwise, add selected tile as destination  
                            click.play()                          
                            take_action.append(action)
            if event.type == pygame.QUIT:
                running = False
        # Display the current action
        """PF.screen.blit(
            pygame.font.SysFont("Calibri", 20).render("Your move is currently:", True, PF.WHITE),
            (800, 400),
        )
        PF.screen.blit(pygame.font.SysFont("Calibri", 20).render(f"{take_action}", True, PF.WHITE), (800, 450))
"""
        # Deselects or overrides action button
        if len(take_action) == 2:
            if take_action[0] == take_action[1]:
                take_action = []
                kill_button, heal_button = "button", "button"
            elif isinstance(take_action[1], str):
                take_action.pop(0)
                if take_action[0] == "heal":
                    kill_button = "button"
                else:
                    heal_button = "button"

        # Draws selection of game piece
        if len(take_action) == 1:
            if not isinstance(take_action[0], str):
                PF.select(take_action[0])

        # Action handling

        if len(take_action) == 2:
            if not isinstance(take_action[0], str):
                result = None
                directionToMove = PF.direction(take_action[0], take_action[1])
                if directionToMove == "moveUp":
                    result = GameBoard.moveUp(take_action[0][0], take_action[0][1])
                elif directionToMove == "moveDown":
                    result = GameBoard.moveDown(take_action[0][0], take_action[0][1])              
                elif directionToMove == "moveLeft":
                    result = GameBoard.moveLeft(take_action[0][0], take_action[0][1])
                elif directionToMove == "moveRight":
                    result = GameBoard.moveRight(take_action[0][0], take_action[0][1])
                if result != False:
                    playerMoved = True
                take_action = []
            elif take_action[0] == "heal":
                result = GameBoard.heal(take_action[1][0], take_action[1][1])
                if result[0] != False:
                    playerMoved = True
                    heal_button = "button"
                    if result[1] == "half": 
                        # Half heal animation
                        while frame < 12:
                            if frame == 0:
                                throw.play()
                            if frame == 5:
                                potion_break.play()
                            PF.half_heal_animation(frame)
                            pygame.display.update()                            
                            clock.tick(12)
                            frame += 1
                        frame = 0
                        score += 25
                    elif result[1] == "full":
                        while frame < 16:
                            if frame == 0:
                                throw.play()
                            if frame == 3:
                                unfect.play()
                            PF.full_heal_animation(frame)
                            pygame.display.update()                            
                            clock.tick(8)
                            frame += 1
                        frame = 0
                        score += 25
                    elif result[1] == "vaccine": 
                        while frame < 6:
                            if frame == 0:
                                throw.play()
                            if frame == 3:
                                vaccine.play()
                            PF.vaccine_animation(frame)
                            pygame.display.update()                            
                            clock.tick(8)
                            frame += 1
                        frame = 0
                        score += 10
                take_action = []
            elif take_action[0] == "kill":
                kill_button = "button"
                result = GameBoard.kill(take_action[1][0], take_action[1][1])
                if result != False:
                    playerMoved = True
                    kill_button = "button"                                  # turns kill button back to normal
                    while frame < 9:
                        if frame == 5:
                            watergun.play()
                        PF.kill_animation(frame)
                        pygame.display.update()                        
                        clock.tick(8)
                        frame += 1
                    frame = 0
                    score += 50
                take_action = []
            move += 1
        if GameBoard.num_humans == 0:
            PF.display_lose_screen(GameBoard.num_zombies)
            DataCollector.save_player_data()
            DataCollector.save_stats_data(True, 1)
            #print(score)
            if event.type == pygame.QUIT:
                running = False
        if GameBoard.num_zombies == 0:
            times = 1000 - (move*50)
            bonus = GameBoard.num_humans*100
            DataCollector.humans_remaining = GameBoard.num_humans
            DataCollector.save_player_data()
            DataCollector.save_stats_data(True, 1)
            PF.display_win_screen(GameBoard.num_humans, score, times, bonus)
            #print(score)
            if event.type == pygame.QUIT:
                running = False
                break            

        # Computer turn
        if playerMoved:
            PF.run(GameBoard, hospital, heal_button, kill_button)
            pygame.display.update()
            playerMoved = False
            take_action = []
            tempcalc = GameBoard.num_humans           
            actions = GameBoard.zombie_move()
            if GameBoard.num_humans == tempcalc-1:
                while frame < 11:
                    if frame == 4:
                        zombie_bite.play()
                    PF.zombie_bite(frame)
                    pygame.display.update()                            
                    clock.tick(8)
                    frame += 1
                frame = 0     
                score += -50        
            GameBoard.update_effects()
    # AI Algorithm        
    else:                
        
        if not WINDOWLESS:
            pygame.display.update() 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break                
        
        if not ai_running and GameBoard.current_player == 1:
            threading.Thread(target=monte_carlo).start()
            ai_running = True            

        elif GameBoard.current_player == -1:                        
            if GameBoard.num_zombies == 0:                                
                DataCollector.humans_remaining = GameBoard.num_humans
                DataCollector.save_ai_data_of_one_game(game_number)
                DataCollector.save_stats_data(False, game_number)
                game_number += 1
                DataCollector.reset_data()
                GameBoard = Board(hospital=hospital)                
                continue
            
            #pygame.time.wait(AI_PLAY_WAITTIME_MS)            
            GameBoard.zombie_random_move()
            GameBoard.update_effects()            

            if not WINDOWLESS: pygame.display.update()
            if GameBoard.num_humans == 0:
                DataCollector.humans_remaining = 0
                DataCollector.save_ai_data_of_one_game(game_number)
                DataCollector.save_stats_data(False, game_number)
                game_number += 1
                DataCollector.reset_data()
                GameBoard = Board(hospital=hospital)                
                continue
    if not WINDOWLESS: pygame.display.update()
        
