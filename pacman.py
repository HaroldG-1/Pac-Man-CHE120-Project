#Abiram Sarvananthan
#Harold Guo - Commenter
#Matthew Kennedy
#Gabriel Tirona
import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from entity import Entity
from sprites import PacmanSprites

#Creates the pacman class where all the pacman information is stored
class Pacman(Entity):
    #Controls the directions pacman can move using vectors
    #Sets speed, radius for collisions with other objects
    #Prepares the pacman sprite
    #Sets pacman's starting node
    def __init__(self, node):
        Entity.__init__(self, node )
        self.name = PACMAN
        self.directions = {STOP:Vector2(), UP:Vector2(0,-1), DOWN:Vector2(0,1), LEFT:Vector2(-1,0), RIGHT:Vector2(1,0)}
        self.direction = STOP
        self.speed = 100 * TILEWIDTH/16
        self.radius = 10
        self.color = YELLOW
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.node = node
        self.target = node
        self.collideRadius = 5
        self.alive = True
        self.sprites = PacmanSprites(self)
        self.reset()
        
    #Update pacman's position to node position
    def setPosition(self):
        self.position = self.node.position.copy()

    #Used to reset pacman after losing a life or starting the game
    #Sets sprite and position to the initial conditions
    def reset(self):
        Entity.reset(self)
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.image = self.sprites.getStartImage()
        self.sprites.reset()

    #Stops movement if pacman dies
    def die(self):
        self.alive = False
        self.direction = STOP

    #Updates the position of pacman throughout the game using speed and time passed
    #Updates the direction and the node pacman is moving towards based on keyboard input
    #If pacman passes its target node, a new one along the same direction is set as the target
    #Turns or reverses pacman direction if conditions are met
    def update(self, dt):
        self.sprites.update(dt)	
        self.position += self.directions[self.direction]*self.speed*dt
        direction = self.getValidKey()
        if self.overshotTarget():
            self.node = self.target
            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]
            self.target = self.getNewTarget(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.getNewTarget(self.direction)
            if self.target is self.node:
                self.direction = STOP
            self.setPosition()
        else: 
            if self.oppositeDirection(direction):
                self.reverseDirection()

    #Checks if the pacman can move in a certain direction
    def validDirection(self, direction):
        if direction is not STOP:
            if self.node.neighbors[direction] is not None:
                return True
        return False

    #Gets pacman to start moving towards a new node it changes to a valid direction
    def getNewTarget(self, direction):
        if self.validDirection(direction):
            return self.node.neighbors[direction]
        return self.node

    #Checks which keys are being pressed by the player
    #If an arrow key is pressed, returns the corresponding direction
    def getValidKey(self):
        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_UP]:
            return UP
        if key_pressed[K_DOWN]:
            return DOWN
        if key_pressed[K_LEFT]:
            return LEFT
        if key_pressed[K_RIGHT]:
            return RIGHT
        return STOP

    #Determines if pacman has passed its target node
    #Calculates distance between pacman and the most recent node
    #If it's greater than the distance between the node and target, pacman has passed the target
    def overshotTarget(self):
        if self.target is not None:
            vec1 = self.target.position - self.node.position
            vec2 = self.position - self.node.position
            node2Target = vec1.magnitudeSquared()
            node2Self = vec2.magnitudeSquared()
            return node2Self >= node2Target
        return False

    #Updates the pacman's target node if direction reverses
    def reverseDirection(self):
        self.direction *= -1
        temp = self.node
        self.node = self.target
        self.target = temp

    #Changes the pacman direction to the opposite direction
    def oppositeDirection(self, direction):
        if direction is not STOP:
            if direction == self.direction * -1:
                return True
        return False

    #Checks for collisions between pacman and pellets
    #If a collision occurs, returns the pellet that was eaten for the game to remove it
    def eatPellets(self, pelletList):
        for pellet in pelletList:
            if self.collideCheck(pellet):
                return pellet
        return None

    #Checks for collision between pacman and ghosts
    def collideGhost(self, ghost):
        return self.collideCheck(ghost)

    #Defines how all collisions are checked, finds distance between pacman and object
    #If that distance is less than the collision radius, a collision happens and function returns True
    def collideCheck(self, other):
        d = self.position - other.position
        dSquared = d.magnitudeSquared()
        rSquared = (self.collideRadius + other.collideRadius)**2
        if dSquared <= rSquared:
            return True
        return False