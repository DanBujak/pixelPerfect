#!/usr/bin/python
import json

with open('settings.json') as settings_file:
    settings = json.load(settings_file)

import numpy as np
import datetime
import sys
import time
import frameGen
import audio
import clockFunc
import pyscreenshot as ImageGrab
from datetime import timedelta
from PIL import Image
#from Image import ANTIALIAS
from globalConfigs import *
from configs import *
from clockParams import *
from instagramParams import * 
from emulator import *
from pprint import pprint

# ------------------- User Configurations ----------------
SERIAL_PORT		= settings["serial"]["port"]	# PC COM Port - 1
PANEL_ENABLE		= settings["panel_enabled"]	# Enable/Disable UART Output
EMULATOR_ENABLE		= settings["emulator_enabled"]	# Enable/Disable Emulator
TEST_MODE		= settings["test_mode"]
FPS			= settings["fps"]		# Frame Rate
GRID_SIZE		= settings["grid_size"]		# Display resolution ( n x n )
PIXEL_SIZE		= settings["pixel_size"]	# Size of each pixel for emulator (in pixels)
PIXEL_STYLE		= settings["pixel_style"]	# Emulator pixel style
# ------------------- Visbul Variables ----------------
VISIBUL_X_PIX		= settings["visibul"]["x"]
VISIBUL_Y_PIX		= settings["visibul"]["y"]
VISIBUL_GRID_SIZE	= settings["visibul"]["grid_size"]
VISIBUL_COLUMNS		= settings["visibul"]["columns"] - 1
VISIBUL_ROWS		= settings["visibul"]["rows"] - 1
VISIBUL_CYCLE_TIME	= settings["visibul"]["cycle_time"]

# ------------------- Global Variables ----------------
LastState = STATE_CLOCK
CurrentState = STATE_CLOCK
NextState = STATE_CLOCK
StateCounter = 0
sdOverride = False
visibullCycle = False
    
State = {
    0: STATE_CLOCK,
    1: STATE_VISIBULL,
    2: STATE_INSTAGRAM,
    3: STATE_CUSTOM,
    4: STATE_SHUTDOWN
}

StateText = {
    0: "Clock",
    1: "Visibull",
    2: "Instagram",
    3: "Custom"
}

wakeupTime = datetime.time(WAKEUP_TIME/100, WAKEUP_TIME%100)
sleepTime = datetime.time(SHUTDOWN_TIME/100, SHUTDOWN_TIME%100)

# Instagram Image persistence counter
imagePersist = 0

def Initialize_UART():
    # Only need serial if panel is connected 
    if (PANEL_ENABLE == True):
        import serial
        serPort = serial.Serial(SERIAL_PORT - 1, BAUD, timeout = 1)  # open first serial port
    else:
        serPort = None
    
    return serPort

def Transition_State(nextState):
    if (nextState == STATE_CLOCK):
        FPS = 10
    elif (nextState == STATE_INSTAGRAM):
        FPS = 10
    elif (nextState == STATE_VISIBULL):
        FPS = 10
    elif (nextState == STATE_CUSTOM):
        FPS = 20
    elif (nextState == STATE_SHUTDOWN):
        FPS = 1

def addMins(tm, mins):
    fulldate = datetime.datetime(100, 1, 1, tm.hour, tm.minute, tm.second)
    fulldate = fulldate + datetime.timedelta(minutes=mins)
    return fulldate.time()

def toggleDisplay(state):
    global LastState, CurrentState, NextState, sdOverride
    
    if (CurrentState == STATE_SHUTDOWN):
	NextState = LastState
	sdOverride = False
	print "Wakeup"
    else:
	NextState = STATE_SHUTDOWN
	LastState = state
	sdOverride = True
	print "Sleep"
    pass

def cycleState():
    global NextState, StateCounter
    
    StateCounter = StateCounter + 1
    
    if (StateCounter > 2):
	StateCounter = 0
    
    NextState = State[StateCounter]
    
    print "Current State: " + StateText[StateCounter]

