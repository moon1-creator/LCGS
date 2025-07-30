import cv2
import mediapipe as mp
import math
import numpy as np
import time
import socket


SERVER_IP = '10.231.130.171'
PORT  = 5050
client_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client_socket.connect((SERVER_IP, PORT))
    print("[INFO] COnnected to server.")
except Exception as e:
    print("[ERROR] Could not connect to server:", e)
    client_socket = None
    
    
# Initialize MediaPipe Hands module
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Initialize hand detection model
hands = mp_hands.Hands(max_num_hands=1,min_detection_confidence=0.8, min_tracking_confidence=0.6)

#cap for internal camera, cap2 for external camera (target)
cap = cv2.VideoCapture(0)
cap2 = cv2.VideoCapture(1)

z = 2000
scaling_factor = 1
x_ref =  320
y_ref = 240

if not cap.isOpened():
    print("Camera index 0 not found. Trying index 1.")
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("No camera found.")
        exit()

# Load the target image (capture one frame)
ret, original_target = cap2.read()
print(ret)
if not ret:
    print("Failed to capture target image.")
    cap2.release()
    exit()

# Get the dimensions of the target image
h, w = original_target.shape[:2]
print(h,w)

speed_level = [item for item in range(0,101,10)]
def are_all_fingers_open(hand_landmarks, frame_shape):
    # Get landmarks
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    thumb_ip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    index_pip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP]
    middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    middle_pip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP]
    ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
    ring_pip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_PIP]
    pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
    pinky_pip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_PIP]

    # Convert to pixel coordinates
    thumb_tip_y = int(thumb_tip.y * frame_shape[0])
    thumb_ip_y = int(thumb_ip.y * frame_shape[0])
    index_tip_y = int(index_tip.y * frame_shape[0])
    index_pip_y = int(index_pip.y * frame_shape[0])
    middle_tip_y = int(middle_tip.y * frame_shape[0])
    middle_pip_y = int(middle_pip.y * frame_shape[0])
    ring_tip_y = int(ring_tip.y * frame_shape[0])
    ring_pip_y = int(ring_pip.y * frame_shape[0])
    pinky_tip_y = int(pinky_tip.y * frame_shape[0])
    pinky_pip_y = int(pinky_pip.y * frame_shape[0])

    # Check if all fingertips are above the PIP joints
    all_fingers_open = all([
        thumb_tip_y < thumb_ip_y,
        index_tip_y < index_pip_y,
        middle_tip_y < middle_pip_y,
        ring_tip_y < ring_pip_y,
        pinky_tip_y < pinky_pip_y
    ])

    return all_fingers_open

def is_index_finger_raised(hand_landmarks, frame_shape):
    # Get fingertip landmarks
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
    pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]

    # Convert to pixel coordinates
    thumb_tip_y = int(thumb_tip.y * frame_shape[0])
    index_tip_y = int(index_tip.y * frame_shape[0])
    middle_tip_y = int(middle_tip.y * frame_shape[0])
    ring_tip_y = int(ring_tip.y * frame_shape[0])
    pinky_tip_y = int(pinky_tip.y * frame_shape[0])

    # Check if index finger is raised
    index_raised = index_tip_y < min(thumb_tip_y, middle_tip_y, ring_tip_y, pinky_tip_y)
    
    # Check if other fingers are in a closed position
    fingers_closed = all([
        (index_tip_y < thumb_tip_y) and (thumb_tip_y - index_tip_y > 50),  # Index above thumb
        index_tip_y < middle_tip_y,  # Index above middle
        index_tip_y < ring_tip_y,    # Index above ring
        index_tip_y < pinky_tip_y    # Index above pinky
    ])
    
    return index_raised and fingers_closed

def is_pinch_detected(hand_landmarks, frame_shape, threshold=40):
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

    h, w = frame_shape[:2]
    thumb_x, thumb_y = int(thumb_tip.x * w), int(thumb_tip.y * h)
    index_x, index_y = int(index_tip.x * w), int(index_tip.y * h)

    distance = math.hypot(index_x - thumb_x, index_y - thumb_y)

    return distance < threshold, (thumb_x, thumb_y), (index_x, index_y)
