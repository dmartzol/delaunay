import sys
from PIL import Image
from delaunay.stippler import Stippler
# from delaunay.grid_search import grid_search
from delaunay.triangulation import Triangulation
from delaunay.image import dither, raster_points

try:
    import cairocffi as cairo
except ImportError:
    cairo = None

# TODO: Voronoi triangulation
# TODO: input and output of clases should be images and I save them form here

def main():
    if len(sys.argv) is not 2:
        raise ValueError("You need to input an image.")
    args = sys.argv[1:]
    filename = args[0]

    image = Image.open(filename)

    stippler = Stippler(image)
    points, shape = stippler.start()
    stippled = raster_points(points, shape)
    triangulation = Triangulation(stippled)
    triangulation.triangulate(output_filename='stippled.png')

    # image = Image.open(filename)
    # dithered = dither(image)
    # triangulation = Triangulation(dithered)
    # triangulation.triangulate(output_filename='dithered.png')
