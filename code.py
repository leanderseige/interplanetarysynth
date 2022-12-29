#
# Software of the Interplanetary Synth, (c) 2022, Leander Seige
# Released under the terms of the GNU GPL V3
# https://github.com/leanderseige/interplanetarysynth
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

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
syncin.pull = Pull.DOWN # None doesn't work for me

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

ledR.value = False # for some reason all pins work inverted for me
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

# global variables

rec_f = {} # recorded frequencies
rec_d = {} # duty cycles ar either 0x7fff or 0 for silence
rec_rc = 0 # recording counter
rec_pc = 0 # playback counter
recmode = "LIVE" # mode of operation

vf = 440
vd = 0x7fff

syncsignal = False # shows a rising edge on the sync signal
synctrigger = True # trigger looped playback

# functions

def play_sound(frequency, duty_cycle): # play a sound for us
    f = math.floor(apin.value/32)
    if f > 10000:
        f = 10000
    if f < 50:
        f = 50
    pwmspk1.frequency = frequency + f
    pwmspk1.duty_cycle = duty_cycle

def wait_sync():
    global syncsignal
    global synctrigger
    global recmode
    for x in range(5):
        if syncin.value==False: # inverted, we should have a switch for this
            # ledR.value = False # just for debugging
            # ledG.value = False
            # ledB.value = False
            if syncsignal==False: # detect rising edge
                syncsignal=True
                if synctrigger==False: # set flag
                    synctrigger=True
                    if recmode=="PLAY" and rec_pc==rec_rc:
                        return # w/o sleeping
        else:
            syncsignal=False
        time.sleep(.01)

while True:

    wait_sync()

    if touch1.raw_value > high1+10:
        vf = touch1.raw_value>>4
        vd = 0x7fff
    elif touch2.raw_value > high2+10:
        vf = touch2.raw_value>>2
        vd = 0x7fff
    elif touch3.raw_value > high3+10:
        vf = touch3.raw_value>>1
        vd = 0x7fff
    else:
        vd = 0

    if (not switch.value) and (recmode=="LIVE" or recmode=="PLAY"):
        # button was pressed but we don't know whether we are actually recording
        recmode="TESTREC"
        ledR.value = False
        ledG.value = True
        ledB.value = True
        rec_rc=0
        rec_f[rec_rc] = vf
        rec_d[rec_rc] = vd
        play_sound(vf,vd)
        if(vd>0): # we have actual input and start recording for real
            recmode="ACTIVEREC"
        rec_pc = 0
    elif (not switch.value) and (recmode=="TESTREC" or recmode=="ACTIVEREC"):
        # button is pressed and we are recording for real
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
        # live mode: nothing is recoded right now so we just play current input data
        recmode="LIVE"
        ledR.value = True
        ledG.value = True
        ledB.value = False
        play_sound(vf,vd)
        rec_rc=0
        rec_pc=0
    elif ((switch.value) and recmode=="ACTIVEREC") or recmode=="PLAY":
        # we are in playback mode
        recmode="PLAY"
        ledR.value = True
        ledG.value = False
        ledB.value = True
        if rec_pc<rec_rc: # play sequence
            # playback of recorded frequencies
            rec_pc = rec_pc+1
            play_sound(rec_f[rec_pc],rec_d[rec_pc])
            synctrigger=False # we got it
        elif rec_pc==rec_rc and synctrigger==True:
            # end of recording was reached and sync is true so we are going to restart playback
            rec_pc = 0 # restart
            play_sound(rec_f[rec_pc],rec_d[rec_pc])
            synctrigger=False # we got it
        else: # rec_pc==rec_rc and synctrigger==False
            # end of recording was reached but not sync signal happened, so we wait and play silence
            ledR.value = False
            ledG.value = True
            ledB.value = False
            play_sound(440,0) # silence
