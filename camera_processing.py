import cv2
import numpy as np

def preprocess_frame(frame, img_size=(32, 32)):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, img_size)
    return resized.flatten() / 255.0
