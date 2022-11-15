from rpi_hardware_pwm import HardwarePWM
from time import sleep

# NOTE! This works for the raspberry pi on pwm channel 0. PWM channel 0 can be configured to be I think 2 different pins
#   It should be simple to modify to use PWM channel 1.
#   My set up uses the 5v and ground pins from the pi to power the servo and a 3.3v PWM pin for signal.

#   This works for the servo I own (different from the air brEakes servo), but will hopfully work for that one two.
#   For my servo this controls it from around 0 to slightly more than 180 degrees. I think thats an issue with the values of A and B.

# convert servo orientation in degrees to the appropriate duty cycle as a %
def deg2duty(deg):
    # A and B are coefficents of a linear equation to convert from degrees to pulse width in ms
    # I found these by experimenting with the arduino Servo.h library. Use data sheets to find exact values
    A = 0.01111
    B = 0.5
    pulse_ms = (A*deg + B)
    period_ms = (1/50)*1000
    duty = (pulse_ms / period_ms) * 100
    return duty

# set up PWM to have a period of 20 ms
pwm = HardwarePWM(pwm_channel=0, hz=50)

# start PWM signal, configured to rotate the servo to 90 degrees
pwm.start(deg2duty(90))
sleep(1)
pwm.change_duty_cycle(deg2duty(45))
sleep(1)
pwm.change_duty_cycle(deg2duty(0))
sleep(1)

# stop PWM signal before exiting.
# if skipped the PWM signal will continute until another program stops or changes it.
pwm.stop()
