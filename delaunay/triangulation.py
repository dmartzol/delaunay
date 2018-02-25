import os
from scipy.spatial import Delaunay
from delaunay.image import get_points
from delaunay.settings import PEN_TIP, LONGEST_SIDE_PRINT
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
        self.tri = None
        self.points = get_points(self.image)

    def triangulate(self):
        self.tri = Delaunay(self.points)
        print("Number of points: {}".format(len(self.points)))

    def filter_path_list(self, l):
        """
        Deleting repeated paths from list
        """
        # TODO: Optimize

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

    def render_as_png(self, output):
        """
        We print twice most of the lines here but it is faster to filter them
        and it doesn't really mater for raster files
        """

        RATIO = PEN_TIP / LONGEST_SIDE_PRINT
        LINE_WIDTH = max(self.image.width, self.image.height) * RATIO
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.image.width, self.image.height)
        context = cairo.Context(surface)
        context.set_line_cap(cairo.LINE_CAP_ROUND)
        context.set_line_join(cairo.LINE_JOIN_ROUND)
        context.set_line_width(LINE_WIDTH)
        with context:
            context.set_source_rgb(1, 1, 1)
            context.paint()
        for triangle in self.tri.simplices:
            x, y = self.tri.points[triangle[-1]]
            context.move_to(x, y)
            for vertex in triangle:
                x, y = self.tri.points[vertex]
                context.line_to(x, y)
        context.stroke()
        surface.write_to_png(output)

    def render_as_svg(self, output):
        paths = []
        for simplice in self.tri.simplices:
            for i, _ in enumerate(simplice):
                paths.append([simplice[i - 1], simplice[i]])

        # Filtering list for repeated paths
        paths = self.filter_path_list(paths)

        fo = open(output, 'wb')
        surface_svg = cairo.SVGSurface(fo, self.image.width, self.image.height)
        context = cairo.Context(surface_svg)
        context.set_line_cap(cairo.LINE_CAP_ROUND)
        context.set_line_join(cairo.LINE_JOIN_ROUND)
        context.set_line_width(0.5)
        with context:
            context.set_source_rgb(1, 1, 1)
            context.paint()
        # Finally drawing paths
        for path in paths:
            x, y = self.tri.points[path[0]]
            context.move_to(x, y)
            x, y = self.tri.points[path[1]]
            context.line_to(x, y)
        context.stroke()
        surface_svg.finish()

    def save(self, output='triangulation.png'):
        name, file_extension = os.path.splitext(output)
        if file_extension == '.png':
            self.render_as_png(output)
        if file_extension == '.svg':
            self.render_as_svg(output)
