from machine import Pin, PWM
from time import ticks_ms, ticks_diff

# === Motor A pins ===
IN1 = Pin(16, Pin.OUT)
IN2 = Pin(17, Pin.OUT)
ENA = PWM(Pin(20))
ENA.freq(1000)

# === Motor B pins ===
IN3 = Pin(26, Pin.OUT)
IN4 = Pin(22, Pin.OUT)
ENB = PWM(Pin(27))
ENB.freq(1000)

# === Servo Setup ===
servo = PWM(Pin(13))
servo.freq(50)  # 50Hz for standard servos

def set_angle(angle):
    angle = max(0, min(180, angle))
    min_us = 500
    max_us = 2500
    us = min_us + (angle / 180) * (max_us - min_us)
    duty = int((us / 20000) * 65535)
    servo.duty_u16(duty)

# === Motor Speed ===
speed = 40000  # Max 65535

def motorA_forward():
    IN1.high()
    IN2.low()
    ENA.duty_u16(speed)

def motorB_forward():
    IN3.high()
    IN4.low()
    ENB.duty_u16(speed)

def stop_all():
    IN1.low()
    IN2.low()
    IN3.low()
    IN4.low()
    ENA.duty_u16(0)
    ENB.duty_u16(0)
    set_angle(70)

# === State Machine ===
state = 0
last_action_time = ticks_ms()

# === Main loop ===
try:
    set_angle(70)  # Initial position
    while True:
        now = ticks_ms()

        if state == 0:
            print("Motors moving forward")
            motorA_forward()
            motorB_forward()
            last_action_time = now
            state = 1

        elif state == 1 and ticks_diff(now, last_action_time) >= 7000:
            print("Rotating servo to 140°")
            set_angle(140)
            last_action_time = now
            state = 2

        elif state == 2 and ticks_diff(now, last_action_time) >= 7000:
            print("Returning servo to 70°")
            set_angle(70)
            last_action_time = now
            state = 3

        elif state == 3 and ticks_diff(now, last_action_time) >= 7000:
            print("Cycle restarting")
            state = 0

        # You can also read sensors, check buttons, etc., here without blocking

except KeyboardInterrupt:
    stop_all()
    print("Program stopped by user")
