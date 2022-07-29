import pygame
import PygameFunctions as PF

WHITE = PF.WHITE
HOSPITAL_COLOR = PF.HOSPITAL_COLOR
screen = PF.screen

def display_image(w,x,y,z):
    return PF.display_image(w,x,y,z)

def tutorial():
    tutorialRunning = True
    tutorialPart = 1
    
    # All tutorial Parts
    while tutorialRunning:
        PF.screen.fill(PF.BACKGROUND)
        PF.screen.blit(pygame.font.SysFont("Calibri", 40).render("Right Click Anywhere to Continue", True, PF.WHITE), (350, 30),)

        # Player Explanation Part 1
        if tutorialPart == 1:
            display_image(screen, "Assets/person_normal.png", (400, 400), (150, 100))
            display_image(screen, "Assets/person_zombie.png", (400, 400), (650, 100))
            display_image(screen, "Assets/govt.png", (400, 200), (150, 500))
            screen.blit(pygame.font.SysFont("Calibri", 40).render("You", True, WHITE), (320, 720),)
            display_image(screen, "Assets/zom.png", (400, 200), (650, 500))
            screen.blit(pygame.font.SysFont("Calibri", 40).render("Your Opponent", True, WHITE), (730, 720),)
        
        # Player Explanation Part 2
        elif tutorialPart == 2:
            screen.blit(pygame.font.SysFont("Calibri", 40).render("Normal Human", True, WHITE), (300, 230),)
            display_image(screen, "Assets/person_normal.png", (200, 200), (120, 150))
            screen.blit(pygame.font.SysFont("Calibri", 40).render("Normal Zombie", True, WHITE), (800, 230),)
            display_image(screen, "Assets/person_zombie.png", (200, 200), (620, 150))
            screen.blit(pygame.font.SysFont("Calibri", 40).render("Vaccinated Human", True, WHITE), (300, 550),)
            display_image(screen, "Assets/person_vax.png", (200, 200), (120, 450))
            screen.blit(pygame.font.SysFont("Calibri", 40).render("Half-Healed Zombie", True, WHITE), (800, 550),)
            display_image(screen, "Assets/person_half_zombie.png", (200, 200), (620, 450))
        
        # Heal Zombies Explaination
        elif tutorialPart == 3 or tutorialPart == 4:
            screen.blit(pygame.font.SysFont("Calibri", 35).render("Applying 'heal' to a zombie on non-hospital tiles:", True, WHITE), (100, 100),)
            display_image(screen, "Assets/person_zombie.png", (200, 200), (200, 200))
            display_image(screen, "Assets/heal_button.png", (100, 100), (400, 200))
            screen.blit(pygame.font.SysFont("Calibri", 40).render("--->", True, WHITE), (400, 300),)
            display_image(screen, "Assets/person_half_zombie.png", (200, 200), (500, 200))
            display_image(screen, "Assets/heal_button.png", (100, 100), (710, 200))
            screen.blit(pygame.font.SysFont("Calibri", 40).render("--->", True, WHITE), (720, 300),)
            display_image(screen, "Assets/person_normal.png", (200, 200), (800, 200))
            screen.blit(pygame.font.SysFont("Calibri", 35).render("What about on hospital tiles?", True, WHITE), (100, 450),)
        
        # Hospital Tiles Explaination
        if tutorialPart == 4:
            pygame.draw.rect(screen, HOSPITAL_COLOR, [200, 500, 800, 200])
            display_image(screen, "Assets/person_zombie.png", (200, 200), (200, 500))
            display_image(screen, "Assets/heal_button.png", (100, 100), (400, 500))
            screen.blit(pygame.font.SysFont("Calibri", 40).render("--->", True, WHITE), (400, 600),)
            display_image(screen, "Assets/person_normal.png", (200, 200), (500, 500))
            screen.blit(pygame.font.SysFont("Calibri", 35).render("Wow! It only takes one move!", True, WHITE), (100, 720),)

        # Vaccinate Humans Explaination
        elif tutorialPart == 5 or tutorialPart == 6:
            screen.blit(pygame.font.SysFont("Calibri", 35).render("What if you apply 'heal' to a person?", True, WHITE), (350, 250),)
        if tutorialPart == 6:
            display_image(screen, "Assets/person_normal.png", (200, 200), (350, 300))
            display_image(screen, "Assets/heal_button.png", (100, 100), (550, 300))
            screen.blit(pygame.font.SysFont("Calibri", 40).render("--->", True, WHITE), (550, 400),)
            display_image(screen, "Assets/person_vax.png", (200, 200), (650, 300))
            screen.blit(pygame.font.SysFont("Calibri", 35).render("Now the person is vaccinated!", True, WHITE), (350, 530),)

        # Kill Zombies Explaination
        elif tutorialPart == 7:
            screen.blit(pygame.font.SysFont("Calibri", 35).render("Applying 'kill' to a zombie:", True, WHITE), (350, 250),)
            display_image(screen, "Assets/person_zombie.png", (200, 200), (350, 300))
            display_image(screen, "Assets/kill_button.png", (100, 50), (550, 330))
            screen.blit(pygame.font.SysFont("Calibri", 40).render("--->", True, WHITE), (550, 400),)
            screen.blit(pygame.font.SysFont("Calibri", 35).render("The zombie is removed from the board.", True, WHITE), (350, 530),)

        # Cannot Kill Humans Explaination
        elif tutorialPart == 8 or tutorialPart == 9:
            screen.blit(pygame.font.SysFont("Calibri", 35).render("What if you apply 'kill' to a person?", True, WHITE), (350, 250),)
        if tutorialPart == 9:
            display_image(screen, "Assets/person_normal.png", (200, 200), (350, 300))
            display_image(screen, "Assets/kill_button.png", (100, 50), (550, 330))
            screen.blit(pygame.font.SysFont("Calibri", 40).render("--->", True, WHITE), (550, 400),)
            display_image(screen, "Assets/person_normal.png", (200, 200), (650, 300))
            screen.blit(pygame.font.SysFont("Calibri", 35).render("Invalid, why would you hurt your own team?!", True, WHITE), (350, 530),)
        
        # Adjacent to Human Explaination
        elif tutorialPart == 10:
            screen.blit(pygame.font.SysFont("Calibri", 35).render("A zombie can only be healed or killed if a human is next to them.", True, WHITE), (150, 250),)
            display_image(screen, "Assets/person_normal.png", (200, 200), (400, 300))
            display_image(screen, "Assets/person_zombie.png", (200, 200), (600, 300))
        
        # End Tutorial
        elif tutorialPart == 11:
            screen.blit(pygame.font.SysFont("Calibri", 35).render("You are ready.", True, WHITE), (500, 350),)
        elif tutorialPart == 12:
            tutorialRunning = False

        for event in pygame.event.get():
            # Next Stage of Tutorial
            if event.type == pygame.MOUSEBUTTONDOWN:
                tutorialPart += 1

            # Close Window
            elif event.type == pygame.QUIT:
                pygame.quit()
                #return

        pygame.display.update()