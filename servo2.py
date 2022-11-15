import RPi.GPIO as IO          #calling header file which helps us use GPIO’s of PI
import time                    #calling time to provide delays in program

IO.setwarnings(False)           #do not show any warnings
IO.setmode(IO.BCM)         #we are programming the GPIO by BCM pin numbers. (PIN35 as ‘GPIO19’)
IO.setup(18,IO.OUT)         # initialize GPIO19 as an output.

baseFreq = 10
GPIOpin = 18

maxPWM = 2410 #μsec
minPWM = 556  #μsec
minDEG = 0
maxDEG = 202

def deg2duty(deg):
    # A and B are coefficents of a linear equation to convert from degrees to pulse width in ms
    # I found these by experimenting with the arduino Servo.h library. Use data sheets to find exact values
      
    A = (maxPWM-minPWM)/(maxDEG-minDEG)
    B = minPWM
    pulse_ms = (A*deg + B)*1000
    period_ms = (1/baseFreq)/1000
    duty = (pulse_ms / period_ms) * 100
    return duty


p = IO.PWM(GPIOpin,baseFreq)          #GPIO19 as PWM output, with 100Hz frequency
p.start(0)                  #generate PWM signal with 0% duty cycle
while True:
    p.ChangeDutyCycle(deg2duty(90))
## loop to move between two angles 
#while 1:   
#    x = 0                            #execute loop forever
#    while x < deg2duty(60):               #execute loop for 50 times, x being incremented from 0 to 49.
#        p.ChangeDutyCycle(x)           #change duty cycle for varying the brightness of LED.
#        time.sleep(0.1)                #sleep for 100m second
#        x = x + 0.1
#     
#
 #   while x > deg2duty(20):                         #execute loop for 50 times, x being incremented from 0 to 49.
  #      p.ChangeDutyCycle(x)          #change duty cycle for changing the brightness of LED.
   #     time.sleep(0.1)  
    #    x = x - 0.1                        #sleep for 100m second