def cycleVisibulGrid():
    global CurrentFrameX, CurrentFrameY, VISIBUL_COLUMNS, VISIBUL_ROWS
    
    CurrentFrameX = CurrentFrameX + 1
    
    if (CurrentFrameX > VISIBUL_COLUMNS):
	CurrentFrameY = CurrentFrameY + 1
	CurrentFrameX = 0
    
    if (CurrentFrameY > VISIBUL_ROWS):
	CurrentFrameY = 0
'''
Main function- maintains display
'''
if __name__ == '__main__':
    # Create Clock instance
    clock = pygame.time.Clock()
    
    # Create COM port instance 
    comPort = Initialize_UART()
    
    # Create instance of display
    sim1 = displaySim(GRID_SIZE, PIXEL_SIZE, PIXEL_STYLE)

    # Frame that gets written on each refresh
    writeFrame = frameGen.blank_frame('000000')
    
    # Time variable 
    currentTime = datetime.datetime.now().time()

    # Capture Area
    ssX =     VISIBUL_X_PIX
    ssY =     VISIBUL_Y_PIX
    ssBox = (ssX, ssY, ssX + GRID_SIZE, ssY + GRID_SIZE)
    
    CurrentFrameX = 0
    CurrentFrameY = 0
    
    # Create instance of display
    sim1 = displaySim(GRID_SIZE, PIXEL_SIZE, PIXEL_STYLE)

    print "Wakeup Time " + str(wakeupTime)
    print "Sleep Time: " + str(sleepTime)
    print ""
    print "Current State: " + StateText[StateCounter]

    # Create Timer
    startTime = int(time.time())
    lastInterval = startTime

    # ------------------------- Main Loop ------------------------------
    while(1):
        
    #>> Pre-State Global Actions ---------------------------------------

        # Update time variable
        if (TEST_MODE == 0):
            currentTime = datetime.datetime.now().time()
        else:
            currentTime =  addMins(currentTime, 1)

    #>> Check for state change
        if (CurrentState != NextState):
            # print("Transition required")
            # print currentTime
            # print str(CurrentState) + ">>" + str(NextState)
            Transition_State(NextState)
            CurrentState = NextState


    #>> Service current state 

        # - >> Clock Display << ----------------------------------------
        if (CurrentState == STATE_CLOCK):
            bgColor = clockFunc.Time_to_Colour(currentTime)

            # Generate clock frame
            writeFrame = frameGen.blank_frame(bgColor)
            writeFrame = clockFunc.generate_clock_frame(currentTime, writeFrame, np, '000000')
        
        # - >> Visibull << ---------------------------------------------
        
        elif (CurrentState == STATE_VISIBULL):
			ssBox = (ssX, ssY, ssX + GRID_SIZE, ssY + GRID_SIZE)

			screenShot = ImageGrab.grab(ssBox)
			#thumb = screenShot.resize((GRID_SIZE,GRID_SIZE), ANTIALIAS)
			writeFrame = np.array(screenShot)

			# Update panel data and send to serial port if panel is connected
			#sim1.updateCells(writeFrame, PANEL_ENABLE, comPort)
        
        # - >> Instagram Mode << ---------------------------------------
        elif (CurrentState == STATE_INSTAGRAM):
            #print "Audio"
            audioData = audio.generateSample()
            writeFrame = frameGen.audio_frame(audioData)
        
        # - >> Custom Mode << ---------------------------------------
        elif (CurrentState == STATE_CUSTOM):
            print "State Not Yet Available"
        
        # - >> Shutdown State << ---------------------------------------
        elif (CurrentState == STATE_SHUTDOWN):
	    writeFrame = frameGen.blank_frame(COLOUR_BLACK)

    #>> Post-State Global Actions --------------------------------------

        # Update panel data and send to serial port if panel is connected
        sim1.updateCells(writeFrame, PANEL_ENABLE, comPort)
        
        # If using emulator then update emulator
        if (EMULATOR_ENABLE == True):
            sim1.redraw()
            pygame.display.flip()

        events = pygame.event.get()
        for e in events:
	    if (e.type == KEYDOWN):
		# print "Key Code: " + str(e.key)
		
		mods = pygame.key.get_mods()
		
		# Toggle Display On/Off
		if (e.key == 261 or e.key == 32): # Space Key (5)
		    toggleDisplay(CurrentState)
		
		if (CurrentState == STATE_VISIBULL):
		    # Adjust Visibull Screen Capture (Numpad Arrows)
		    if (e.key == 260 or e.key == 276): # Left (4)
			if mods & pygame.KMOD_NUM or mods & pygame.KMOD_SHIFT:
			    VISIBUL_X_PIX = VISIBUL_X_PIX - 1
			    print "(X,Y) = (" + str(VISIBUL_X_PIX) + "," + str(VISIBUL_Y_PIX)
			else:
			    VISIBUL_X_PIX = VISIBUL_X_PIX - VISIBUL_GRID_SIZE
		    if (e.key == 262 or e.key == 275): # Right (6)
			if mods & pygame.KMOD_NUM or mods & pygame.KMOD_SHIFT:
			    VISIBUL_X_PIX = VISIBUL_X_PIX + 1
			    print "(X,Y) = (" + str(VISIBUL_X_PIX) + "," + str(VISIBUL_Y_PIX)
			else:
			    VISIBUL_X_PIX = VISIBUL_X_PIX + VISIBUL_GRID_SIZE
		    if (e.key == 264 or e.key == 273): # Up (8)
			if mods & pygame.KMOD_NUM or mods & pygame.KMOD_SHIFT:
			    VISIBUL_Y_PIX = VISIBUL_Y_PIX - 1
			    print "(X,Y) = (" + str(VISIBUL_X_PIX) + "," + str(VISIBUL_Y_PIX)
			else:
			    VISIBUL_Y_PIX = VISIBUL_Y_PIX - VISIBUL_GRID_SIZE
		    if (e.key == 258 or e.key == 274): # Down (2)
			if mods & pygame.KMOD_NUM or mods & pygame.KMOD_SHIFT:
			    VISIBUL_Y_PIX = VISIBUL_Y_PIX + 1
			    print "(X,Y) = (" + str(VISIBUL_X_PIX) + "," + str(VISIBUL_Y_PIX)
			else:
			    VISIBUL_Y_PIX = VISIBUL_Y_PIX + VISIBUL_GRID_SIZE
		
		    # Pause/Resume Visibull Cycle
		    if (e.key == 256 or e.key == 112): # P (0)
			visibullCycle = not visibullCycle
			if (visibullCycle):
			    print "Starting Visibul Grid Cycle"
			    CurrentFrameX = 0
			    CurrentFrameY = 0
			else:
			    print "Stopping Visibul Grid Cycle"
		    
		    if ((e.key == 99 or e.key == 266) and not visibullCycle): #C (.)
			cycleVisibulGrid()
		
		# Cycle Dislay Mode
		if (e.key == 271 or e.key == 9): # Enter
		    cycleState()
		
        clock.tick(FPS)     # Main Loop
	
	if (CurrentState == STATE_VISIBULL):
	    currentTime = int(time.time())
	    
	    if (visibullCycle) and ((currentTime - startTime) % 5 == 0) and (currentTime != lastInterval):
		lastInterval = currentTime
		cycleVisibulGrid()
	    
	    ssX = VISIBUL_X_PIX + (CurrentFrameX * VISIBUL_GRID_SIZE)
	    ssY = VISIBUL_Y_PIX + (CurrentFrameY * VISIBUL_GRID_SIZE)

    
#TODO
# Shutdown override button
# state change button (hold button to cycle through ON, OFF, AUTO)
