'''
               __          __               .__.__  .__                            
____________ _/  |______ _/  |_  ____  __ __|__|  | |  |   ____      ______ ___.__.
\_  __ \__  \\   __\__  \\   __\/  _ \|  |  \  |  | |  | _/ __ \     \____ <   |  |
 |  | \// __ \|  |  / __ \|  | (  <_> )  |  /  |  |_|  |_\  ___/     |  |_> >___  |
 |__|  (____  /__| (____  /__|  \____/|____/|__|____/____/\___  > /\ |   __// ____|
            \/          \/                                    \/  \/ |__|   \/  
@Credits 2021 By:  Théophile Aumont - Mario Papazogloy  
 Description: 
 We have created a UI Framework based on Pygame that allows new users who do not understand the details of creating a UI, 
 to be able to apply it in a quick and easy way without being detuned by other objects in their project.
 Fully customizable features included:

    - Draw Button
    - Button with image background
    - More stuff coming soon!
To use Ratatouille Framework you have to:
** Start method means that the method has to be called at the start of
the game and game loop method means that the method must be called inside
the loop **
Also, a "*" after an argument means that is OPTIONAL.
ratatouille = Ratouille.init(display_surface)
# Commands : Start Methods
.new_button() # Creates a button
Guide:
.new_button(coordinates, font_surface, text, color_text,hovering_color_text, size, border_radius*, func*, args*)
.new_special_button() # Create a button using images
Guide:                           # image can be a loaded image or just a path
.new_special_button(coordinates, image, image_hover, size, func, args)
.pause_button() # Creates a Pause button
Guide:
.pause_button(coordinates, font_surface, text, size,func)
# Commands : Game Loop Methods
.show_fps()  # show current fps
Guide:
.show_fps(clock, font, coordinates, color, color_txt)
To make the framework work you have to use this architecture of project :
# at the start
- initializing the engine with .init()
- defining all your buttons and stuff
# game loop:
- ratatouille.update() -> update all your stuff
    # event loop:
        - ratatouille.handle_events(event)
- (OPTIONAL) : draw shapes with the ratatouille.draw."shape" -> 
'''

import pygame as pg


def init(surface: pg.Surface):
    return FrameWork(surface)


class FrameWork:

    def __init__(self, screen: pg.Surface):
        self.screen, self.w, self.h, self.buttons = screen, screen.get_width(), screen.get_height(), []

    def update(self):
        return [button.update(self.screen) for button in self.buttons]

    def handle_events(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1: self.handle_clicks(event.pos)

    t, d, f = tuple[int, int, int], tuple[int, int], pg.font.Font  # Triple, Double, font

    def handle_clicks(self, pos: t):
        return [button.handle_click(pos) for button in self.buttons]

    def new_button(self, coordinates: d, font: f, text: str, color_text: t, color_text_hover: t, color: t,
                   color_hover: t, size: d, border_radius=25, func=None, args=None):
        self.buttons.append(
            Button(coordinates, font, text, color_text, color_text_hover, color, color_hover, size, border_radius, func,
                   args))

    def new_special_button(self, coordinates: d, image: pg.Surface or str, image_hover: pg.Surface or str, size: d,
                           func=None, args=None):
        return self.buttons.append(SpecialButton(coordinates, image, image_hover, size, func, args))

    def show_fps(self, clock: pg.time.Clock, font: f, coordinates: d, color=(0, 0, 0), color_txt=(255, 255, 255)):
        render = font.render(f"{round(clock.get_fps())}", True, color_txt);
        rect = render.get_rect(topleft=coordinates);
        pg.draw.rect(self.screen, color, rect)
        return self.screen.blit(render, rect)


# ------------- Finished Products ---------------


class Button:
    t, d, f = tuple[int, int, int], tuple[int, int], pg.font.Font  # Triple, Double, font

    def __init__(self, coords: d, font: f, text: str, color_text: t, color_text_hover: t, color: t, color_hover: t,
                 size: d, border_radius, func=None, args=None):  # defaults is None
        self.font = font  # Getting font
        # Rendering text with the normal color
        self.rendered_text, self.rendered_text_hover = self.font.render(text, True,
                                                                        color_text).convert_alpha(), self.font.render(
            text, True, color_text_hover).convert_alpha()

        # Getting the rects to blit in the update method, centering the rect according to the button size
        center = size[0] // 2 + coords[0], size[1] // 2 + coords[1]

        self.rendered_text_rect, self.rendered_text_hover_rect = self.rendered_text.get_rect(
            center=center), self.rendered_text_hover.get_rect(center=center)

        self.rect = pg.Rect(*coords, *size)  # Blit it with the given coordinates

        # Getting all the args needed for the next functions
        self.color, self.color_hover, self.func, self.args, self.border_radius = color, color_hover, func, args, border_radius

    """Update function is there to blit the button, and manage the colors and hovering,
        it finally blit the surface to the screen given as an argument"""

    def update(self, screen):
        # Checking for mouse hover based on position
        if self.rect.collidepoint(pg.mouse.get_pos()):
            pg.draw.rect(screen, self.color_hover, self.rect, border_radius=self.border_radius)
            screen.blit(self.rendered_text_hover, self.rendered_text_hover_rect)
        else:
            pg.draw.rect(screen, self.color, self.rect, border_radius=self.border_radius)
            screen.blit(self.rendered_text, self.rendered_text_rect)

    # Function to manage clicks
    def handle_click(self, pos):
        if self.rect.collidepoint(pos):  # Detecting clicks
            if self.func is not None:
                if self.args is not None:  # Checking if there are some args to put in the function
                    self.func(*self.args)
                else:
                    self.func()


class SpecialButton:

    def __init__(self, coordinates: tuple[int, int], image: pg.Surface or str, image_hover: pg.Surface or str,
                 size: tuple[int, int], func=None, args=None):
        # We let the user the possibility to use a path for an image, instead of a directly loaded image
        if type(image) == str:
            image = pg.image.load(image).convert()
        if type(image_hover) == str:
            image_hover = pg.image.load(image_hover).convert()

        # we resize the images
        self.image, self.image_hover = pg.transform.smoothscale(image, size), pg.transform.smoothscale(image_hover,
                                                                                                       size)
        self.rect = self.image.get_rect(
            topleft=coordinates)  # As the images are resized to the same size, we can use the same , rect for both

        # get the func and args
        self.func, self.args = func, args

    def update(self, screen):
        # getting mouse coordinates
        if self.rect.collidepoint(pg.mouse.get_pos()):
            screen.blit(self.image_hover, self.rect)
        else:
            screen.blit(self.image, self.rect)

    def handle_click(self, pos):
        # detecting clicks
        if self.rect.collidepoint(pos):
            # checking if a function is assigned to the button:
            if self.func is not None:
                #  checking if there are some args to put in the function
                if self.args is not None:
                    self.func(*self.args)
                else:
                    self.func()