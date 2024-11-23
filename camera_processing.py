import cv2
import numpy as np

def preprocess_frame(frame, img_size=(64, 64)):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, binarizada = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)
    resized = cv2.resize(gray, img_size)
    return resized.flatten() / 255.0
