import tqdm
import sys
import time
import scipy.misc
import scipy.ndimage
import numpy as np
import delaunay.voronoi as voronoi
from delaunay.settings import NUMBER_OF_POINTS, N_ITER, THRESHOLD, PIXELS_PER_REGION


class Stippler(object):
    def __init__(self, image):
        self.image = self.mode_L(image)
        self.density = self.density_array()
        self.shape = self.density.shape
        self.density_P = self.density.cumsum(axis=1)
        self.density_Q = self.density_P.cumsum(axis=1)
        self.points = None
        self.iteration = 0

    def mode_L(self, image):
        if image.mode is 'L':
            return image
        else:
            return image.convert('L')

    def find_points(self, mode='finite'):
        # Initialization
        points = self.initialization(NUMBER_OF_POINTS, self.density)
        print("Number points:", NUMBER_OF_POINTS)
        if mode is 'finite':
            print("Number iterations:", N_ITER)
            for i in tqdm.trange(N_ITER):
                regions, points = voronoi.centroids(points, self.density, self.density_P, self.density_Q)
        elif mode is 'infinite':
            start = time.time()
            print("Press Ctrl-C to stop.")
            try:
                while True:
                    regions, points = voronoi.centroids(points, self.density, self.density_P, self.density_Q)
                    self.iteration += 1
                    sys.stdout.write("\rIteration: %i" % self.iteration)
                    sys.stdout.flush()
            except KeyboardInterrupt:
                print('\n')
                t = (time.time() - start) / (60*60)
                print('{} hours'.format(round(t, 2)))

        self.points = points

    def density_array(self):
        density = np.array(self.image)
        zoom = (NUMBER_OF_POINTS * PIXELS_PER_REGION) / (density.shape[0] * density.shape[1])
        zoom = int(round(np.sqrt(zoom)))
        # If the image is big the zoom will be less than 1 and approximated to 0
        # We want to avoid this
        if zoom is not 0:
            density = scipy.ndimage.zoom(density, zoom, order=0)

        # Apply THRESHOLD onto image
        # Any color > THRESHOLD will be white
        density = np.minimum(density, THRESHOLD)
        density = 1.0 - self.normalize(density)
        return density

    def normalize(self, density):
        Vmin, Vmax = density.min(), density.max()
        if Vmax - Vmin > 1e-5:
            density = (density - Vmin) / (Vmax - Vmin)
        else:
            density = np.zeros_like(density)
        return density

    def initialization(self, n, density):
        """
        Return n points distributed over [xmin, xmax] x [ymin, ymax]
        according to (normalized) density distribution.

        with xmin, xmax = 0, density.shape[1]
             ymin, ymax = 0, density.shape[0]

        The algorithm here is a simple rejection sampling.
        """

        samples = []
        while len(samples) < n:
            X = np.random.uniform(0, density.shape[1], 10 * n)
            Y = np.random.uniform(0, density.shape[0], 10 * n)
            P = np.random.uniform(0, 1, 10 * n)
            index = 0
            while index < len(X) and len(samples) < n:
                x, y = X[index], Y[index]
                x_, y_ = int(np.floor(x)), int(np.floor(y))
                if P[index] < density[y_, x_]:
                    samples.append([x, y])
                index += 1
        return np.array(samples)
