from machine import Pin
from time import sleep

# ------------------- Stepper Setup -------------------
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
current_angle = 0

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
    target_angle = max(MIN_ANGLE, min(MAX_ANGLE, target_angle))  # Clamp
    delta_angle = target_angle - current_angle
    if abs(delta_angle) < 0.5:
        print(f"Stepper already near {target_angle:.1f}°")
        return
    direction = 1 if delta_angle > 0 else -1
    steps = int(abs(delta_angle) / DEG_PER_STEP)
    step_motor(0.01, steps, direction)
    current_angle = target_angle
    print(f"✅ Stepper moved to {current_angle:.2f}°")

def return_to_origin():
    global current_angle
    if abs(current_angle) > 0.5:
        steps_back = int(abs(current_angle) / DEG_PER_STEP)
        direction = -1 if current_angle > 0 else 1
        step_motor(0.01, steps_back, direction)
        print("✅ Stepper returned to 0°")
        current_angle = 0
    else:
        print("Stepper already at origin")

# ------------------- Input Loop -------------------
print("Enter stepper angle between -30° and +30°. Type 'exit' to quit.")

try:
    while True:
        user_input = input("Angle: ")
        if user_input.lower() == 'exit':
            break
        angle = float(user_input)
        go_to_stepper_angle(angle)

except KeyboardInterrupt:
    print("\n🔁 Interrupted by user. Returning to origin...")
    return_to_origin()
