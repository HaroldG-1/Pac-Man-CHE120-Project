#Abiram Sarvananthan
#Harold Guo
#Matthew Kennedy - Commenter
#Gabriel Tirona
import pygame
from constants import *
import numpy as np
from animation import Animator

# Base size of tiles in the original sprite sheet
BASETILEWIDTH = 16
BASETILEHEIGHT = 16

# Animation key for death animation
DEATH = 5


##############################################################
#  SPRITESHEET CLASS — loads sprite sheet & extracts images
##############################################################
class Spritesheet(object):
    def __init__(self):
        # Load the entire master sprite sheet
        self.sheet = pygame.image.load("spritesheet.png").convert_alpha()

        # Read the color of the top-left pixel (used as transparency)
        transcolor = self.sheet.get_at((0,0))
        self.sheet.set_colorkey(transcolor)

        # Scale the sprite sheet to match game tile size
        width = int(self.sheet.get_width() / BASETILEWIDTH * TILEWIDTH)
        height = int(self.sheet.get_height() / BASETILEHEIGHT * TILEHEIGHT)
        self.sheet = pygame.transform.scale(self.sheet, (width, height))
        
    def getImage(self, x, y, width, height):
        """
        Extract a rectangle from the sprite sheet.
        x, y are in TILE coordinates (not pixels).
        width, height are pixel values.
        """
        x *= TILEWIDTH     # convert tile index → pixel position
        y *= TILEHEIGHT
        self.sheet.set_clip(pygame.Rect(x, y, width, height))
        return self.sheet.subsurface(self.sheet.get_clip())
    


##############################################################
#  PACMAN SPRITES 
##############################################################
class PacmanSprites(Spritesheet):
    def __init__(self, entity):
        # Load sprite sheet through parent class
        Spritesheet.__init__(self)
        self.entity = entity

        # Default image Pac-Man starts with
        self.entity.image = self.getStartImage()  

        # Dictionary holding animations for each direction
        self.animations = {}
        self.defineAnimations()

        # When Pac-Man is stopped, which frame should be shown
        self.stopimage = (8, 0)     

    def getStartImage(self):
        # Returns the idle Pac-Man frame
        return self.getImage(8, 0)

    def getImage(self, x, y):
        # Pac-Man sprites are 2×2 tiles
        return Spritesheet.getImage(self, x, y, 2*TILEWIDTH, 2*TILEHEIGHT)
    
    def defineAnimations(self):
        """
        Assign animation sequences for each direction.
        Each tuple contains (tile_x, tile_y) for each frame.
        """
        self.animations[LEFT] = Animator(((8,0), (0, 0), (0, 2), (0, 0)))
        self.animations[RIGHT] = Animator(((10,0), (2, 0), (2, 2), (2, 0)))
        self.animations[UP] = Animator(((10,2), (6, 0), (6, 2), (6, 0)))
        self.animations[DOWN] = Animator(((8,2), (4, 0), (4, 2), (4, 0)))

        # Death animation frames (11 frames)
        self.animations[DEATH] = Animator(
            ((0, 12), (2, 12), (4, 12), (6, 12), (8, 12),
             (10, 12), (12, 12), (14, 12), (16, 12),
             (18, 12), (20, 12)),
            speed=6,
            loop=False
        )

    def update(self, dt):
        """
        Changes Pac-Man's sprite depending on direction or death.
        dt = delta time since last frame.
        """
        if self.entity.alive == True:
            # Pick animation depending on direction
            if self.entity.direction == LEFT:
                self.entity.image = self.getImage(*self.animations[LEFT].update(dt))
                self.stopimage = (8, 0)

            elif self.entity.direction == RIGHT:
                self.entity.image = self.getImage(*self.animations[RIGHT].update(dt))
                self.stopimage = (10, 0)

            elif self.entity.direction == DOWN:
                self.entity.image = self.getImage(*self.animations[DOWN].update(dt))
                self.stopimage = (8, 2)

            elif self.entity.direction == UP:
                self.entity.image = self.getImage(*self.animations[UP].update(dt))
                self.stopimage = (10, 2)

            elif self.entity.direction == STOP:
                # Standing-still frame
                self.entity.image = self.getImage(*self.stopimage)
        
        else:
            # Death animation
            self.entity.image = self.getImage(*self.animations[DEATH].update(dt))
           
    def reset(self):
        # Resets animations (usually at start of life)
        for key in list(self.animations.keys()):
            self.animations[key].reset()



