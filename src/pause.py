import pygame as pg

from src.utils import load, load_alpha, resize, resizex


class Pause:

    def __init__(self, screen):

        self.screen, self.w, self.h = screen, screen.get_width(), screen.get_height()

        self.bg = resizex(load_alpha("data/assets/credits-background-no-burger.png"), 4)
        self.bg_rect = self.bg.get_rect(center=(self.w // 2, self.h // 2))

        self.buttons = [
            resizex(load_alpha("data/assets/button.png"), 2),
            resizex(load_alpha("data/assets/button.png"), 2)
        ]
        self.buttons_hover = [
            resizex(load_alpha("data/assets/button_hover.png"), 2),
            resizex(load_alpha("data/assets/button_hover.png"), 2)
        ]
        self.btn_rects = [
            self.buttons[0].get_rect(center=(self.w//2, self.h//2-20)),
            self.buttons[1].get_rect(center=(self.w//2, self.h//2+45))
        ]

        self.font = pg.font.Font(None, 40)
        self.text = [self.font.render("resume", True, (0, 0, 0)), self.font.render("quit", True, (0, 0, 0))]
        self.txt_rects = [txt.get_rect(center=self.btn_rects[id_].center) for id_, txt in enumerate(self.text)]

        self.opacity_layer = pg.Surface(self.screen.get_size())
        self.opacity_layer.set_alpha(180)

        self.layer_added = False

    def handle_events(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.btn_rects[0].collidepoint(event.pos):
                return "resume"
            elif self.btn_rects[1].collidepoint(event.pos):
                return "quit"

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                return "resume"

    def update(self):

        self.screen.blit(self.bg, self.bg_rect)

        for id_, button in enumerate(self.buttons):
            if not self.btn_rects[id_].collidepoint(pg.mouse.get_pos()):
                self.screen.blit(button, self.btn_rects[id_])
            else:
                self.screen.blit(self.buttons_hover[id_], self.btn_rects[id_])

        for id_, text in enumerate(self.text):
            self.screen.blit(text, self.txt_rects[id_])
