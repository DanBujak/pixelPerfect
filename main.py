#!/usr/bin/python
import json

with open('settings.json') as settings_file:
    settings = json.load(settings_file)

# System Modules
import datetime
import sys
import time
from datetime import timedelta
# PixelPerfext Modules
import frameGen
import clockFunc
from configs import *
from clockParams import *
from emulator import *
from pprint import pprint
import wx
#Audio Imports
from PIL import Image
import numpy as np
import pyaudio
from scipy.fftpack import fft

# ------------------- User Configurations ----------------
SERIAL_PORT        = settings["serial"]["port"]    # PC COM Port - 1
PANEL_ENABLE        = settings["panel_enabled"]    # Enable/Disable UART Output
EMULATOR_ENABLE        = settings["emulator_enabled"]    # Enable/Disable Emulator
TEST_MODE        = settings["test_mode"]
FPS            = settings["fps"]        # Frame Rate
GRID_SIZE        = settings["grid_size"]        # Display resolution ( n x n )
PIXEL_SIZE        = settings["pixel_size"]    # Size of each pixel for emulator (in pixels)
PIXEL_STYLE        = settings["pixel_style"]    # Emulator pixel style
# ------------------- Visbul Variables ----------------
VISIBUL_X_PIX        = settings["visibul"]["x"]
VISIBUL_Y_PIX        = settings["visibul"]["y"]
VISIBUL_GRID_SIZE    = settings["visibul"]["grid_size"]
VISIBUL_COLUMNS        = settings["visibul"]["columns"] - 1
VISIBUL_ROWS        = settings["visibul"]["rows"] - 1
VISIBUL_CYCLE_TIME    = settings["visibul"]["cycle_time"]


# -------------------- Audio Configs ------------------
MAX_AMPLITUDE = settings["audio"]["max_amplitude"]      # Maximum audio level to clip at
AUDIO_RATE = settings["audio"]["audio_rate"]            # Sampling frequency of audio
VIDEO_RATE = 25                                         # Frame rate of display (should be set dynamically based on existing user config)
FORMAT = pyaudio.paInt16                                # Audio bit depth
CHANNELS = 1                                            # Number of audio channels to record
CHUNK = AUDIO_RATE/VIDEO_RATE                           # Set 1 CHUNK to be 1 video frame's worth of data
INTERVAL = int(CHUNK/2/GRID_SIZE)                       # Interval size to average entire audio spectrum on to map it into our grid size

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
    2: STATE_AUDIO,
    3: STATE_SHUTDOWN
}

StateText = {
    0: "Clock",
    1: "Visibull",
    2: "Audio"
}

wakeupTime = datetime.time(WAKEUP_TIME/100, WAKEUP_TIME%100)
sleepTime = datetime.time(SHUTDOWN_TIME/100, SHUTDOWN_TIME%100)
sleepOverride = False

# Open sound stream from default mic 
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
    channels=CHANNELS,
    rate=AUDIO_RATE,
    input=True,
    frames_per_buffer=CHUNK)

'''
Capture the audio, filter it, run fft and split it into 30 bands
'''
def generateSample():
    processedSamples = []
    dataOut = []
    scaledData = []
    
    nextSample = stream.read(CHUNK)
    nextSample = np.fromstring(nextSample, dtype=np.int16)
    npSample = np.hstack(nextSample)
    
    # this is 8-bit track, b is now normalized on [-1,1)
    #b =[(ele/2**8.)*2-1 for ele in npSample] 
    for e in npSample:
        processedSamples.append((float( e / 2**8) * 2) - 1)

    # calculate fourier transform (complex numbers list)
    processedSamples = fft(processedSamples) 
    
    # Calculate absolute values of processed sampels
    processedSamples = map(np.absolute, processedSamples)
    
    # Divide the audio input range into GRID_SIZE number of ranges and
    # take the average of each of the groups. Map the average amplitude
    # to the range of our resolution and round to nearest int
    start = 0
    end = INTERVAL
    for o in range(0,GRID_SIZE):
        start = start + INTERVAL
        end = end + INTERVAL
        nextAmplitude = np.mean(processedSamples[start:end])
        nextAmplitude = int((nextAmplitude /MAX_AMPLITUDE) * GRID_SIZE)
        scaledData.append(min(nextAmplitude, GRID_SIZE))
    return scaledData

'''
Initialize UART connection
'''
def Initialize_UART():
    # Only need serial if panel is connected 
    if (PANEL_ENABLE == True):
        import serial
        serPort = serial.Serial(SERIAL_PORT - 1, BAUD, timeout = 1)  # open serial port
    else:
        serPort = None
    
    return serPort

'''
Set framerate and state variable on transition
'''
def Transition_State(nextState):
    global FPS

    if (nextState == STATE_CLOCK):
        FPS = 5
    elif (nextState == STATE_AUDIO):
        FPS = VIDEO_RATE
    elif (nextState == STATE_VISIBULL):
        FPS = 25
    elif (nextState == STATE_SHUTDOWN):
        FPS = 1

'''
Debug function to test clock
'''
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

