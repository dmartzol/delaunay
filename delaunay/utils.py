import os


def clamp(x):
    if x < 0:
        return 0
    if x > 255:
        return 255
    return x


def make_dir(directory='temp'):
    if not os.path.exists(directory):
        os.makedirs(directory)
    else:
        raise ValueError('Dir already exists')
