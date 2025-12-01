import pygame
from vector import Vector2
from constants import *


###########################
# Text Object
###########################
class Text(object):
    def __init__(self, text, color, x, y, size, time=None, id=None, visible=True):
        self.id = id
        self.text = text
        self.color = color
        self.size = size
        self.visible = visible
        
        # Position stored as Vector2 for easy coordinate manipulation
        self.position = Vector2(x, y)
        
        # Timer used if text has a limited lifespan (ex: points popup)
        self.timer = 0
        self.lifespan = time
        
        # Label graphic created by pygame font system
        self.label = None
        
        # If true, TextGroup will delete this text instance
        self.destroy = False

        # Create font and label texture
        self.setupFont("PressStart2P-Regular.ttf")
        self.createLabel()

    # Load font from file
    def setupFont(self, fontpath):
        self.font = pygame.font.Font(fontpath, self.size)

    # Render text to a surface so pygame can draw it
    def createLabel(self):
        self.label = self.font.render(self.text, 1, self.color)

    # Change displayed text and regenerate label
    def setText(self, newtext):
        self.text = str(newtext)
        self.createLabel()

    # Timer logic for temporary text
    def update(self, dt):
        if self.lifespan is not None:
            self.timer += dt
            
            # Destroy when lifetime expires
            if self.timer >= self.lifespan:
                self.timer = 0
                self.lifespan = None
                self.destroy = True

    # Draw text if visible
    def render(self, screen):
        if self.visible:
            x, y = self.position.asTuple()
            screen.blit(self.label, (x, y))


###########################
# Text Group Controller
###########################
class TextGroup(object):
    def __init__(self):
        self.nextid = 10
        self.alltext = {}

        # Create default UI text labels
        self.setupText()

        # Start with "READY!" (but hidden until game starts)
        self.showText(READYTXT)

    # Add new text to dictionary and return its ID
    def addText(self, text, color, x, y, size, time=None, id=None):
        self.nextid += 1
        self.alltext[self.nextid] = Text(text, color, x, y, size, time=time, id=id)
        return self.nextid

    # Remove text entry from dictionary
    def removeText(self, id):
        self.alltext.pop(id)
        
    # Create standard UI labels
    def setupText(self):
        size = TILEHEIGHT
        
        self.alltext[SCORETXT]     = Text("0".zfill(8), WHITE, 0, TILEHEIGHT, size)
        self.alltext[LEVELTXT]     = Text(str(1).zfill(3), WHITE, 23*TILEWIDTH, TILEHEIGHT, size)
        self.alltext[READYTXT]     = Text("READY!", YELLOW, 11.25*TILEWIDTH, 20*TILEHEIGHT, size, visible=False)
        self.alltext[PAUSETXT]     = Text("PAUSED!", YELLOW, 10.625*TILEWIDTH, 20*TILEHEIGHT, size, visible=False)
        self.alltext[GAMEOVERTXT]  = Text("GAMEOVER!", YELLOW, 10*TILEWIDTH, 20*TILEHEIGHT, size, visible=False)

        # Add top UI titles
        self.addText("SCORE", WHITE, 0, 0, size)
        self.addText("LEVEL", WHITE, 23*TILEWIDTH, 0, size)

    # Update all text objects and remove expired ones
    def update(self, dt):
        for tkey in list(self.alltext.keys()):
            self.alltext[tkey].update(dt)
            if self.alltext[tkey].destroy:
                self.removeText(tkey)

    # Show only the selected text (READY, PAUSE, GAMEOVER)
    def showText(self, id):
        self.hideText()
        self.alltext[id].visible = True

    # Hide status text types
    def hideText(self):
        self.alltext[READYTXT].visible = False
        self.alltext[PAUSETXT].visible = False
        self.alltext[GAMEOVERTXT].visible = False

    # Update displayed score
    def updateScore(self, score):
        self.updateText(SCORETXT, str(score).zfill(8))

    # Update level label
    def updateLevel(self, level):
        self.updateText(LEVELTXT, str(level + 1).zfill(3))

    # Helper to update text if it exists
    def updateText(self, id, value):
        if id in self.alltext.keys():
            self.alltext[id].setText(value)

    # Draw every visible text item
    def render(self, screen):
        for tkey in list(self.alltext.keys()):
            self.alltext[tkey].render(screen)
