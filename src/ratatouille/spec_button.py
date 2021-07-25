import pygame as pg


class SpecialButton:

    def __init__(self,
                 coordinates: tuple[int, int],
                 image: pg.Surface or str,  
                 image_hover: pg.Surface or str,
                 size: tuple[int, int],
                 func=None,
                 args=None
                 ):

        # we here let the user the possibility to use a path for an image
        # instead of a directly loaded image
        if type(image) == str:
            image = pg.image.load(image).convert()
        if type(image_hover) == str:
            image_hover = pg.image.load(image_hover).convert()

        # we resize the images
        self.image = pg.transform.smoothscale(image, size)
        self.image_hover = pg.transform.smoothscale(image_hover, size)

        # as the images are resized to the same size, we can use the same
        # rect for both
        self.rect = self.image.get_rect(topleft=coordinates)

        # get the func and args
        self.func = func
        self.args = args

    def update(self, screen):
        
        # getting mouse coordinates
        mo_coo = pg.mouse.get_pos()

        if self.rect.collidepoint(mo_coo):
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