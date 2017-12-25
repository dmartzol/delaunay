import numpy as np
from scipy.spatial import Delaunay
import sys
from PIL import Image, ImageEnhance
import PIL
import random
from delaunay.bridson import poisson_disc_samples
import os

try:
    import cairocffi as cairo
except ImportError:
    cairo = None

# TODO: Voronoi
MIN_POINTS = 20000
FADE = 60
# Incrementing limits makes the image whiter
BLACK_LIMIT = 180
WHITE_LIMIT = 251

def render_tri(tri, width, height, c_factor=None, b_factor=None, format_='png'):
    if format_ is 'png':
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
        if c_factor is not None and b_factor is not None:
            surface.write_to_png(os.path.join('temp', 'out-{}-{}.png'.format(c_factor, b_factor)))
        else:
            surface.write_to_png('out.png')
    if format_ is 'svg':
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


def clamp(x):
    if x < 0:
        return 0
    if x > 255:
        return 255
    return x


def linear_fade(x):
    x = fade_all(x)
    x = grayish_black(x)
    x = grayish_white(x)
    return x


def grayish_white(x):
    # Incrementing the limit makes the whites whiter
    if x > WHITE_LIMIT:
        return WHITE_LIMIT
    return x


def grayish_black(x):
    # Incrementing the limit makes the blacks whiter
    if x < BLACK_LIMIT:
        return BLACK_LIMIT
    return x


def fade_all(x):
    # Incrementing the fade makes the image whiter
    return clamp(x + FADE)


def get_points(im):
    points = []
    if not im.mode is 'L':
        raise ValueError('Image should be mode 1')
    for x in range(im.width):
        for y in range(im.height):
            if im.getpixel((x, y)) == 0:
                points.append([x, y])
    return np.array(points)


def fade_image(im):
    for x in range(im.width):
        for y in range(im.height):
            value = im.getpixel((x, y))
            im.putpixel((x, y), linear_fade(value))
    return im


def process_image(im, c_factor, b_factor):
    contrast = ImageEnhance.Contrast(im)
    im = contrast.enhance(c_factor)
    brightness = ImageEnhance.Brightness(im)
    im = brightness.enhance(b_factor)
    im = black_and_white(im)
    return im


def grayscale_image(im):
    im = im.convert('L')
    im = fade_image(im)
    return im


def black_and_white(im):
    im = im.convert('1')
    im = im.convert('L') # Converting to L due to bug in PIL
    return im


def triangulate_image(im, c_factor=None, b_factor=None, format_='png'):
    if c_factor is not None and b_factor is not None:
        im = process_image(im, c_factor, b_factor)
    points = get_points(im)
    triangulation = Delaunay(points)
    print("Number of points: {}".format(len(points)))
    render_tri(triangulation, im.width, im.height, c_factor, b_factor, format_)


def make_dir(directory='temp'):
    if not os.path.exists(directory):
        os.makedirs(directory)
    else:
        raise ValueError('Dir already exists')


def grid_search(im, max_attempts=10):
    make_dir()
    attempt = 0
    image = grayscale_image(im)
    for contrast_factor in np.linspace(0.0001, 1, max_attempts):
        for bright_factor in np.linspace(1, 4, max_attempts):
            attempt += 1
            print('Attempt {} of {}'.format(attempt, max_attempts * max_attempts))
            im = image
            im = process_image(im, contrast_factor, bright_factor)

            points = get_points(im)
            print(len(points), contrast_factor, bright_factor)
            if len(points) < MIN_POINTS and len(points) > 10:
                triangulate_image(image, contrast_factor, bright_factor)


def main():
    if len(sys.argv) is not 2:
        raise ValueError("You need to input an image.")
    args = sys.argv[1:]
    filename = args[0]

    image = Image.open(filename)
    maxsize = (900, 900)
    image.thumbnail(maxsize, PIL.Image.ANTIALIAS)
    width, height = image.size

    image = grayscale_image(image)
    image = fade_image(image)
    image = black_and_white(image)
    triangulate_image(image, format_='png')
    image.save('out2.png')
    # grid_search(image)
