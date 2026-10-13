import pygame


class TextBox:
    def __init__(self, x, y, w, h, font, placeholder="", password=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.text = ""
        self.active = False
        self.password = password

        self.color_inactive = pygame.Color("gray")
        self.color_active = pygame.Color("white")
        self.color = self.color_inactive
        self.placeholder = placeholder

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Click inside box?
            self.active = self.rect.collidepoint(event.pos)
            self.color = self.color_active if self.active else self.color_inactive

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]

            elif event.key == pygame.K_RETURN:
                return self.text

            else:
                self.text += event.unicode

        return None

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, 2)

        if self.text == "":
            text_surface = self.font.render(self.placeholder, True, "gray")
        else:
            display_text = self.text
            if self.password:
                display_text = "*" * len(self.text)

            text_surface = self.font.render(display_text, True, "white")

        screen.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))
