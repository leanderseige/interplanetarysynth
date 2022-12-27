# import pulseio
import math
import pwmio
import board
import time
import touchio
from digitalio import DigitalInOut, Direction, Pull
import analogio

# init buttons

touch1 = touchio.TouchIn(board.A0)
touch2 = touchio.TouchIn(board.A1)
touch3 = touchio.TouchIn(board.A2)

# D1: init pwm (sound out)

pwmspk1 = pwmio.PWMOut(board.D1, duty_cycle=0x7fff, frequency=440, variable_frequency=True)

# D2: init potentiometer

apin = analogio.AnalogIn(board.A4) # this is D2

# D3: init sync in

syncin = DigitalInOut(board.D3)
syncin.direction = Direction.INPUT
syncin.pull = Pull.DOWN

# D4: init push switch

switch = DigitalInOut(board.D4)
switch.direction = Direction.INPUT
switch.pull = Pull.UP

# init LEDs

ledR = DigitalInOut(board.D6)
ledR.direction = Direction.OUTPUT
ledG = DigitalInOut(board.D5)
ledG.direction = Direction.OUTPUT
ledB = DigitalInOut(board.D7)
ledB.direction = Direction.OUTPUT

time.sleep(1)  # Sleep for a bit to avoid a race condition on some systems

# turn red = calibration

ledR.value = False
ledG.value = True
ledB.value = True

high1 = 0
high2 = 0
high3 = 0

# find low level

for x in range(0,20):
    v = touch1.raw_value
    if v > high1:
        high1 = v
    v = touch2.raw_value
    if v > high2:
        high2 = v
    v = touch3.raw_value
    if v > high3:
        high3 = v
    ledR.value = True
    time.sleep(.05)
    ledR.value = False
    time.sleep(.05)

high1 = int(high1*1.1)
high2 = int(high2*1.1)
high3 = int(high3*1.1)

# global variables

rec_f = {}
rec_d = {}
rec_rc = 0
rec_pc = 0
recmode = "LIVE"

vf = 440
vd = 0x7fff

syncsignal = False
synctrigger = True

# functions

def play_sound(frequency, duty_cycle):
    f = math.floor(apin.value/32)
    if f > 10000:
        f = 10000
    if f < 20:
        f= 20
    pwmspk1.frequency = frequency + f
    pwmspk1.duty_cycle = duty_cycle

def wait_sync():
    global syncsignal
    global synctrigger
    for x in range(4):
        if syncin.value==False: # inverted
            # ledR.value = False + just for debugging
            # ledG.value = False
            # ledB.value = False
            if syncsignal==False: # detect rising edge
                syncsignal=True
                if synctrigger==False: # set flag
                    synctrigger=True
                    return # w/o sleeping
        else:
            syncsignal=False
        time.sleep(.01)

while True:

    wait_sync()

    if touch1.raw_value > high1+20:
        vf = touch1.raw_value>>4
        vd = 0x7fff
    elif touch2.raw_value > high2+20:
        vf = touch2.raw_value>>2
        vd = 0x7fff
    elif touch3.raw_value > high3+20:
        vf = touch3.raw_value>>1
        vd = 0x7fff
    else:
        vd = 0

    if (not switch.value) and (recmode=="LIVE" or recmode=="PLAY"):
        recmode="TESTREC"
        ledR.value = False
        ledG.value = True
        ledB.value = True
        rec_rc=0
        rec_f[rec_rc] = vf
        rec_d[rec_rc] = vd
        play_sound(vf,vd)
        if(vd>0):
            recmode="ACTIVEREC"
        rec_pc = 0
    elif (not switch.value) and (recmode=="TESTREC" or recmode=="ACTIVEREC"):
        ledR.value = False
        ledG.value = True
        ledB.value = True
        rec_rc = rec_rc+1
        rec_f[rec_rc] = vf
        rec_d[rec_rc] = vd
        play_sound(vf,vd)
        if(vd>0):
            recmode="ACTIVEREC"
        rec_pc = 0
    elif ((switch.value) and recmode=="TESTREC") or recmode=="LIVE":
        recmode="LIVE"
        ledR.value = True
        ledG.value = True
        ledB.value = False
        play_sound(vf,vd)
        rec_rc=0
        rec_pc=0
    elif ((switch.value) and recmode=="ACTIVEREC") or recmode=="PLAY":
        recmode="PLAY"
        ledR.value = True
        ledG.value = False
        ledB.value = True
        if rec_pc<rec_rc: # play sequence
            rec_pc = rec_pc+1
            play_sound(rec_f[rec_pc],rec_d[rec_pc])
            synctrigger=False # we got it
        elif rec_pc==rec_rc and synctrigger==True: # end reached, sync is true => restart
            rec_pc = 0 # restart
            play_sound(rec_f[rec_pc],rec_d[rec_pc])
            synctrigger=False # we got it
        else: # rec_pc==rec_rc and synctrigger==False
            ledR.value = False
            ledG.value = True
            ledB.value = False
            play_sound(440,0) # silence
