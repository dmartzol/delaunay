import numpy as np
from scipy.spatial import Delaunay

try:
    import cairocffi as cairo
except ImportError:
    cairo = None

def main():
    points = np.array([[0, 0], [0, 1.1], [1, 0], [1, 1]])
    tri = Delaunay(points)
    print(tri.simplices)
