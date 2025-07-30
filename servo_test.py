from machine import Pin, PWM
from time import sleep

# ------------------- Servo Setup -------------------
servo1 = PWM(Pin(11))
servo2 = PWM(Pin(14))

servo1.freq(50)
servo2.freq(50)

# Convert angle (0–180°) to PWM duty cycle
def angle_to_duty(angle):
    min_duty = 1802
    max_duty = 7864
    return int(min_duty + (angle / 180) * (max_duty - min_duty))

# Move servos to specified angle
def set_servo_angle(angle):
    angle = max(0, min(180, angle))
    servo1_angle = 180-angle
    servo2_angle = angle
    servo1.duty_u16(angle_to_duty(servo1_angle))
    servo2.duty_u16(angle_to_duty(servo2_angle))
    print(f"Servos moved to {servo1_angle}° / {servo2_angle}°")
    sleep(0.2)

# ------------------- Input Loop -------------------
print("Enter servo angle (0–180),type e to quit.")

while True:
    try:
        user_input = input("Angle: ")
        if user_input.lower() == 'e':
            print("Exiting servo control")
            break
        angle = float(user_input)
        set_servo_angle(angle)
    except ValueError:
        print(" Invalid input. Please enter a number between 0 and 180 or 'e'.")
    except KeyboardInterrupt:
        print("\n Interrupted by user. Returning servos to 90°.")
#         set_servo_angle(90)
        break
