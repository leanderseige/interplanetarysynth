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

apin = analogio.AnalogIn(board.A4)

# init LEDs

ledR = DigitalInOut(board.D6)
ledR.direction = Direction.OUTPUT
ledG = DigitalInOut(board.D5)
ledG.direction = Direction.OUTPUT
ledB = DigitalInOut(board.D7)
ledB.direction = Direction.OUTPUT

time.sleep(1)  # Sleep for a bit to avoid a race condition on some systems

# turn red = calibration

ledR.value = True
ledG.value = True
ledB.value = False

high1 = 0
high2 = 0
high3 = 0


def play_sound(frequency, duty_cycle):
    f = math.floor(apin.value/32)
    if f > 10000:
        f = 10000
    if f < 20:
        f= 20
    pwmspk1.frequency = frequency + f
    pwmspk1.duty_cycle = duty_cycle



# find low level

for x in range(0,100):
    v = touch1.raw_value
    if v > high1:
        high1 = v
    v = touch2.raw_value
    if v > high2:
        high2 = v
    v = touch3.raw_value
    if v > high3:
        high3 = v
    time.sleep(.01)

switch = DigitalInOut(board.D4)
switch.direction = Direction.INPUT
switch.pull = Pull.UP

# init PWMs
pwmspk1 = pwmio.PWMOut(board.D1, duty_cycle=0x7fff, frequency=440, variable_frequency=True)
# pwmspk2 = pulseio.PWMOut(board.D2, duty_cycle=0x7fff, frequency=440, variable_frequency=True)
# pwmspk3 = pulseio.PWMOut(board.D3, duty_cycle=0x7fff, frequency=440, variable_frequency=True)

# use button values to set freqency, no sound if near low level

rec_f = {}
rec_d = {}
rec_rc = 0
rec_pc = 0
recmode = "LIVE"

vf = 440
vd = 0x7fff

while True:
    time.sleep(.04)
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

    # pwmspk1.frequency = vf
    # pwmspk1.duty_cycle = vd

    #  trigge r

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
        rec_rc = rec_rc + 1
        rec_f[rec_rc] = vf
        rec_d[rec_rc] = vd
        play_sound(vf,vd)
        if(vd>0):
            recmode="ACTIVEREC"
        rec_pc = 0
    elif ((switch.value) and recmode=="TESTREC") or recmode=="LIVE":
        ledR.value = True
        ledG.value = True
        ledB.value = False
        play_sound(vf,vd)
        recmode="LIVE"
        rec_rc=0
        rec_pc=0
    elif ((switch.value) and recmode=="ACTIVEREC") or recmode=="PLAY":
        ledR.value = True
        ledG.value = False
        ledB.value = True
        play_sound(rec_f[rec_pc],rec_d[rec_pc])
        rec_pc = rec_pc+1
        rec_pc = rec_pc%rec_rc
        recmode="PLAY"
