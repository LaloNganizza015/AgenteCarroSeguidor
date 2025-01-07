import cv2
import numpy as np

def find_squares(frame, min_area, max_area):
    # Convertir el cuadro a escala de grises
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Aplicar detección de bordes y encontrar contornos
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    squares = []  # Lista para almacenar cuadrados detectados
    areas = []    # Lista para almacenar las áreas de los cuadrados

    for contour in contours:
        # Aproximar el contorno
        approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)

        # Verificar si el contorno tiene 4 lados (es cuadrado o rectangular)
        if len(approx) == 4 and cv2.isContourConvex(approx):
            # Calcular el área del contorno
            area = cv2.contourArea(contour)

            # Verificar si el área está dentro de los límites
            if min_area <= area <= max_area:
                # Verificar si tiene proporciones de un cuadrado
                (x, y, w, h) = cv2.boundingRect(approx)
                aspect_ratio = float(w) / h
                if 0.85 <= aspect_ratio <= 1.15:  # Ajustar según tolerancia
                    squares.append(approx)
                    areas.append(area)  # Guardar el área del cuadrado detectado

    # Dibujar los cuadrados detectados en una copia del frame
    frame_with_squares = frame.copy()
    cv2.drawContours(frame_with_squares, squares, -1, (0, 255, 0), 3)

    # Retorna el frame modificado, los cuadrados detectados y sus áreas
    return frame_with_squares, squares, areas
