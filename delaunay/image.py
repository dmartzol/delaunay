from delaunay.utils import clamp
from delaunay.settings import FADE, BLACK_LIMIT, WHITE_LIMIT
import numpy as np
from PIL import ImageEnhance, Image


def raster_points(points, shape):
    """
    points: numpy array with the black points
    shape: dimensions of image where the points will be draw
    ---
    Returns a PIL image in mode L
    """

    # Creating white image array
    image_array = np.full(shape, 255)
    points = points.astype(int)
    for point in points:
        x = point[0]
        y = point[1]
        image_array[y][x] = 0
    stippled = Image.fromarray(image_array.astype('uint8'), 'L')
    return stippled


def get_points(image):
    """
    Finds every black point in a B&W image and returns their position in a numpy array.
    Image has to be mode 1 (not grayscale).
    """
    points = []
    if image.mode is not 'L':
        raise ValueError('Image should be mode L')
    for x in range(image.width):
        for y in range(image.height):
            if image.getpixel((x, y)) == 0:
                points.append([x, y])
    return np.array(points)


def process_image(image, contrast_factor, bright_factor):
    image = change_contrast(image, contrast_factor)
    image = change_brigthness(image, bright_factor)
    return image


def change_contrast(image, contrast_factor):
    contrast = ImageEnhance.Contrast(image)
    image = contrast.enhance(contrast_factor)
    return image


def change_brigthness(image, bright_factor):
    brightness = ImageEnhance.Brightness(image)
    image = brightness.enhance(bright_factor)
    return image


def grayscale_image(image):
    image = image.convert('L')
    image = fade_image(image)
    return image


def fade_image(image):
    for x in range(image.width):
        for y in range(image.height):
            value = image.getpixel((x, y))
            image.putpixel((x, y), linear_fade(value))
    return image


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


def dither(image):
    dithered = grayscale_image(image)
    dithered = fade_image(dithered)
    dithered = black_and_white(dithered)
    return dithered


def grayish_black(x):
    # Incrementing the limit makes the blacks whiter
    if x < BLACK_LIMIT:
        return BLACK_LIMIT
    return x


def fade_all(x):
    # Incrementing the fade makes the image whiter
    return clamp(x + FADE)


def black_and_white(image):
    image = image.convert('1')
    # Converting to L due to bug in PIL
    image = image.convert('L')
    return image
