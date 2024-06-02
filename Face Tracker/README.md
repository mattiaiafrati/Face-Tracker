Facial Recognition and Servo Control System

This project implements a facial recognition and servo control system on a Raspberry Pi. Using OpenCV, the system detects and recognizes faces, adjusting two servos to keep the detected face centered in the video frame. The servos are connected to GPIO pins 27 (pan) and 17 (tilt).

Features:
- Facial Recognition: Utilizes OpenCV and a Haar cascade classifier to detect faces.
- Servo Control: Two servos are controlled to adjust the pan and tilt angles, keeping the face centered in the frame.
- Video Display: Shows the live video feed with recognition information overlay, including the recognized person's name and confidence level.

Setup:
1. Hardware: Connect the pan servo to GPIO pin 27 and the tilt servo to GPIO pin 17 on the Raspberry Pi.
2. Training Data: Train the face recognizer and save the `trainer.yml` file in the specified directory.
3. Cascade Classifier: Ensure the `haarcascade_frontalface_default.xml` file is available in the project directory.

Usage:
1. Start the program.
2. The system waits for the camera to warm up.
3. Servos initialize to the default position.
4. The system detects faces and adjusts the servos to keep the face centered in the frame.
5. The video feed is displayed with rectangles around detected faces and labels showing the name and confidence level.

This system is ideal for applications requiring real-time facial recognition and tracking, providing a robust solution for interactive and responsive projects.