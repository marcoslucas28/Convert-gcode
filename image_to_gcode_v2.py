import cv2
import numpy as np
import svgpathtools
from scipy import ndimage
from PIL import Image

def detect_edges(image_path, threshold=100):
    """Aplica detecção de bordas usando Canny"""
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    blurred = cv2.GaussianBlur(image, (5, 5), 0)
    edges = cv2.Canny(blurred, threshold, threshold * 2)
    return edges

def trace_contours(edges):
    """Encontra contornos na imagem"""
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return contours if contours else []

def normalize_contours(contours, target_size=30):
    """Redimensiona e centraliza os contornos para caber em target_size x target_size"""
    if not contours:
        return []  # Retorna uma lista vazia se não houver contornos
    
    all_points = np.vstack([c.reshape(-1, 2) for c in contours]) if contours else np.array([])
    if all_points.size == 0:
        return []  # Retorna lista vazia para evitar erro
    
    min_x, min_y = np.min(all_points, axis=0)
    max_x, max_y = np.max(all_points, axis=0)
    
    width, height = max_x - min_x, max_y - min_y
    scale = target_size / max(width, height)
    
    normalized_contours = []
    for contour in contours:
        scaled_contour = ((contour.reshape(-1, 2) - [min_x, min_y]) * scale)
        centered_contour = scaled_contour + [(target_size - (width * scale)) / 2, (target_size - (height * scale)) / 2]
        normalized_contours.append(centered_contour.astype(np.int32))
    
    return normalized_contours

def convert_to_gcode(contours, scale=1.0):
    """Converte contornos em G-code"""
    contours = normalize_contours(contours, target_size=30)
    if not contours:
        return "G21 ; Set units to mm\nG90 ; Absolute positioning\nM30 ; No contours found"
    
    gcode = ["G21 ; Set units to mm", "G90 ; Absolute positioning", "G1 Z5 F500"]
    
    for contour in contours:
        points = contour.reshape(-1, 2) * scale
        gcode.append(f"G0 X{points[0][0]:.2f} Y{points[0][1]:.2f}")
        gcode.append("G1 Z0 F500")
        
        for x, y in points:
            gcode.append(f"G1 X{x:.2f} Y{y:.2f}")
        
        gcode.append("G1 Z5 F500")
    
    gcode.append("M30 ; End of program")
    return "\n".join(gcode)

def process_svg(svg_path, scale=1.0, use_curves=True):
    """Converte SVG para G-code, com ou sem curvas"""
    paths, _ = svgpathtools.svg2paths(svg_path)
    if not paths:
        return "G21\nG90\nM30 ; No paths found"
    
    gcode = ["G21", "G90", "G1 Z5 F500"]
    
    for path in paths:
        for segment in path:
            start = segment.start * scale
            end = segment.end * scale
            
            if isinstance(segment, svgpathtools.Line):
                gcode.append(f"G1 X{end.real:.2f} Y{end.imag:.2f}")
            elif isinstance(segment, (svgpathtools.CubicBezier, svgpathtools.QuadraticBezier)):
                if use_curves:
                    gcode.append(f"G2 X{end.real:.2f} Y{end.imag:.2f} I{start.real - end.real:.2f} J{start.imag - end.imag:.2f}")
                else:
                    gcode.append(f"G1 X{end.real:.2f} Y{end.imag:.2f}")  # Sem curvas
            
    gcode.append("M30")
    return "\n".join(gcode)

def convert_image_to_gcode(image_path, use_curves=True):
    """Detecta bordas e converte para G-code"""
    edges = detect_edges(image_path)
    contours = trace_contours(edges)
    return convert_to_gcode(contours)

def convert_svg_to_gcode(svg_path, use_curves=True):
    """Converte SVG para G-code"""
    return process_svg(svg_path, use_curves=use_curves)
