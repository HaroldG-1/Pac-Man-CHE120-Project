import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from random import randint

############################################################
# ENTITY BASE CLASS
# This is the parent class for Pac-Man, Ghosts, and any
# other moving objects on the grid. 
############################################################

class Entity(object):
    def __init__(self, node):
        # Name of entity (set by child class — Pacman / Ghost)
        self.name = None

        # Movement vector for each direction
        self.directions = {
            UP:    Vector2(0, -1),
            DOWN:  Vector2(0,  1),
            LEFT:  Vector2(-1, 0),
            RIGHT: Vector2(1,  0),
            STOP:  Vector2()
        }

        # Starting facing direction
        self.direction = STOP

        # Base movement speed
        self.setSpeed(100)

        # Visual and collision sizes
        self.radius = 10
        self.collideRadius = 5
        self.color = WHITE

        # Visibility toggles (ghosts can be hidden)
        self.visible = True

        # Disable portals flag (Pac-Man uses → Ghosts can disable)
        self.disablePortal = False

        # For ghosts: the tile they try to reach
        self.goal = None

        # How the entity picks new directions:
        # Default = aim toward goal (Ghosts), but can be randomized
        self.directionMethod = self.goalDirection

        # Set initial node and position
        self.setStartNode(node)

        # If set, overrides drawing (e.g., ghost sprites)
        self.image = None

    ############################################################
    # START NODE SETUP
    ############################################################
    def setStartNode(self, node):
        """
        Set node as the starting point for the object.
        Also resets position and target.
        """
        self.node = node
        self.startNode = node
        self.target = node
        self.setPosition()

    ############################################################
    # GENERAL RESET (used after death / level restart)
    ############################################################
    def reset(self):
        """
        Reset entity to its original node and state.
        """
        self.setStartNode(self.startNode)
        self.direction = STOP
        self.speed = 100
        self.visible = True

    ############################################################
    # USED WHEN FORCING ENTITY BETWEEN TWO NODES
    ############################################################
    def setBetweenNodes(self, direction):
        """
        Force the entity to appear centered between two nodes.
        Used when reversing direction or teleporting.
        """
        if self.node.neighbors[direction] is not None:
            self.target = self.node.neighbors[direction]
            self.position = (self.node.position + self.target.position) / 2.0

    ############################################################
    # POSITION CONTROL
    ############################################################
    def setPosition(self):
        """
        Sets Entity's actual position equal to its node's position.
        """
        self.position = self.node.position.copy()

    ############################################################
    # MAIN UPDATE LOOP — MOVEMENT + NODE TRANSITION
    ############################################################
    def update(self, dt):
        """
        Moves Entity toward its target every frame.
        Handles:
        - movement updates
        - checking for passing target node
        - picking new direction at intersections
        """
        # Move based on speed and direction
        self.position += self.directions[self.direction] * self.speed * dt

        # If passed the node we were traveling toward:
        if self.overshotTarget():
            # Snap to target node
            self.node = self.target

            # Get list of valid directions at this node
            directions = self.validDirections()

            # Determine new direction (goal-based or random)
            direction = self.directionMethod(directions)

            # Handle portals (wrap tunnels)
            if not self.disablePortal:
                if self.node.neighbors[PORTAL] is not None:
                    self.node = self.node.neighbors[PORTAL]

            # Set next target node
            self.target = self.getNewTarget(direction)

            # If valid direction -> commit to turn
            if self.target is not self.node:
                self.direction = direction
            else:
                # If direction blocked, keep trying same direction
                self.target = self.getNewTarget(self.direction)

            # Snap exact position to node center
            self.setPosition()

    ############################################################
    # VALID MOVEMENT CHECKERS
    ############################################################
    def validDirection(self, direction):
        """
        Checks whether an entity can move in a direction from current node.
        Prevents:
        - moving into walls
        - moving opposite direction unless required
        """
        if direction is not STOP:
            if self.name in self.node.access[direction]:
                if self.node.neighbors[direction] is not None:
                    return True
        return False

    def validDirections(self):
        """
        Returns all possible legal movement directions.
        Removes the reverse direction unless forced.
        """
        directions = []
        for key in [UP, DOWN, LEFT, RIGHT]:
            if self.validDirection(key):
                # Don't allow immediate backtracking
                if key != self.direction * -1:
                    directions.append(key)

        # If trapped, only option is reverse
        if len(directions) == 0:
            directions.append(self.direction * -1)

        return directions

    ############################################################
    # RANDOM MOVEMENT CHOICE
    ############################################################
    def randomDirection(self, directions):
        """
        Choose a random valid direction.
        Used for ghosts in freight mode.
        """
        return directions[randint(0, len(directions)-1)]

    ############################################################
    # SETTING NEW TARGET NODE
    ############################################################
    def getNewTarget(self, direction):
        """
        Returns the node that lies in the direction of movement.
        If invalid, returns current node (no movement).
        """
        if self.validDirection(direction):
            return self.node.neighbors[direction]
        return self.node

    ############################################################
    # CHECK IF ENTITY HAS PASSED ITS TARGET NODE
    ############################################################
    def overshotTarget(self):
        """
        Determines whether the entity has traveled farther than the
        distance between its current and target node.
        """
        if self.target is not None:
            vec1 = self.target.position - self.node.position
            vec2 = self.position - self.node.position
            return vec2.magnitudeSquared() >= vec1.magnitudeSquared()
        return False

    ############################################################
    # DIRECTION UTILITIES
    ############################################################
    def reverseDirection(self):
        """
        Immediately reverse movement direction.
        Used by ghosts when switching from scatter to chase.
        """
        self.direction *= -1
        temp = self.node
        self.node = self.target
        self.target = temp

    def oppositeDirection(self, direction):
        """
        True if the given direction is exactly opposite to current.
        """
        if direction is not STOP:
            if direction == self.direction * -1:
                return True
        return False

    ############################################################
    # SPEED CONTROL
    ############################################################
    def setSpeed(self, speed):
        """
        Converts speed into tile-based movement speed.
        Speed is relative to tile size.
        """
        self.speed = speed * TILEWIDTH / 16

    ############################################################
    # GOAL-SEEKING MOVEMENT (main ghost AI)
    ############################################################
    def goalDirection(self, directions):
        """
        Choose the direction that minimizes squared distance to 'goal'.
        Used by ghosts in chase/scatter/spawn modes.
        """
        distances = []
        for direction in directions:
            #Find pacmans position 1 tile ahead
            vec = self.node.position + self.directions[direction] * TILEWIDTH - self.goal
            distances.append(vec.magnitudeSquared())

        # Select direction with the shortest desired path
        return directions[distances.index(min(distances))]

    ############################################################
    # RENDERING
    ############################################################
    def render(self, screen):
        """
        Draws the entity.
        If image is assigned: draw sprite.
        Otherwise: draw colored circle.
        """
        if self.visible:
            if self.image is not None:
                adjust = Vector2(TILEWIDTH, TILEHEIGHT) / 2
                p = self.position - adjust
                screen.blit(self.image, p.asTuple())
            else:
                p = self.position.asInt()
                pygame.draw.circle(screen, self.color, p, self.radius)
