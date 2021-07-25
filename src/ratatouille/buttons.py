import pygame as pg


class Button:

    def __init__(self, 
                 coordinates: tuple[int, int],
                 font: pg.font.Font,
                 text: str, 
                 color_text: tuple[int, int, int],
                 color_text_hover: tuple[int, int, int],
                 color: tuple[int, int, int],
                 color_hover: tuple[int, int, int], 
                 size: tuple[int, int],  # not sure about size
                 border_radius=0,
                 func=None,  # default is None
                 args=None  # default is None
                 ): 

        # getting font
        self.font = font
        # rendering text with the normal color
        self.rendered_text = self.font.render(text, True, color_text)
        # rendering the text with the hover color
        self.rendered_text_hover = self.font.render(text, True, color_text_hover)

        # getting the rects to blit in the update method, centering the rect according to the button size
        center = size[0]//2+coordinates[0], size[1]//2+coordinates[1]

        self.rendered_text_rect = self.rendered_text.get_rect(center=center)
        self.rendered_text_hover_rect = self.rendered_text_hover.get_rect(center=center)

        # setting up the surface of the button with the given size and color, and finally getting its rect
        # to blit it with the given coordinates
        self.rect = pg.Rect(*coordinates, *size)

        # getting all the args needed for the nex functions
        self.color = color
        self.color_hover = color_hover
        self.func = func
        self.args = args
        
        self.border_radius = border_radius

    def update(self, screen):

        """Update function is there to blit the button, and manage the colors and hovering,
        it finally blit the surface to the screen given as an argument"""
        
        # getting the coordinates of the mouse to check the hovering
        mo_coo = pg.mouse.get_pos()

        # checking for mouse hover
        if self.rect.collidepoint(mo_coo):
            pg.draw.rect(screen, self.color_hover, self.rect, border_radius=self.border_radius)
            screen.blit(self.rendered_text_hover, self.rendered_text_hover_rect)
        else:
            pg.draw.rect(screen, self.color, self.rect, border_radius=self.border_radius)
            screen.blit(self.rendered_text, self.rendered_text_rect)

    def handle_click(self, pos):

        """Function to manage clicks"""

        # detecting clicks
        if self.rect.collidepoint(pos):
            # checking if a function is assigned to the button
            if self.func is not None:
                # checking if there are some args to put in the function
                if self.args is not None:
                    self.func(*self.args)
                else:
                    self.func()
