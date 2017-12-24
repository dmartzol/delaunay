import numpy as np
from scipy.spatial import Delaunay
import sys
from PIL import Image
import random
from delaunay.bridson import poisson_disc_samples

try:
    import cairocffi as cairo
except ImportError:
    cairo = None

NUMBER_OF_DOTS = 500

# TODO: Voronoi


def render_tri(tri, width, height, format='png'):
    if format is 'png':
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        context = cairo.Context(surface)
        context.set_line_cap(cairo.LINE_CAP_ROUND)
        context.set_line_join(cairo.LINE_JOIN_ROUND)
        context.set_line_width(1)
        with context:
            context.set_source_rgb(1, 1, 1)
            context.paint()
        for triangle in tri.simplices:
            x, y = tri.points[triangle[-1]]
            context.move_to(x, y)
            for vertex in triangle:
                x, y = tri.points[vertex]
                context.line_to(x, y)
        context.stroke()
        surface.write_to_png('out.png')
    if format is 'svg':
        fo = open('out.svg', 'wb')
        surface_svg = cairo.SVGSurface(fo, width, height)
        context = cairo.Context(surface_svg)
        context.set_line_cap(cairo.LINE_CAP_ROUND)
        context.set_line_join(cairo.LINE_JOIN_ROUND)
        context.set_line_width(1)
        with context:
            context.set_source_rgb(1, 1, 1)
            context.paint()
        for triangle in tri.simplices:
            x, y = tri.points[triangle[-1]]
            context.move_to(x, y)
            for vertex in triangle:
                x, y = tri.points[vertex]
                context.line_to(x, y)
        context.stroke()
        surface_svg.finish()



def main():
    if len(sys.argv) is not 2:
        raise ValueError("You need to input an image.")
    args = sys.argv[1:]
    filename = args[0]
    im = Image.open(filename)
    width, height = im.size
    points = []
    for i in range(NUMBER_OF_DOTS):
        points.append([random.randint(0, width), random.randint(0, height)])
    a = np.array(poisson_disc_samples(width, height, r=10))
    # points = np.array(points)
    points = a
    triangulation = Delaunay(points)
    render_tri(triangulation, width, height, format='png')

