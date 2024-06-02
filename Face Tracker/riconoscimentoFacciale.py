from __future__ import print_function
import cv2
import numpy as np
import os
import RPi.GPIO as GPIO
import time
from imutils.video import VideoStream
import imutils

# Definisci i GPIO dei servomotori
PAN_SERVO_PIN = 27
TILT_SERVO_PIN = 17

# Disabilita gli avvertimenti GPIO e configura i pin GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PAN_SERVO_PIN, GPIO.OUT)
GPIO.setup(TILT_SERVO_PIN, GPIO.OUT)

# Inizializza il riconoscitore di volti
recognizer = cv2.face.LBPHFaceRecognizer_create()
trainer_file_path = '/home/pi/ProgettoPython/RiconoscimentoFacciale/trainer/trainer.yml'
recognizer.read(trainer_file_path)
cascade_path = '/home/pi/ProgettoPython/RiconoscimentoFacciale/haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(cascade_path)

# Mappatura ID-nome
id_to_name = {0: 'Lorenzo', 1: 'Mattia', 2: 'None', 3: 'None', 4: 'None', 5: 'None'}


# Posiziona un servo alla posizione desiderata
def position_servo(servo_pin, angle):
    pwm = GPIO.PWM(servo_pin, 50)
    pwm.start(8)
    duty_cycle = angle / 18.0 + 2.5
    pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(0.3)  # Aggiungi un ritardo per un movimento più fluido
    pwm.stop()
    print("[INFO] Positioning servo at GPIO {0} to {1} degrees".format(servo_pin, angle))


# Sposta un singolo servo con ritardo per ridurre gli spasmi
def move_single_servo(servo_pin, angle):
    pwm = GPIO.PWM(servo_pin, 50)
    pwm.start(8)
    duty_cycle = angle / 18.0 + 2.5
    pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(0.5)  # Aggiungi un ritardo per ridurre gli spasmi
    pwm.stop()


# Sposta entrambi i servomotori in parallelo
def move_servo(pan_angle, tilt_angle):
    t1 = threading.Thread(target=move_single_servo, args=(PAN_SERVO_PIN, pan_angle))
    t2 = threading.Thread(target=move_single_servo, args=(TILT_SERVO_PIN, tilt_angle))
    t1.start()
    t2.start()
    t1.join()
    t2.join()


# Inizializza il flusso video e attendi il riscaldamento della fotocamera
print("[INFO] waiting for camera to warm up...")
vs = VideoStream(src=0).start()
time.sleep(2.0)

# Dimensione della finestra del video
frame_width = 640
frame_height = 480
center = (frame_width // 2, frame_height // 2)

# Inizializza gli angoli dei servomotori
pan_angle = 90
tilt_angle = 90

# Posiziona i servomotori nella posizione iniziale
position_servo(PAN_SERVO_PIN, pan_angle)
position_servo(TILT_SERVO_PIN, tilt_angle)

# Definisci la zona morta
dead_zone = 30

# Loop principale
while True:
    frame = vs.read()
    frame = imutils.resize(frame, width=frame_width)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(100, 100),
    )

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        id, confidence = recognizer.predict(gray[y:y + h, x:x + w])

        name = id_to_name.get(id, "Unknown")
        confidence = "  {0}%".format(round(100 - confidence))

        cv2.putText(frame, str(name), (x + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, str(confidence), (x + 5, y + h - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 1)

        # Calcola il centro del volto
        face_center_x = x + w // 2
        face_center_y = y + h // 2

        # Controlla se il volto è fuori dalla zona morta
        if abs(face_center_x - center[0]) > dead_zone:
            if face_center_x < center[0]:
                pan_angle -= 2
            else:
                pan_angle += 2

        if abs(face_center_y - center[1]) > dead_zone:
            if face_center_y < center[1]:
                tilt_angle -= 2
            else:
                tilt_angle += 2

        # Limita gli angoli dei servomotori
        pan_angle = max(0, min(180, pan_angle))
        tilt_angle = max(0, min(180, tilt_angle))

        move_servo(pan_angle, tilt_angle)

    cv2.imshow('Frame', frame)

    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        break

# Pulizia
print("\n [INFO] Exiting Program and cleanup stuff \n")
position_servo(PAN_SERVO_PIN, 90)
position_servo(TILT_SERVO_PIN, 90)
GPIO.cleanup()
cv2.destroyAllWindows()
vs.stop()
