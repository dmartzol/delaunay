import os
from scipy.spatial import Delaunay
from delaunay.image import get_points

try:
    import cairocffi as cairo
except ImportError:
    cairo = None


class Triangulation(object):
    """
    Input should be a dithered image in mode L
    """
    def __init__(self, dithered_image):
        self.width, self.height = dithered_image.size
        self.image = dithered_image

    def triangulate(self, output_filename='out.png'):
        points = get_points(self.image)
        triangulation = Delaunay(points)
        print("Number of points: {}".format(len(points)))
        self.render_triangulation(
            triangulation,
            self.image.width,
            self.image.height,
            output_filename)

    def filter_path_list(self, l):
        """
        Filtering list for repeated paths
        """
        new_list = []
        for element in l:
            inverted = element[::-1]
            if element in new_list:
                continue
            elif inverted in new_list:
                continue
            else:
                new_list.append(element)
        return new_list

    def render_as_png(self, tri, width, height, output_filename):
        """
        We print twice most of the lines here but it is faster to filter them
        and it doesn't really mater for raster files
        """
        line_width = 1.0
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        context = cairo.Context(surface)
        context.set_line_cap(cairo.LINE_CAP_ROUND)
        context.set_line_join(cairo.LINE_JOIN_ROUND)
        context.set_line_width(line_width)
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
        surface.write_to_png(output_filename)

    def render_as_svg(self, tri, width, height, output_filename):
        #TODO: Optimize this algorithm one day
        # converting points to paths
        paths = []
        for simplice in tri.simplices:
            for i, _ in enumerate(simplice):
                paths.append([simplice[i - 1], simplice[i]])

        # Filtering list for repeated paths
        paths = self.filter_path_list(paths)

        fo = open(output_filename, 'wb')
        surface_svg = cairo.SVGSurface(fo, width, height)
        context = cairo.Context(surface_svg)
        context.set_line_cap(cairo.LINE_CAP_ROUND)
        context.set_line_join(cairo.LINE_JOIN_ROUND)
        context.set_line_width(1)
        with context:
            context.set_source_rgb(1, 1, 1)
            context.paint()
        # Finally drawing paths
        for path in paths:
            x, y = tri.points[path[0]]
            context.move_to(x, y)
            x, y = tri.points[path[1]]
            context.line_to(x, y)
        context.stroke()
        surface_svg.finish()

    def render_triangulation(self, tri, width, height, output_filename):
        name, file_extension = os.path.splitext(output_filename)
        if file_extension == '.png':
            self.render_as_png(tri, width, height, output_filename)
        if file_extension == '.svg':
            self.render_as_svg(tri, width, height, output_filename)
