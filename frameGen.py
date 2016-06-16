#!/usr/bin/python

from globalConfigs import *
import numpy as np
from time import sleep

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
    LOW_COLOUR = "003F00"
    MID_COLOUR = "3F3F00"
    HIGH_COLOUR = "3F0000"

    outputArray = blank_frame(HIGH_COLOUR)

    for col in range(0,GRID_SIZE):
        #print "C: " + str(col)
        for row in range(GRID_SIZE-sample[col], GRID_SIZE):
            #print "\tR: " + str(row)
            outputArray[row,col] = [255, 0, 0]
        #sleep (1)
    
    return outputArray

#'''
#Main function- maintains display
#'''
#if __name__ == '__main__':
#
#    mylist = range(0,31)
#    print mylist
#    audio_frame(mylist)
