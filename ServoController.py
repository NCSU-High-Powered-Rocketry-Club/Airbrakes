import RPi.GPIO as GPIO

servoPin = 12			# the GPIO pin the servo is plugged into
GPIO.setwarnings(False)			#disable warnings
GPIO.setmode(GPIO.BOARD)		#set pin numbering system

# set the servo pin to output
GPIO.setup(servoPin, GPIO.OUT)

print(f"Set up servo on pin {servoPin}")

#create PWM instance with frequency
pi_pwm = GPIO.PWM(servoPin, 50)

# start PWM of required Duty Cycle
pi_pwm.start(0) 

# minimum duty cycle for left stop (determined with trial and error)
servo_duty_min = 3.5 
# maximum duty cycle for right stop (determined with trial and error)
servo_duty_max = 11.5 

# this function converts the degree value to the duty cycle for the servo
def degrees_to_duty(deg):
    # TODO: Should this error or just fail silently? I think incorrect behavior
    # is better than exiting the program when the rocket is flying
    if (deg > 180) or (deg < 0):
        raise ValueError("Value not between 0 and 180")
    return ((deg * (servo_duty_max - servo_duty_min)) / 180) + servo_duty_min

def set_servo(deg):
    """
    Sets the servo to the angle in degrees, from 0 to 180
    """
    pi_pwm.ChangeDutyCycle(degrees_to_duty(deg))

if __name__== "__main__":
    while True:
        deg = int(input("enter input: "))
        try:
            set_servo(deg)
        except:
            print("enter a value between 0 and 180")
