#!/usr/bin/python

from clockParams import *
from configs import *
import datetime
from decimal import Decimal


timeAM = datetime.time(TIME_AM/100, TIME_AM%100)
timeNoon = datetime.time(TIME_NOON/100, TIME_NOON%100)
timePM = datetime.time(TIME_PM/100, TIME_PM%100)
timeNight = datetime.time(TIME_NIGHT/100, TIME_NIGHT%100)

'''Set background colour based on time of day'''
def Time_to_Colour(currentTime):
    
    if (currentTime < timeAM):
        return COLOR_NIGHT
    elif (currentTime < timeNoon):
        t1 = timeAM
        t2 = timeNoon
        color1 = COLOR_AM
        color2 = COLOR_NOON
    elif (currentTime < timePM):
        t1 = timeNoon
        t2 = timePM
        color1 = COLOR_NOON
        color2 = COLOR_PM
    elif (currentTime < timeNight):
        t1 = timePM        
        t2 = timeNight
        color1 = COLOR_PM
        color2 = COLOR_NIGHT
    else:
        return COLOR_OFF


    t1 = (t1.hour * 3600) + (t1.minute * 60) + t1.second
    t2 = (t2.hour * 3600) + (t2.minute * 60) + t2.second

    currentTime = (currentTime.hour * 3600) + (currentTime.minute * 60) + currentTime.second

    percent = round(100 * Decimal(currentTime - t1) / Decimal(t2 - t1), 2)

    return Colour_Gradient(color1, color2, percent)


'''Gradient colour based on 2 colours and percentage between them'''
def Colour_Gradient(color1, color2, percent):

    r1 = int(color1[0:2], 16)
    g1 = int(color1[2:4], 16)
    b1 = int(color1[4:6], 16)

    r2 = int(color2[0:2], 16)
    g2 = int(color2[2:4], 16)
    b2 = int(color2[4:6], 16)
    
    r = r1 + ((r2 - r1) * percent /100)
    g = g1 + ((g2 - g1) * percent /100)
    b = b1 + ((b2 - b1) * percent /100)
    
    #print ("%0.2X" % r) + ("%0.2X" % g) + ("%0.2X" % b)
    
    return ("%0.2X" % r) + ("%0.2X" % g) + ("%0.2X" % b)

''' Augment a blank background frame with current time digits '''
def generate_clock_frame(currentTime, clockFrame, np, colour):
    r = int(colour[0:2], 16)
    g = int(colour[2:4], 16)
    b = int(colour[4:6], 16)
    onPixel = np.array([r,g,b])
    
    #Hour 1
    digit = np.array(LARGE_NUMBERS[int(currentTime.hour / 10)])
    for y in range (0, HOUR_DIGIT_Y):
        for x in range(0, HOUR_DIGIT_X):
            if (digit[y,x] == 1):
                clockFrame[y + HOUR1_Y, x + HOUR1_X] = onPixel

    #Hour 2
    digit = np.array(LARGE_NUMBERS[currentTime.hour % 10])
    for y in range (0, HOUR_DIGIT_Y):
        for x in range(0, HOUR_DIGIT_X):
            if (digit[y,x] == 1):
                clockFrame[y + HOUR2_Y, x + HOUR2_X] = onPixel

    #Minute 1
    digit = np.array(MEDIUM_NUMBERS[int(currentTime.minute / 10)])
    for y in range (0, MIN_DIGIT_Y):
        for x in range(0, MIN_DIGIT_X):
            if (digit[y,x] == 1):
                clockFrame[y + MIN1_Y, x + MIN1_X] = onPixel

    #Minute 2
    digit = np.array(MEDIUM_NUMBERS[currentTime.minute % 10])
    for y in range (0, MIN_DIGIT_Y):
        for x in range(0, MIN_DIGIT_X):
            if (digit[y,x] == 1):
                clockFrame[y + MIN2_Y, x + MIN2_X] = onPixel

    #Second 1
    digit = np.array(SMALL_NUMBERS[int(currentTime.second / 10)])
    for y in range (0, SEC_DIGIT_Y):
        for x in range(0, SEC_DIGIT_X):
            if (digit[y,x] == 1):
                clockFrame[y + SEC1_Y, x + SEC1_X] = onPixel

    #Second 2
    digit = np.array(SMALL_NUMBERS[currentTime.second % 10])
    for y in range (0, SEC_DIGIT_Y):
        for x in range(0, SEC_DIGIT_X):
            if (digit[y,x] == 1):
                clockFrame[y + SEC2_Y, x + SEC2_X] = onPixel
                
    return clockFrame
