# Memory Puzzle
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random, pygame, sys
from pygame.locals import *



FPS = 3 # frames per second, the general speed of the program
#            R    G    B
GRAY     = (100, 100, 100)
NAVYBLUE = ( 60,  60, 100)
WHITE    = (255, 255, 255)
RED      = (255,  50,  50)
GREEN    = (  0, 255,   0)
BLUE     = (  0,   0, 255)
YELLOW   = (255, 255,   0)
ORANGE   = (255, 128,   0)
PURPLE   = (255,   0, 255)
CYAN     = (  0, 255, 255)
BLACK    = (  0,   0,   0)

BGCOLOR = WHITE
LIGHTBGCOLOR = GRAY
BOXCOLOR = BLACK
HIGHLIGHTCOLOR = BLUE

BORDER_WIDTH =  5

RED_INDEX =     0
BLUE_INDEX =    1
GREEN_INDEX =   2

SQUARE = 'square'
CIRCLE = 'circle'

SERIAL_PORT = 10
BAUD = 800000
COLOURSPACE = 'BRG'
ALPHA = 0.75

class cell:
    
    def __init__(self, x1, y1, x2, y2, colour = NAVYBLUE):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.colour = colour
        self.rect = (x1, y1, (x2-x1), (y2-y1))

class displaySim:
    def __init__(self, gridSize, pixelSize, shape):
        windowSize = (gridSize * pixelSize) + (BORDER_WIDTH * 2)
        pygame.init()
        
        self.gridSize = gridSize
        self.pixelSize = pixelSize 
        self.shape = shape
        
        # ---------- Main Screen
        self.screen = pygame.display.set_mode(( windowSize, windowSize))
        self.screen.fill(BGCOLOR)
        pygame.display.set_caption('RGB Dot Matrix Sim by @Dan_Bujak')

        # ---------- Grid
        
        # Border
        pygame.draw.rect(self.screen, BOXCOLOR, (0,0, windowSize - 1, windowSize -1),BORDER_WIDTH) 
        # Cells
        self.board = [[cell(i * pixelSize + BORDER_WIDTH + 1, j * pixelSize + + BORDER_WIDTH + 1, (i + 1) * pixelSize + BORDER_WIDTH -1, (j + 1) * pixelSize + BORDER_WIDTH -1) for i in range(gridSize)] for j in range(gridSize)]
        # Bezels
        for i in range(self.gridSize):
            for j in range(self.gridSize):
                if (self.shape == SQUARE):
                    pygame.draw.rect(self.screen, LIGHTBGCOLOR, (i * pixelSize + BORDER_WIDTH, j * pixelSize + + BORDER_WIDTH, pixelSize -1, pixelSize -1))
                elif (self.shape == CIRCLE):
                    print "circle not implemented"
                    #pygame.draw.circl(self.screen, LIGHTBGCOLOR, (i * pixelSize + BORDER_WIDTH, j * pixelSize + + BORDER_WIDTH, pixelSize -1, pixelSize -1))

    def updateCells(self, dataArray, toPanel = False, serPort = None):
        txBuff = '' 
        tempBuff = ''
        
        for i in range(self.gridSize):
            for j in range(self.gridSize):
                self.board[i][j].colour = dataArray[i][j][RED_INDEX], dataArray[i][j][BLUE_INDEX], dataArray[i][j][GREEN_INDEX]
                if (i%2 == 0):
                    txBuff += chr(int(dataArray[i][j][BLUE_INDEX] * ALPHA)) + chr(int(dataArray[i][j][RED_INDEX] * ALPHA)) + chr(int(dataArray[i][j][GREEN_INDEX] * ALPHA))
            # Odd rows need to be built in reverse order for physical panel. If we're on an odd row overwrite existing buffer
            if (i%2 !=0):
                for j in range(self.gridSize - 1, -1 , -1):
                    txBuff += chr(int(dataArray[i][j][BLUE_INDEX] * ALPHA)) + chr(int(dataArray[i][j][RED_INDEX] * ALPHA)) + chr(int(dataArray[i][j][GREEN_INDEX] * ALPHA))
            
        if (toPanel == True):            
            serPort.write(txBuff) 
                    

    def redraw(self):
        for i in range(self.gridSize):
            for j in range(self.gridSize):
                pygame.draw.rect(self.screen, self.board[i][j].colour, self.board[i][j].rect)
        
