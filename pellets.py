import pygame
from vector import Vector2
from constants import *
import numpy as np


###########################
# Pellet Class
###########################
class Pellet(object):
    def __init__(self, row, column):
        self.name = PELLET
        
        # Convert tile grid position to pixel coordinates
        self.position = Vector2(column*TILEWIDTH, row*TILEHEIGHT)
        
        # Visual appearance
        self.color = WHITE
        self.radius = int(2 * TILEWIDTH / 16)        # Size of pellet
        self.collideRadius = int(2 * TILEWIDTH / 16) # Used for collision detection
        
        # Gameplay attributes
        self.points = 10
        self.visible = True

    # Draw pellet if it's still visible (not yet eaten)
    def render(self, screen):
        if self.visible:
            # Position it in the center of the tile
            adjust = Vector2(TILEWIDTH, TILEHEIGHT) / 2
            p = self.position + adjust
            
            pygame.draw.circle(screen, self.color, p.asInt(), self.radius)


###########################
# Power Pellet Class
###########################
class PowerPellet(Pellet):
    def __init__(self, row, column):
        super().__init__(row, column)  # Use Pellet setup
        
        self.name = POWERPELLET
        
        # Override size and score value
        self.radius = int(8 * TILEWIDTH / 16)
        self.points = 50

        # Flashing control variables
        self.flashTime = 0.2   # Time between visibility toggles
        self.timer = 0

    # Update visibility to create flashing effect
    def update(self, dt):
        self.timer += dt
        
        if self.timer >= self.flashTime:
            self.visible = not self.visible
            self.timer = 0


###########################
# Pellet Group
###########################
class PelletGroup(object):
    def __init__(self, pelletfile):
        self.pelletList = []     # Stores all pellets (normal + power pellets)
        self.powerpellets = []   # Tracks only power pellets for animation updates
        self.createPelletList(pelletfile)
        self.numEaten = 0

    # Update only power pellets (for flashing)
    def update(self, dt):
        for powerpellet in self.powerpellets:
            powerpellet.update(dt)

    # Create pellet objects based on map file characters
    def createPelletList(self, pelletfile):
        data = self.readPelletfile(pelletfile)

        for row in range(data.shape[0]):
            for col in range(data.shape[1]):
                
                # Normal pellet symbols
                if data[row][col] in ['.', '+']:
                    self.pelletList.append(Pellet(row, col))

                # Power pellet symbols
                elif data[row][col] in ['P', 'p']:
                    pp = PowerPellet(row, col)
                    self.pelletList.append(pp)
                    self.powerpellets.append(pp)

    # Read layout file and return grid as NumPy array
    def readPelletfile(self, textfile):
        return np.loadtxt(textfile, dtype='<U1')

    # Returns True when all pellets have been eaten
    def isEmpty(self):
        return len(self.pelletList) == 0

    # Render all pellets remaining on the screen
    def render(self, screen):
        for pellet in self.pelletList:
            pellet.render(screen)
