from machine import Pin, PWM
from time import sleep

# Motor A pins
IN1 = Pin(16, Pin.OUT)
IN2 = Pin(17, Pin.OUT)
ENA = PWM(Pin(21))
ENA.freq(1000)

# Motor B pins
IN3 = Pin(19, Pin.OUT)
IN4 = Pin(18, Pin.OUT)
ENB = PWM(Pin(20))
ENB.freq(1000)


# Initialize PWM on GPIO14
servo = PWM(Pin(13))
servo.freq(50)  # SG90 works on 50Hz

def set_angle(angle):
    # Clamp angle between 0 and 180
    angle = max(0, min(180, angle))
    # Convert angle to duty cycle (approx. 0.5ms to 2.5ms pulse width)
    min_us = 500    # 0.5 ms
    max_us = 2500   # 2.5 ms
    us = min_us + (angle / 180) * (max_us - min_us)
    duty = int((us / 20000) * 65535)  # Scale to 16-bit range (20ms period = 50Hz)
    servo.duty_u16(duty)
# Half speed setting (0-65535)
speed = 40000  #

def motorA_forward():
    IN1.high()
    IN2.low()
    ENA.duty_u16(speed)

def motorB_forward():
    IN3.low()
    IN4.high()
    ENB.duty_u16(speed)

def stop_all():
    IN1.low()
    IN2.low()
    IN3.low()
    IN4.low()
    ENA.duty_u16(0)
    ENB.duty_u16(0)
    set_angle(70)


# Main loop
set_angle(70)
try:
  while True:

    print(" Motors forward")
    motorA_forward()
    motorB_forward()
    sleep(5)
    print("servo intiated")
    set_angle(140)
    sleep(5)
    set_angle(70)
    print("servo returned to original posotion")
except KeyboardInterrupt:
    stop_all()
    print("Stopped by user")