# Main loop
speed =0
c=0
d=0
while cap.isOpened():
    ret, frame = cap.read()
    _,frame2 = cap2.read()
    if not ret:
        break

    # Convert frame to RGB
    frame=cv2.flip(frame,1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    
    

    # Copy the original target image
    target = cv2.resize(original_target, (w, h))
    
    # Draw hand landmarks and connections
    if results.multi_hand_landmarks:
        
        
        for hand_landmarks in results.multi_hand_landmarks:
            pinch, thumb_coords, index_coords = is_pinch_detected(hand_landmarks, frame.shape)
            
            
            
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            index_tip_x = int(index_tip.x * frame.shape[1])
            index_tip_y = int(index_tip.y * frame.shape[0])
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            thumb_tip_x = int(thumb_tip.x * frame.shape[1])
            thumb_tip_y = int(thumb_tip.y * frame.shape[0])
            h, w, _ = frame.shape
            thumb_x, thumb_y = int(thumb_tip.x * w), int(thumb_tip.y * h)
            index_x, index_y = int(index_tip.x * w), int(index_tip.y * h) 
            cv2.circle(frame, (thumb_x, thumb_y), 10, (255, 0, 0), -1)
            cv2.circle(frame, (index_x, index_y), 10, (255, 0, 0), -1)
            cv2.line(frame, (thumb_x, thumb_y), (index_x, index_y), (0, 255, 0), 3)
            
            #calculate distance
            distance = math.hypot(index_x - thumb_x, index_y - thumb_y)
        
            if are_all_fingers_open(hand_landmarks, frame.shape):
                # Draw a circle on the index tip
                cv2.circle(frame, (index_tip_x, index_tip_y), 20, (0, 255, 0), 2)
                cv2.circle(target, (index_tip_x, index_tip_y), 20, (0, 255, 0), 2)
                
                if c==1 and d==0:
                    d=1
                    c=0
                    # angle_hor = -1.65 * math.atan(float((index_x-320)*scaling_factor/z)) * (180/math.pi)
                    angle_hor = math.atan(float((index_x-320)/z)) * (180/math.pi)
                    angle_hor = np.interp(angle_hor,[-6,6],[-30,30])
                    
                    # angle_ver = 95- 1.85*math.atan(float(480-index_y)/z)*(180/math.pi)
                    angle_ver = math.atan(float((480-index_y)/z)) * (180/math.pi)
                    angle_ver = 150-np.interp(angle_ver,[4,12],[40,110])
                    
                    
                    
                break
            elif is_index_finger_raised(hand_landmarks, frame.shape):
                # Draw a cross on the index tip
                
                cv2.line(frame, (index_tip_x - 20, index_tip_y), (index_tip_x + 20, index_tip_y), (0, 0, 255), 2)
                cv2.line(frame, (index_tip_x, index_tip_y - 20), (index_tip_x, index_tip_y + 20), (0, 0,255), 2)
                cv2.line(target, (index_tip_x - 20, index_tip_y), (index_tip_x + 20, index_tip_y), (0, 0, 255), 2)
                cv2.line(target, (index_tip_x, index_tip_y - 20), (index_tip_x, index_tip_y + 20), (0, 0, 255), 2)
                c=1
                # speed_bar = np.interp(distance, [30, 100], [400, 150])
                # speed_perc = np.interp(distance, [30, 100], [0, 100])
                # cv2.rectangle(frame, (50, 150), (85, 400), (0, 255, 0), 3)
                # cv2.rectangle(frame, (50, int(speed_bar)), (85, 400), (0, 255, 0), -1)
                # speed = np.interp(distance, [30, 100], [0,100])
                # cv2.putText(frame, f'{int(speed_perc)} %', (40, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                
            elif pinch and d==1:
                d=0
                c=0
                cv2.circle(frame, thumb_coords, 15, (0, 255, 255), -1)
                cv2.circle(frame, index_coords, 15, (0, 255, 255), -1)
                cv2.line(frame, thumb_coords, index_coords, (0, 255, 255), 3)
                print(f"{angle_hor},{angle_ver},{1}\n")
                try:
                    message=f"{angle_hor},{angle_ver},{1}\n"
                    client_socket.sendall(message.encode('utf-8'))
                    print(f"{angle_hor},{angle_ver},{1}\n")
                            
                except Exception as e:
                    # print("[ERROR] Sending failed:", e)
                    pass

            # Draw landmarks
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    
    # Show the output frames
    cv2.line(frame2, (320 -20, 240), (320 + 20, 240), (0, 0, 255), 2)
    cv2.line(frame2, (320, 240- 20), (320, 240 + 20), (0, 0, 255), 2)
    
    cv2.imshow('Hand Detection', frame)
    cv2.imshow("TARGET", frame2)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cap2.release()
cv2.destroyAllWindows()
if client_socket:
    client_socket.close()