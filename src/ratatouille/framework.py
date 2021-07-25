import pygame as pg
from .buttons import Button
from .spec_button import SpecialButton


def init(surface: pg.Surface):
    return FrameWork(surface)


class FrameWork:

    def __init__(self,
                 screen: pg.Surface):

        self.screen, self.w, self.h = screen, screen.get_width(), screen.get_height()

        self.buttons = []

    def update(self):

        for button in self.buttons:
            button.update(self.screen)

    def handle_events(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.handle_clicks(event.pos)

    def handle_clicks(self, pos: tuple[int, int, int]):
        for button in self.buttons:
            button.handle_click(pos)

    def new_button(self,
                   coordinates: tuple[int, int],
                   font: pg.font.Font,
                   text: str,
                   color_text: tuple[int, int, int],
                   color_text_hover: tuple[int, int, int],
                   color: tuple[int, int, int],
                   color_hover: tuple[int, int, int],
                   size: tuple[int, int],  # not sure about size
                   border_radius=0,
                   func=None,
                   args=None):
        self.buttons.append(Button(coordinates, font, text, color_text,
                                   color_text_hover, color, color_hover,
                                   size, border_radius, func, args))

    def new_special_button(self,
                           coordinates: tuple[int, int],
                           image: pg.Surface or str,
                           image_hover: pg.Surface or str,
                           size: tuple[int, int],
                           func=None,
                           args=None
                           ):
        self.buttons.append(SpecialButton(coordinates, image,
                                          image_hover, size,
                                          func, args))

    def show_fps(self,
                 clock: pg.time.Clock,
                 font: pg.font.Font,
                 coordinates: tuple[int, int],
                 color=(0, 0, 0),
                 color_txt=(255, 255, 255)):
        render = font.render(str(round(clock.get_fps())), True, color_txt)
        rect = render.get_rect(topleft=coordinates)
        pg.draw.rect(self.screen, color, rect)
        self.screen.blit(render, rect)
