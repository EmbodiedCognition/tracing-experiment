#!/usr/bin/env python

import matplotlib.pyplot as plt
import numpy as np
import os

# enable 3d plots
from mpl_toolkits.mplot3d import Axes3D


def list_paths():
    for f in os.listdir('paths'):
        yield f.split('.')[0], np.loadtxt('paths/{}'.format(f))


def main():
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(*np.loadtxt('paths/circle.txt').T)
    ax.plot(*np.loadtxt('paths/triangle.txt').T)
    ax.plot(*np.loadtxt('paths/square.txt').T)
    for name, path in list_paths():
        if np.random.random() < 0.03:
            ax.plot(*path.T)
    plt.show()


if __name__ == '__main__':
    main()
