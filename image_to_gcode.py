import os
import cv2 as cv
import numpy as np
from scipy import ndimage
import constants  # Importando as coordenadas circulares

ignore_color = (255, 255, 255)  # Branco
color_threshold = 10  # Tolerância de cor

class ImageToGcode():
    def __init__(self, img, spread, area, feedrate, offsets):
        self.img = cv.imread(img, cv.IMREAD_GRAYSCALE)
        self.output = ""
        self.outFile = os.path.splitext(os.path.abspath(img))[0] + ".gcode"
        self.spread = spread
        self.printArea = area
        self.feedrate = feedrate
        self.offsets = offsets
        self.visited = np.zeros_like(self.img, dtype=bool)
        self.process_image()

    def detect_edges(self):
        edges = ndimage.sobel(self.img)
        edges = (edges > color_threshold).astype(np.uint8) * 255
        return edges

    def find_neighbors(self, x, y):
        """Retorna os vizinhos conectados usando a matriz de coordenadas circulares"""
        neighbors = []
        for r, circle in enumerate(constants.circumferences):
            for dx, dy in circle:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.img.shape[1] and 0 <= ny < self.img.shape[0]:
                    if self.edges[ny, nx] == 255 and not self.visited[ny, nx]:
                        neighbors.append((nx, ny))
            if neighbors:
                break  # Usa o menor raio possível
        return neighbors

    def trace_path(self, x, y):
        """Segue um caminho de pixels conectados para otimizar a trajetória."""
        path = [(x, y)]
        self.visited[y, x] = True
        while True:
            neighbors = self.find_neighbors(x, y)
            if not neighbors:
                break
            x, y = neighbors[0]  # Pega o próximo ponto mais próximo
            self.visited[y, x] = True
            path.append((x, y))
        return path

    def process_image(self):
        self.edges = self.detect_edges()
        self.output = "G21 ; Configura unidade em mm\nG90 ; Modo absoluto\n"
        self.output += "M280 P0 S50 ; Levantar caneta\n"
        
        for y in range(self.edges.shape[0]):
            for x in range(self.edges.shape[1]):
                if self.edges[y, x] == 255 and not self.visited[y, x]:
                    path = self.trace_path(x, y)
                    
                    # Move até o início do traço
                    start_x, start_y = path[0]
                    self.output += f"G0 X{start_x} Y{start_y} F{self.feedrate}\n"
                    self.output += "M280 P0 S100 ; Baixar caneta\n"
                    
                    # Desenha o caminho
                    for px, py in path[1:]:
                        self.output += f"G1 X{px} Y{py} F{self.feedrate}\n"
                    
                    self.output += "M280 P0 S50 ; Levantar caneta\n"
        
        self.output += "M280 P0 S50 ; Levantar caneta no final\nM30 ; Fim do programa\n"
        
    def save_gcode(self):
        with open(self.outFile, 'w') as f:
            f.write(self.output)
        return self.outFile
