import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from entity import Entity
from modes import ModeController
from sprites import GhostSprites

###########################################################
# GHOST BASE CLASS
###########################################################

class Ghost(Entity):
    def __init__(self, node, pacman=None, blinky=None):
        # Initialize base entity at a specific map node
        Entity.__init__(self, node)

        # Set baseline attributes
        self.name = GHOST

        # Base point value (used when pacman eats ghost in freight mode)
        self.default_points = 200
        self.points = self.default_points

        # Goal position the ghost tries to move toward (depends on mode)
        self.goal = Vector2()

        # Reference to pacman (needed for CHASE mode)
        self.pacman = pacman

        # Controls ghost mode: SCATTER, CHASE, FREIGHT, SPAWN
        self.mode = ModeController(self)

        # Blinky reference (needed for Inky’s chase algorithm)
        self.blinky = blinky

        # Node where the ghost starts
        self.homeNode = node

        # Function pointer for modding ghost behavior (default is empty)
        self.mod_hook = self.default

    ###########################################################
    # DEFAULT HOOK — called when ghost has no mod active
    ###########################################################
    def default(self, dump):
        return

    ###########################################################
    # COLLISION-BASED PELLET COLLECTOR (MOD FEATURE)
    ###########################################################
    def collect_point(self, pellet_list):
        """
        Detects collision with pellets and awards points.
        Only active when mod_hook is switched to collect_point.
        """
        for pellet in pellet_list:
            if self.collideCheck(pellet):
                self.points += 1       # Increment ghost's internal point counter
                return pellet          # Return pellet so caller knows which to remove
        return None

    ###########################################################
    # DISTANCE-BASED COLLISION CHECK
    ###########################################################
    def collideCheck(self, other):
        """
        Returns True when two objects physically overlap.
        Uses radius-squared distance formulas to avoid taking square roots.
        """
        d = self.position - other.position
        dSquared = d.magnitudeSquared()
        rSquared = (self.collideRadius + other.collideRadius)**2
        return dSquared <= rSquared

    ###########################################################
    # TRIGGER THE MOD HOOK
    ###########################################################
    def eatPellets(self, pellet_list):
        """
        Calls the currently active mod behavior (default or collect_point).
        """
        return self.mod_hook(pellet_list)

    ###########################################################
    # ENABLE / DISABLE MOD
    ###########################################################
    def become_greedy(self):
        """
        Enables pellet-eating behavior for ghosts.
        """
        self.mod_hook = self.collect_point

    def stop_mod(self):
        """
        Returns to normal ghost behavior (no pellet eating).
        """
        self.mod_hook = self.default

    ###########################################################
    # RESET GHOST
    ###########################################################
    def reset(self):
        """
        Reset position, mode, movement, and points.
        """
        self.points = self.default_points
        Entity.reset(self=self)

    ###########################################################
    # GHOST UPDATE LOOP
    ###########################################################
    def update(self, dt):
        """
        Real-time update: animations, mode switching, behavior.
        """
        self.sprites.update(dt)
        self.mode.update(dt)

        if self.mode.current is SCATTER:
            self.scatter()
        elif self.mode.current is CHASE:
            self.chase()

        Entity.update(self, dt)

    ###########################################################
    # OVERRIDDEN RESET
    ###########################################################
    def reset(self):
        Entity.reset(self)
        self.points = 200
        self.directionMethod = self.goalDirection

    ###########################################################
    # MODE BEHAVIORS
    ###########################################################
    def scatter(self):
        """
        Default scatter target = corner (0,0).
        Children override this.
        """
        self.goal = Vector2()

    def chase(self):
        """
        Default chase = target Pac-Man directly.
        """
        self.goal = self.pacman.position

    ###########################################################
    # FREIGHT MODE (BLUE GHOSTS)
    ###########################################################
    def startFreight(self):
        """
        Ghost becomes vulnerable (blue), moves slowly and randomly.
        """
        self.mode.setFreightMode()
        if self.mode.current == FREIGHT:
            self.setSpeed(50)
            self.directionMethod = self.randomDirection

    ###########################################################
    # NORMAL MODE
    ###########################################################
    def normalMode(self):
        """
        Restore normal movement after freight.
        """
        self.setSpeed(100)
        self.directionMethod = self.goalDirection
        self.homeNode.denyAccess(DOWN, self)

    ###########################################################
    # SPAWN MODE (RETURNING TO GHOST HOUSE)
    ###########################################################
    def spawn(self):
        """
        Move toward the spawn node (ghost house entrance).
        """
        self.goal = self.spawnNode.position

    def setSpawnNode(self, node):
        """
        Set where ghosts return after being eaten.
        """
        self.spawnNode = node

    def startSpawn(self):
        """
        Trigger spawn mode after being eaten.
        """
        self.mode.setSpawnMode()
        if self.mode.current == SPAWN:
            self.setSpeed(150)
            self.directionMethod = self.goalDirection
            self.spawn()


