import pygame, sys
from button import Button

pygame.init()

SCREEN = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Login screen")

#TODO: add a different background image
BG = pygame.image.load("Poker_sim/Login_system/Background.png")

# Main menu screen
def main_menu():
    pygame.display.set_caption("Login screen")

    while True:
        SCREEN.blit(BG, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(100).render("Poker", True, "White")
        MENU_RECT = MENU_TEXT.get_rect(center=(640, 100))

        #TODO: add a different button image
        LOGIN_BUTTON = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(640, 250), text_input="Play", font=get_font(75), base_color="White", hovering_color="Green")
        SIGNUP_BUTTON = Button(image=pygame.image.load("assets/Signup Rect.png"), pos=(640, 400), text_input="Options", font=get_font(75), base_color="White", hovering_color="Green")
        QUIT_BUTTON = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(640, 550), text_input="Quit", font=get_font(75), base_color="White", hovering_color="Green")

        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [LOGIN_BUTTON, SIGNUP_BUTTON, QUIT_BUTTON]:
            button.change_color(MENU_MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if LOGIN_BUTTON.check_for_input(MENU_MOUSE_POS):
                    Login()
                if SIGNUP_BUTTON.check_for_input(MENU_MOUSE_POS):
                    Signup()
                if QUIT_BUTTON.check_for_input(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()


def Login():
    pass

def Signup():
    pass

def get_font(size):
    return pygame.font.Font("assets/font.ttf", size)

