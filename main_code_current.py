import network
import socket
from machine import Pin, PWM
from time import sleep

# ------------------- Wi-Fi Setup -------------------------------------------------------------------------------------------------------
SSID = 'VIRUSS'
PASSWORD = 'Viru_246'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)
print("Connecting to Wi-Fi")
while not wlan.isconnected():
    sleep(1)
print("wifi connected ! IP:", wlan.ifconfig()[0])

# ------------------- Stepper Setup -------------------------------------------------------------------------------------------------
IN1 = Pin(2, Pin.OUT)
IN2 = Pin(3, Pin.OUT)
IN3 = Pin(4, Pin.OUT)
IN4 = Pin(5, Pin.OUT)

sequence = [
    [1, 0, 1, 0],
    [0, 1, 1, 0],
    [0, 1, 0, 1],
    [1, 0, 0, 1]
]

STEPS_PER_REV = 200
DEG_PER_STEP = 360 / STEPS_PER_REV  # 1.8°
MAX_ANGLE = 30
MIN_ANGLE = -30
current_angle = 0  # Track current stepper angle
#---------------------------------------- motor and servo(sg90) setup(top platform)-----------------------------------------------
# Motor A pins
in1 = Pin(16, Pin.OUT)
in2 = Pin(17, Pin.OUT)
ENA = PWM(Pin(20))
ENA.freq(1000)

# Motor B pins
in3 = Pin(26, Pin.OUT)
in4 = Pin(22, Pin.OUT)
ENB = PWM(Pin(27))
ENB.freq(1000)
# Initialize PWM on GPIO13
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
    in1.low()
    in2.high()
    ENA.duty_u16(speed)

def motorB_forward():
    in3.high()
    in4.low()
    ENB.duty_u16(speed)

def stop_all():
    in1.low()
    in2.low()
    in3.low()
    in4.low()
    ENA.duty_u16(0)
    ENB.duty_u16(0)
    set_angle(70)
#---------------------------------------------Stepper Definitions----------------------------------------------------------------------    

def step_motor(delay, steps, direction=1):
    seq = sequence if direction == 1 else list(reversed(sequence))
    for _ in range(steps):
        for step in seq:
            IN1.value(step[0])
            IN2.value(step[1])
            IN3.value(step[2])
            IN4.value(step[3])
            sleep(delay)

def go_to_stepper_angle(target_angle):
    global current_angle
    target_angle = max(MIN_ANGLE, min(MAX_ANGLE, target_angle))
    delta_angle = target_angle - current_angle
    if abs(delta_angle) < 0.5:
        print(f"Stepper already near {target_angle:.1f}°")
        return
    direction = 1 if delta_angle > 0 else -1
    steps = int(abs(delta_angle) / DEG_PER_STEP)
    step_motor(0.01, steps, direction)
    current_angle = target_angle
    print(f"Stepper moved to {current_angle:.2f}°")
def stepper_overheating_protection():
    IN1.low()
    IN2.low()
    IN3.low()
    IN4.low()
def return_stepper_to_origin():
    global current_angle
    if abs(current_angle) > 0.5:
        steps_back = int(abs(current_angle) / DEG_PER_STEP)
        direction = -1 if current_angle > 0 else 1
        step_motor(0.01, steps_back, direction)
        print("Stepper returned to 0°")
        current_angle = 0
    else:
        print("Stepper already at origin")

# ------------------------------------------------------Servo Setup ---------------------------------------------------------------------
servo1 = PWM(Pin(14))
servo2 = PWM(Pin(11))
servo1.freq(50)
servo2.freq(50)

SERVO_ORIGIN = 90

def angle_to_duty(angle):
    min_duty = 1802
    max_duty = 7864
    return int(min_duty + (angle / 180) * (max_duty - min_duty))

def set_servo_angle(angle):
    angle = max(0, min(180, angle))
    servo1_angle = 180 - angle
    servo2_angle =  angle
    servo1.duty_u16(angle_to_duty(servo1_angle))
    servo2.duty_u16(angle_to_duty(servo2_angle))
    print(f"Servos moved to {servo1_angle}° <--> {servo2_angle}°")
    sleep(0.1)

# Initialize servo position
servo1.duty_u16(angle_to_duty(SERVO_ORIGIN))
servo2.duty_u16(angle_to_duty(180 - SERVO_ORIGIN))
print(f"Initial Platform angle set to {SERVO_ORIGIN}°")

# ------------------- TCP Server ----------------------------------------------------------------------------------------------------------
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('', 5050))
server_socket.listen(1)
print("Listening on port 5050")

try:
    while True:
        conn, addr = server_socket.accept()
        print("Connection from", addr)

        while True:
            data = conn.recv(1024)
            if not data:
                break

            try:
                message = data.decode().strip()
                print("Received:", message)

                parts = message.split(",")
                if len(parts) != 3:
                    raise ValueError("Expected format: a,b,c")

                a_str, b_str, c_str = parts
                a = float(a_str)
                b = float(b_str)
                c = float(c_str)  # shoot flag, 0---> no shooting , 1----> shoots

                # Clamp and move stepper
                go_to_stepper_angle(a)
                stepper_overheating_protection() #motor was heating up a lot 

                # Move servos
                set_servo_angle(b)
                if int(c) == 1:
                    print("Motors forward")
                    motorA_forward()
                    motorB_forward()
                    sleep(4)
                    print("servo intiated")
                    set_angle(140)
                    sleep(2)
                    set_angle(70)
                    print("servo returned to original position")
                    stop_all()

                conn.send(b"ACK\n")
                stop_all() #just in case tcp relay fails 
               
            except Exception as e:
                print("Error:", e)
                conn.send(b"ERR\n")

        conn.close()
        print(" Connection closed")

except KeyboardInterrupt:
    print("\n Interrupted! Returning to origin...")
    return_stepper_to_origin()
    servo1.duty_u16(angle_to_duty(SERVO_ORIGIN))
    servo2.duty_u16(angle_to_duty(180 - SERVO_ORIGIN))
    sleep(1)
    servo1.deinit()
    servo2.deinit()
    stepper_overheating_protection()
    print(" Servos reset and deinitialized. Goodbye!")


