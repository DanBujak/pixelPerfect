#!/usr/bin/python

from globalConfigs import *
import numpy as np
from configs import COLOUR_BLACK, COLOUR_WHITE

''' colour = 'FF00FF' '''
def blank_frame(colour):
    
    rowArray = []
    frameArray = []
    
    r = int(colour[0:2], 16)
    g = int(colour[2:4], 16)
    b = int(colour[4:6], 16)

    for row in range(0, GRID_SIZE):

        for cell in range(0, GRID_SIZE):
            rowArray.append([r,g,b])

        frameArray.append(rowArray)
        rowArray = []
    
    return np.array(frameArray)

def test_pattern(colour):
    rowArray = []
    frameArray = []
    
    r = int(colour[0:2], 16)
    g = int(colour[2:4], 16)
    b = int(colour[4:6], 16)

    for row in range(0, GRID_SIZE):
        for cell in range(0, GRID_SIZE/2):
            rowArray.append([0,0,0])
        for cell in range(0, GRID_SIZE/2):
            rowArray.append([r,g,b])

        frameArray.append(rowArray)
        rowArray = []

    return np.array(frameArray)

''' Pass in an audio sample which is a list of GRID_SIZE values from 0 to 
    GRID_SIZE (ie amplitudes) for the frequency band being sampled. '''
def audio_frame(sample):
    #print sample
    COLOURS = [ [   40, 96,  55 ], 
                [  57, 108,  55 ], 
                [  72, 117,  55 ], 
                [  87, 128,  55 ], 
                [ 102, 138,  55 ], 
                [ 118, 149,  55 ], 
                [ 133, 160,  55 ], 
                [ 148, 171,  55 ], 
                [ 163, 181,  55 ], 
                [ 179, 192,  55 ], 
                [ 209, 213,  55 ], 
                [ 224, 224,  55 ], 
                [ 239, 235,  55 ], 
                [ 255, 246,  55 ], 
                [ 255, 246,  55 ],
                [ 254, 229,  52 ], 
                [ 254, 213,  48 ], 
                [ 254, 197,  44 ], 
                [ 254, 180,  40 ],
                [ 254, 164,  36 ], 
                [ 254, 148,  32 ], 
                [ 254, 132,  28 ], 
                [ 254, 115,  24 ], 
                [ 254,  99,  20 ], 
                [ 254,  83,  16 ], 
                [ 254,  66,  12 ], 
                [ 254,  50,   8 ], 
                [ 254,  34,   4 ], 
                [ 254,  18,   0 ],                
                [ 254,   2,   0 ] ]

    outputArray = blank_frame(COLOUR_BLACK)

    for col in range(0,GRID_SIZE):
        for row in range(GRID_SIZE-sample[col], GRID_SIZE):
            outputArray[row,col] = COLOURS[col]

    return outputArray

#'''
#Main function- maintains display
#'''
#if __name__ == '__main__':
#
#    mylist = range(0,31)
#    print mylist
#    audio_frame(mylist)
