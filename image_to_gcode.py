import cv2
import numpy as np

def convert_image_to_gcode(image_path, scale=1.0, feedrate=1000):
    """Converte imagem para G-code sem curvas G2/G3"""
    
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    edges = cv2.Canny(img, 100, 200)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    gcode = ["G21 ; Definir para mm", "G90 ; Coordenadas absolutas", f"G1 F{feedrate}"]
    
    for contour in contours:
        for i, point in enumerate(contour):
            x, y = point[0] * scale
            if i == 0:
                gcode.append(f"G0 X{x:.2f} Y{y:.2f}")  # Movimento rápido
                gcode.append("M3 S255")  # Ativar caneta
            else:
                gcode.append(f"G1 X{x:.2f} Y{y:.2f}")  # Movimento linear
        gcode.append("M5")  # Desativar caneta
    
    gcode.append("G0 X0 Y0")  # Retornar ao início
    gcode.append("M2 ; Fim do programa")
    
    return "\n".join(gcode)  # Retorna como string