###########################################################
# INDIVIDUAL GHOST BEHAVIORS
###########################################################

class Blinky(Ghost):
    """
    Blinky = Red ghost
    Chases Pac-Man directly
    Scatter target: top-right corner
    """
    def __init__(self, node, pacman=None, blinky=None):
        Ghost.__init__(self, node, pacman, blinky)
        self.name = BLINKY
        self.color = RED
        self.sprites = GhostSprites(self)


class Pinky(Ghost):
    """
    Pinky = Pink ghost
    Attempts to ambush Pac-Man 4 tiles ahead.
    Scatter target: upper-left corner.
    """
    def __init__(self, node, pacman=None, blinky=None):
        Ghost.__init__(self, node, pacman, blinky)
        self.name = PINKY
        self.color = PINK
        self.sprites = GhostSprites(self)

    def scatter(self):
        self.goal = Vector2(TILEWIDTH*NCOLS, 0)

    def chase(self):
        # Predict Pac-Man's movement 4 tiles ahead
        self.goal = self.pacman.position + self.pacman.directions[self.pacman.direction] * TILEWIDTH * 4


class Inky(Ghost):
    """
    Inky = Blue ghost
    Complex chase algorithm using Blinky + Pac-Man.
    Scatter corner: bottom-right.
    """
    def __init__(self, node, pacman=None, blinky=None):
        Ghost.__init__(self, node, pacman, blinky)
        self.name = INKY
        self.color = TEAL
        self.sprites = GhostSprites(self)

    def scatter(self):
        self.goal = Vector2(TILEWIDTH*NCOLS, TILEHEIGHT*NROWS)

    def chase(self):
        # Two-tile lookahead
        vec1 = self.pacman.position + self.pacman.directions[self.pacman.direction] * TILEWIDTH * 2
        # Reflection vector using Blinky's position
        vec2 = (vec1 - self.blinky.position) * 2
        self.goal = self.blinky.position + vec2


class Clyde(Ghost):
    """
    Clyde = Orange ghost
    If far: chase Pac-Man
    If close: run away to corner
    """
    def __init__(self, node, pacman=None, blinky=None):
        Ghost.__init__(self, node, pacman, blinky)
        self.name = CLYDE
        self.color = ORANGE
        self.sprites = GhostSprites(self)

    def scatter(self):
        self.goal = Vector2(0, TILEHEIGHT*NROWS)

    def chase(self):
        d = self.pacman.position - self.position
        ds = d.magnitudeSquared()

        # If close to Pac-Man → retreat to corner
        if ds <= (TILEWIDTH * 8)**2:
            self.scatter()
        else:
            # Otherwise chase 4 tiles ahead
            self.goal = self.pacman.position + self.pacman.directions[self.pacman.direction] * TILEWIDTH * 4


###########################################################
# GHOST GROUP CLASS — HANDLES ALL GHOSTS TOGETHER
###########################################################

class GhostGroup(object):
    def __init__(self, node, pacman):
        # Instantiate all four ghosts
        self.blinky = Blinky(node, pacman)
        self.pinky  = Pinky(node, pacman)
        self.inky   = Inky(node, pacman, self.blinky)
        self.clyde  = Clyde(node, pacman)

        # Convenient iterable list
        self.ghosts = [self.blinky, self.pinky, self.inky, self.clyde]

    def __iter__(self):
        return iter(self.ghosts)

    ###########################################################
    # GROUP UPDATE
    ###########################################################
    def update(self, dt):
        for ghost in self:
            ghost.update(dt)

    ###########################################################
    # FREIGHT MODE ACTIVATION
    ###########################################################
    def startFreight(self):
        for ghost in self:
            ghost.startFreight()
        self.resetPoints()

    ###########################################################
    # SPAWN NODE SETTER
    ###########################################################
    def setSpawnNode(self, node):
        for ghost in self:
            ghost.setSpawnNode(node)

    ###########################################################
    # POINT DOUBLING (during multiple ghost eats)
    ###########################################################
    def updatePoints(self):
        for ghost in self:
            ghost.points *= 2

    def resetPoints(self):
        for ghost in self:
            ghost.points = 200

    ###########################################################
    # RESET ALL GHOSTS
    ###########################################################
    def reset(self):
        for ghost in self:
            ghost.reset()

    ###########################################################
    # VISIBILITY MANAGEMENT
    ###########################################################
    def hide(self):
        for ghost in self:
            ghost.visible = False

    def show(self):
        for ghost in self:
            ghost.visible = True

    ###########################################################
    # RENDER ALL GHOSTS
    ###########################################################
    def render(self, screen):
        for ghost in self:
            ghost.render(screen)
