from constants import *


###########################
# Maze Base Class
###########################
class MazeBase(object):
    def __init__(self):
        # Offset where the ghost house is positioned relative to map
        self.homeoffset = (0, 0)

        # Stores node positions where certain ghosts cannot move
        # Format: direction → tuple(node positions)
        self.ghostNodeDeny = {UP:(), DOWN:(), LEFT:(), RIGHT:()}

    # Create and connect the ghost home node(s)
    def connectHomeNodes(self, nodes):
        key = nodes.createHomeNodes(*self.homeoffset)
        nodes.connectHomeNodes(key, self.homenodeconnectLeft, LEFT)
        nodes.connectHomeNodes(key, self.homenodeconnectRight, RIGHT)

    # Add ghost home offset to a node position
    def addOffset(self, x, y):
        return x + self.homeoffset[0], y + self.homeoffset[1]

    # Apply ghost access restrictions on specific nodes
    def denyGhostsAccess(self, ghosts, nodes):
        # Block left and right movement at a central gate
        nodes.denyAccessList(*(self.addOffset(2, 3) + (LEFT, ghosts)))
        nodes.denyAccessList(*(self.addOffset(2, 3) + (RIGHT, ghosts)))

        # Apply additional movement restrictions defined per maze
        for direction in list(self.ghostNodeDeny.keys()):
            for values in self.ghostNodeDeny[direction]:
                nodes.denyAccessList(*(values + (direction, ghosts)))


###########################
# Maze 1 Layout
###########################
class Maze1(MazeBase):
    def __init__(self):
        super().__init__()   # Inherit shared setup
        self.name = "maze1"

        # Position references for spawning and ghost house
        self.homeoffset = (11.5, 14)
        self.homenodeconnectLeft = (12, 14)
        self.homenodeconnectRight = (15, 14)

        self.pacmanStart = (15, 26)
        self.fruitStart = (9, 20)

        # Restrict ghost movement in maze 1 layout
        self.ghostNodeDeny = {
            UP: ((12, 14), (15, 14), (12, 26), (15, 26)),
            LEFT: (self.addOffset(2, 3),),
            RIGHT: (self.addOffset(2, 3),)
        }


###########################
# Maze 2 Layout
###########################
class Maze2(MazeBase):
    def __init__(self):
        super().__init__()
        self.name = "maze2"

        # Position references for spawning and ghost home
        self.homeoffset = (11.5, 14)
        self.homenodeconnectLeft = (9, 14)
        self.homenodeconnectRight = (18, 14)

        self.pacmanStart = (16, 26)
        self.fruitStart = (11, 20)

        # Restrict ghost movement in maze 2 layout
        self.ghostNodeDeny = {
            UP: ((9, 14), (18, 14), (11, 23), (16, 23)),
            LEFT: (self.addOffset(2, 3),),
            RIGHT: (self.addOffset(2, 3),)
        }


###########################
# Maze Loader
###########################
class MazeData(object):
    def __init__(self):
        self.obj = None
        
        # Map numeric keys to maze classes
        self.mazedict = {0: Maze1, 1: Maze2}

    # Returns an instance of the selected maze based on level cycling
    def loadMaze(self, level):
        self.obj = self.mazedict[level % len(self.mazedict)]()
