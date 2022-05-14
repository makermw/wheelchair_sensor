# Wheelchar reversing sensor using pi pico microcontroller
# save to main.py on pico to run automatically
# Matt Westmore, v1.2 2022.02.15- external power switch

from machine import Pin, PWM
import utime

DEBUG = 0 # DEBUG levels change at 0,10,100. 0 = silent running

#initialise i/o
buzzer=PWM(Pin(14))
led = Pin(25, Pin.OUT)
power = [Pin(1, Pin.OUT), Pin(1, Pin.OUT)]
trigger = [Pin(3, Pin.OUT), Pin(3, Pin.OUT)]
echo = [Pin(2, Pin.IN), Pin(2, Pin.IN)]

# define constants
DELAY = 100 #ms deault time between distance checks
MAXDIST = 70 # cm if MINDIST < distance < MAXDIST iintermittent beeping 
MINDIST = 15 # cm if distance < MINDIST continuous tone will be heard 

#set up buzzer funnctions.Assumes PWM buzzer
def playtone(frequency):
    # play a tone. Duty cycle sets volume, fewq sets tone
    buzzer.duty_u16(3000)
    buzzer.freq(frequency)

def bequiet():
    # turns buzzer off
    buzzer.duty_u16(0)
    
def renormalise(n, range1, range2):
    # renormalises a number from range1 to range2
    delta1 = range1[1] - range1[0]
    delta2 = range2[1] - range2[0]
    return (delta2 * (n - range1[0]) / delta1) + range2[0]

def ultra(sensor):
    # senses distance
    if DEBUG > 10: print ("ultra sensor "+str(sensor))
    trigger[sensor].low()
    utime.sleep_us(2)
    trigger[sensor].high()
    utime.sleep_us(5)
    trigger[sensor].low()
    #iniialise in case we fail to sense
    signaloff = signalon = 0
    
    if DEBUG > 10: print ("sensor value",echo[sensor].value() )
    while echo[sensor].value() == 0:    
        signaloff = utime.ticks_us()
    if DEBUG > 10: print ("sensor value",echo[sensor].value() )
    while echo[sensor].value() == 1:
        signalon = utime.ticks_us()
  
    timepassed = signalon - signaloff
    distance = (timepassed * 0.0343) / 2
    
    if DEBUG > 10: print("The distance from object is ",distance,"cm")
    return distance

# forever loop
def main ():
    # turn all sensors on
    if DEBUG > 0: print("Wheelchair sensor starting")
    for i in range(len(power)): power[i].high()
    
    # pDELAY changes depending on disctance so reset it at start of loop
    pdelay = DELAY
    
    # main loop
    while True:
        # blink led
        led.toggle()
      
        # sense distance
        distance = 1000 # start with an our of range value
        for i in range(len(trigger)):
            utime.sleep_ms(pdelay)
            distance = min(distance, ultra(i))
            utime.sleep_ms(pdelay)

        # beep rate and frequency depending on distance
        if distance < MINDIST:
            if DEBUG > 10: print ("main MINDIST",distance)
            playtone(1000)
            pdelay = DELAY
        elif MINDIST <= distance <= MAXDIST:
            if DEBUG > 0:    
                tone = int(renormalise(distance,[MINDIST,MAXDIST],[1000,500]))
                pdelay = int(renormalise(distance,[MINDIST,MAXDIST],[0,100]))
                playtone(tone)
                print ("main between min and max",distance, tone, pdelay)
                utime.sleep(0.2)
                bequiet()
        else:
            if DEBUG > 0: print ("main MAXDIST",distance)
            pdelay = DELAY
            bequiet()
          
try:
    main()

except KeyboardInterrupt:
    print('Got ctrl-c')

finally:
    print('turning off sound')
    buzzer.duty_u16(0)
    
