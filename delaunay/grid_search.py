import numpy as np
from delaunay.utils import make_dir
from delaunay.image import grayscale_image, get_points, process_image, black_and_white
from delaunay.illustration import Illustration

MIN_POINTS = 20000


def grid_search(im, max_attempts=10, directory='temp'):
    make_dir(directory)
    attempt = 0
    original_image = grayscale_image(im)
    for contrast_factor in np.linspace(0.1, 3, max_attempts):
        for bright_factor in np.linspace(1.0, 3, max_attempts):
            attempt += 1
            print('Attempt {} of {}'.format(attempt, max_attempts * max_attempts))
            im = original_image
            im = process_image(im, contrast_factor, bright_factor)
            im = black_and_white(im)
            points = get_points(im)
            print(len(points), contrast_factor, bright_factor)
            # only triangulating images with not too many or not too few points
            if len(points) < MIN_POINTS and len(points) > 10:
                illustration = Illustration(im, dithered=im)
                filename = '{}/{}-{}.png'.format(
                    directory,
                    contrast_factor,
                    bright_factor)
                illustration.triangulate(filename=filename)