'''
Automatically cycle through visibull displays
'''
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
    # Create an App instance for screen capture
    wxInstance = wx.App()
    screen = wx.ScreenDC()
    
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
    ssX = VISIBUL_X_PIX
    ssY = VISIBUL_Y_PIX
    
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
        # Put the panel to sleep durring sleep hours unless the override is enabled
        if ((currentTime < wakeupTime or currentTime > sleepTime) and not sleepOverride):
            writeFrame = frameGen.blank_frame(COLOUR_BLACK)
        else:
            # Reset the sleep override during waking hours
            if ((currentTime > wakeupTime and currentTime < sleepTime) and sleepOverride):
                sleepOverride = False
            
            # - >> Clock Display << ----------------------------------------
            if (CurrentState == STATE_CLOCK):
                bgColor = clockFunc.Time_to_Colour(currentTime)

                # Generate clock frame
                writeFrame = frameGen.blank_frame(bgColor)
                writeFrame = clockFunc.generate_clock_frame(currentTime, writeFrame, np, '000000')
            
            # - >> Visibull << ---------------------------------------------
            
            elif (CurrentState == STATE_VISIBULL):
                bmp = wx.EmptyBitmap(GRID_SIZE, GRID_SIZE)  
                memory = wx.MemoryDC(bmp)
                memory.Blit(0, 0, GRID_SIZE, GRID_SIZE, screen, ssX, ssY)
                del memory
                myWxImage = wx.ImageFromBitmap( bmp )
                img = Image.frombytes('RGB', (GRID_SIZE, GRID_SIZE), myWxImage.GetData())
                writeFrame = np.array(np.array(img))
                
                ##Update panel data and send to serial port if panel is connected
                sim1.updateCells(writeFrame, PANEL_ENABLE, comPort)
                
                #if (CurrentState == STATE_VISIBULL):
                currentTime = int(time.time())
                
                # Periodically cycle through visibull images if enabled
                if (visibullCycle) and ((currentTime - startTime) % 5 == 0) and (currentTime != lastInterval):
                    lastInterval = currentTime
                    cycleVisibulGrid()
                
                # Update screen capture location
                ssX = VISIBUL_X_PIX + (CurrentFrameX * VISIBUL_GRID_SIZE)
                ssY = VISIBUL_Y_PIX + (CurrentFrameY * VISIBUL_GRID_SIZE)                
                    
            # - >> Audio Mode << -------------------------------------------
            elif (CurrentState == STATE_AUDIO):
                audioData = generateSample()
                writeFrame = frameGen.audio_frame(audioData)

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
                #print "Key Code: " + str(e.key)

                mods = pygame.key.get_mods()
                
                # Toggle Display On/Off
                if (e.key == 261 or e.key == 32): # Space Key (5)
                    toggleDisplay(CurrentState)
                
                # Toggle Sleep Override
                if (e.key == 111 or e.key == 268): # O (*)
                    sleepOverride = not sleepOverride
                    print "Sleep Override: " + str(sleepOverride)
                    
                if (CurrentState == STATE_VISIBULL):
                    # Adjust Visibull Screen Capture (Numpad Arrows)
                    if (e.key == 260 or e.key == 276): # Left (4)
                        if (mods & pygame.KMOD_NUM or mods & pygame.KMOD_SHIFT):
                            VISIBUL_X_PIX = VISIBUL_X_PIX - 1
                        else:
                            VISIBUL_X_PIX = VISIBUL_X_PIX - VISIBUL_GRID_SIZE
                    if (e.key == 262 or e.key == 275): # Right (6)
                        if mods & pygame.KMOD_NUM or mods & pygame.KMOD_SHIFT:
                            VISIBUL_X_PIX = VISIBUL_X_PIX + 1
                        else:
                            VISIBUL_X_PIX = VISIBUL_X_PIX + VISIBUL_GRID_SIZE
                    if (e.key == 264 or e.key == 273): # Up (8)
                        if mods & pygame.KMOD_NUM or mods & pygame.KMOD_SHIFT:
                            VISIBUL_Y_PIX = VISIBUL_Y_PIX - 1
                        else:
                            VISIBUL_Y_PIX = VISIBUL_Y_PIX - VISIBUL_GRID_SIZE
                    if (e.key == 258 or e.key == 274): # Down (2)
                        if mods & pygame.KMOD_NUM or mods & pygame.KMOD_SHIFT:
                            VISIBUL_Y_PIX = VISIBUL_Y_PIX + 1
                        else:
                            VISIBUL_Y_PIX = VISIBUL_Y_PIX + VISIBUL_GRID_SIZE

                    print "(X,Y) = (" + str(VISIBUL_X_PIX) + "," + str(VISIBUL_Y_PIX)
                
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
                if (e.key == 271 or e.key == 9): # Tab (Enter)
                    StateCounter = StateCounter + 1
    
                    if (StateCounter > 2):
                        StateCounter = 0
                    
                    NextState = State[StateCounter]
                    
                    print "Current State: " + StateText[StateCounter]
        
        #Maintain Framefrate
        clock.tick(FPS)