##############################################################
#  GHOST SPRITES — logic for ghost eyes, scared mode, directions
##############################################################
class GhostSprites(Spritesheet):
    def __init__(self, entity):
        Spritesheet.__init__(self)

        # Column offset for each ghost (their colours)
        self.x = {BLINKY:0, PINKY:2, INKY:4, CLYDE:6}

        self.entity = entity
        self.entity.image = self.getStartImage()
               
    def getStartImage(self):
        # Default facing-up sprite
        return self.getImage(self.x[self.entity.name], 4)

    def getImage(self, x, y):
        # Ghost sprites are 2×2 tiles
        return Spritesheet.getImage(self, x, y, 2*TILEWIDTH, 2*TILEHEIGHT)
    
    def update(self, dt):
        """
        Change ghost sprite depending on direction and mode:
        - SCATTER or CHASE : normal eyes + color
        - FREIGHT : blue scared ghost
        - SPAWN : only eyes (returning to house)
        """
        x = self.x[self.entity.name]

        # Normal modes
        if self.entity.mode.current in [SCATTER, CHASE]:
            if self.entity.direction == LEFT:
                self.entity.image = self.getImage(x, 8)
            elif self.entity.direction == RIGHT:
                self.entity.image = self.getImage(x, 10)
            elif self.entity.direction == DOWN:
                self.entity.image = self.getImage(x, 6)
            elif self.entity.direction == UP:
                self.entity.image = self.getImage(x, 4)

        # Blue frightened ghost
        elif self.entity.mode.current == FREIGHT:
            self.entity.image = self.getImage(10, 4)

        # Eyes only (ghost returning to box)
        elif self.entity.mode.current == SPAWN:
            if self.entity.direction == LEFT:
                self.entity.image = self.getImage(8, 8)
            elif self.entity.direction == RIGHT:
                self.entity.image = self.getImage(8, 10)
            elif self.entity.direction == DOWN:
                self.entity.image = self.getImage(8, 6)
            elif self.entity.direction == UP:
                self.entity.image = self.getImage(8, 4)



##############################################################
#  FRUIT SPRITES — images for fruits by level
##############################################################
class FruitSprites(Spritesheet):
    def __init__(self, entity, level):
        Spritesheet.__init__(self)
        self.entity = entity

        # Locations of fruits on sprite sheet
        self.fruits = {
            0:(16,8), 1:(18,8), 2:(20,8),
            3:(16,10), 4:(18,10), 5:(20,10)
        }

        # Pick fruit depending on level
        self.entity.image = self.getStartImage(level % len(self.fruits))

    def getStartImage(self, key):
        return self.getImage(*self.fruits[key])

    def getImage(self, x, y):
        # Fruits are also 2×2 tiles
        return Spritesheet.getImage(self, x, y, 2*TILEWIDTH, 2*TILEHEIGHT)
    


##############################################################
#  LIFE SPRITES — icons used to show Pac-Man lives
##############################################################
class LifeSprites(Spritesheet):
    def __init__(self, numlives):
        Spritesheet.__init__(self)
        self.resetLives(numlives)

    def removeImage(self):
        # Remove one life icon
        if len(self.images) > 0:
            self.images.pop(0)

    def resetLives(self, numlives):
        # Reset lives display to n icons
        self.images = []
        for i in range(numlives):
            self.images.append(self.getImage(0,0))

    def getImage(self, x, y):
        return Spritesheet.getImage(self, x, y, 2*TILEWIDTH, 2*TILEHEIGHT)
    


##############################################################
#  MAZE SPRITES — constructs the tile-based maze background
##############################################################
class MazeSprites(Spritesheet):
    def __init__(self, mazefile, rotfile):
        Spritesheet.__init__(self)

        # Maze tile map (digits)
        self.data = self.readMazeFile(mazefile)

        # Rotation values for each tile
        self.rotdata = self.readMazeFile(rotfile)

    def getImage(self, x, y):
        # Maze tiles are 1×1 tile squares
        return Spritesheet.getImage(self, x, y, TILEWIDTH, TILEHEIGHT)

    def readMazeFile(self, mazefile):
        # Load a file containing maze layout characters
        return np.loadtxt(mazefile, dtype='<U1')

    def constructBackground(self, background, y):
        """
        Builds the maze image by looping over each tile in the maze file.
        If tile is a number → choose tile from sheet and rotate it.
        If tile is '=' → draw special unrotated tile.
        """
        for row in list(range(self.data.shape[0])):
            for col in list(range(self.data.shape[1])):

                if self.data[row][col].isdigit():
                    # Select correct sprite index
                    x = int(self.data[row][col]) + 12
                    sprite = self.getImage(x, y)

                    # Rotate depending on rotation map
                    rotval = int(self.rotdata[row][col])
                    sprite = self.rotate(sprite, rotval)

                    # Draw onto background
                    background.blit(sprite, (col*TILEWIDTH, row*TILEHEIGHT))

                elif self.data[row][col] == '=':
                    # Draw special tile (no rotation)
                    sprite = self.getImage(10, 8)
                    background.blit(sprite, (col*TILEWIDTH, row*TILEHEIGHT))

        return background
    
    def rotate(self, sprite, value):
        # Rotates tile in 90-degree increments
        return pygame.transform.rotate(sprite, value*90)
