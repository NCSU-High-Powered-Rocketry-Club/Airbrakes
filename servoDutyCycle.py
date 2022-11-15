import RPi.GPIO as GPIO
from time import sleep

servoPin = 12			# the GPIO pin the servo is plugged into
GPIO.setwarnings(False)			#disable warnings
GPIO.setmode(GPIO.BOARD)		#set pin numbering system

# set the servo pin to output
GPIO.setup(servoPin, GPIO.OUT)

#create PWM instance with frequency
pi_pwm = GPIO.PWM(servoPin, 50)

# start PWM of required Duty Cycle
pi_pwm.start(0) 

# minimum duty cycle for left stop (determined with trial and error)
servoMinDuty = 3.5 
# maximum duty cycle for right stop (determined with trial and error)
servoMaxDuty = 11.5 

# this function converts the degree value to rotate the 
def degreesToPos(deg):
    if (deg > 180) or (deg < 0):
        raise ValueError("Value not between 0 and 180")
    return ((deg * (servoMaxDuty - servoMinDuty)) / 180) + servoMinDuty


while True:
    getInput = int(input("enter input: "))
    try:
        pi_pwm.ChangeDutyCycle(degreesToPos(getInput))
    except:
        print("enter a value between 0 and 180 smh my head")
    #sleep(0.1)
