#Abiram Sarvananthan
#Harold Guo
#Matthew Kennedy
#Gabriel Tirona - Commenter
import pygame
from vector import Vector2
from constants import *
import numpy as np


# NODE CLASS — represents a single intersection in the maze
class Node(object):
    def __init__(self, x, y):
        # Position of this node in pixel coordinates
        self.position = Vector2(x, y)

        # Neighboring nodes in all possible directions
        self.neighbors = {
            UP: None, DOWN: None,
            LEFT: None, RIGHT: None,
            PORTAL: None
        }

        # Which entities are allowed to move through each direction
        self.access = {
            UP:    [PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT],
            DOWN:  [PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT],
            LEFT:  [PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT],
            RIGHT: [PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT],
        }


    # ACCESS CONTROL
    def denyAccess(self, direction, entity):
        # Removes entity permission
        if entity.name in self.access[direction]:
            self.access[direction].remove(entity.name)

    def allowAccess(self, direction, entity):
        # Adds entity permission
        if entity.name not in self.access[direction]:
            self.access[direction].append(entity.name)


    # DRAWING / DEBUG VISUALIZATION
    def render(self, screen):
        # Draw lines connecting this node to its neighbors
        for n in self.neighbors.keys():
            if self.neighbors[n] is not None:
                line_start = self.position.asTuple()
                line_end = self.neighbors[n].position.asTuple()
                pygame.draw.line(screen, WHITE, line_start, line_end, 4)
                pygame.draw.circle(screen, RED, self.position.asInt(), 12)



# NODE GROUP — creates all nodes based on the maze layout
class NodeGroup(object):
    def __init__(self, level):
        self.level = level
        self.nodesLUT = {}      # Lookup table: (x,y) → Node
        self.nodeSymbols = ['+', 'P', 'n']  # Symbols that represent nodes
        self.pathSymbols = ['.', '-', '|', 'p']  # Symbols that represent passable paths

        # Read layout and build node network
        data = self.readMazeFile(level)
        self.createNodeTable(data)
        self.connectHorizontally(data)
        self.connectVertically(data)

        self.homekey = None  # Entrance node for ghost house

    # FILE LOADING
    def readMazeFile(self, textfile):
        return np.loadtxt(textfile, dtype='<U1')


    # CREATE ALL NODES FROM MAZE DATA
    def createNodeTable(self, data, xoffset=0, yoffset=0):
        for row in range(data.shape[0]):
            for col in range(data.shape[1]):
                # Only create Node objects for actual node symbols
                if data[row][col] in self.nodeSymbols:
                    x, y = self.constructKey(col + xoffset, row + yoffset)
                    self.nodesLUT[(x, y)] = Node(x, y)

    def constructKey(self, x, y):
        # Convert tile position → pixel coordinates
        return x * TILEWIDTH, y * TILEHEIGHT


    # CONNECT NODES HORIZONTALLY
    def connectHorizontally(self, data, xoffset=0, yoffset=0):
        for row in range(data.shape[0]):
            key = None
            for col in range(data.shape[1]):
                if data[row][col] in self.nodeSymbols:     # Found a node
                    if key is None:
                        key = self.constructKey(col + xoffset, row + yoffset)
                    else:
                        otherkey = self.constructKey(col + xoffset, row + yoffset)
                        # Connect nodes left to right
                        self.nodesLUT[key].neighbors[RIGHT] = self.nodesLUT[otherkey]
                        self.nodesLUT[otherkey].neighbors[LEFT] = self.nodesLUT[key]
                        key = otherkey
                elif data[row][col] not in self.pathSymbols:
                    key = None  # Reset connection state

    # CONNECT NODES VERTICALLY
    def connectVertically(self, data, xoffset=0, yoffset=0):
        dataT = data.transpose()
        for col in range(dataT.shape[0]):
            key = None
            for row in range(dataT.shape[1]):
                if dataT[col][row] in self.nodeSymbols:
                    if key is None:
                        key = self.constructKey(col + xoffset, row + yoffset)
                    else:
                        otherkey = self.constructKey(col + xoffset, row + yoffset)
                        # Connect nodes up to down
                        self.nodesLUT[key].neighbors[DOWN] = self.nodesLUT[otherkey]
                        self.nodesLUT[otherkey].neighbors[UP] = self.nodesLUT[key]
                        key = otherkey
                elif dataT[col][row] not in self.pathSymbols:
                    key = None

    
    # NODE LOOKUP HELPERS
    def getNodeFromPixels(self, xpixel, ypixel):
        return self.nodesLUT.get((xpixel, ypixel), None)

    def getNodeFromTiles(self, col, row):
        x, y = self.constructKey(col, row)
        return self.nodesLUT.get((x, y), None)

    def getStartTempNode(self):
        # Return first node in dictionary (used for debugging)
        nodes = list(self.nodesLUT.values())
        return nodes[0]


    # CREATE GHOST HOUSE NODES
    def createHomeNodes(self, xoffset, yoffset):
        homedata = np.array([
            ['X','X','+','X','X'],
            ['X','X','.','X','X'],
            ['+','X','.','X','+'],
            ['+','.','+','.','+'],
            ['+','X','X','X','+']
        ])

        self.createNodeTable(homedata, xoffset, yoffset)
        self.connectHorizontally(homedata, xoffset, yoffset)
        self.connectVertically(homedata, xoffset, yoffset)

        # Entrance of ghost house
        self.homekey = self.constructKey(xoffset + 2, yoffset)
        return self.homekey


    # CONNECT GHOST HOUSE TO MAZE
    def connectHomeNodes(self, homekey, otherkey, direction):
        key = self.constructKey(*otherkey)
        self.nodesLUT[homekey].neighbors[direction] = self.nodesLUT[key]
        self.nodesLUT[key].neighbors[direction * -1] = self.nodesLUT[homekey]


    # ACCESS CONTROL HELPERS
    def denyAccess(self, col, row, direction, entity):
        node = self.getNodeFromTiles(col, row)
        if node:
            node.denyAccess(direction, entity)

    def allowAccess(self, col, row, direction, entity):
        node = self.getNodeFromTiles(col, row)
        if node:
            node.allowAccess(direction, entity)

    def denyAccessList(self, col, row, direction, entities):
        for entity in entities:
            self.denyAccess(col, row, direction, entity)

    def allowAccessList(self, col, row, direction, entities):
        for entity in entities:
            self.allowAccess(col, row, direction, entity)

    def denyHomeAccess(self, entity):
        self.nodesLUT[self.homekey].denyAccess(DOWN, entity)

    def allowHomeAccess(self, entity):
        self.nodesLUT[self.homekey].allowAccess(DOWN, entity)

    def denyHomeAccessList(self, entities):
        for entity in entities:
            self.denyHomeAccess(entity)

    def allowHomeAccessList(self, entities):
        for entity in entities:
            self.allowHomeAccess(entity)


    # DRAW ALL NODES (DEBUG)
    def render(self, screen):
        for node in self.nodesLUT.values():
            node.render(screen)
