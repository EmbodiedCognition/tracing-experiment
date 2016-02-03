import climate
import matplotlib.pyplot as plt
import numpy as np

from mpl_toolkits.mplot3d import Axes3D

import constants as C
import util

TARGET = C.cols('target-x', 'target-y', 'target-z')


def main(dataset='measurements.npy'):
    data = np.load(dataset, mmap_mode='r')
    print 'loaded', dataset, data.shape

    fig = plt.figure()
    ax = util.axes(fig, 111)

    trial = data[15, 1, 5]
    for f in range(0, len(trial), 300):
        util.plot_skeleton(ax, trial[f], alpha=1)
    x, y, z = trial[:, TARGET].T
    ax.plot(x, z, y, 'o-', color='#111111', alpha=0.5)

    util.set_limits(ax, center=(0, 0, 1), span=1)

    ax.w_xaxis.set_pane_color((1, 1, 1, 1))
    ax.w_yaxis.set_pane_color((1, 1, 1, 1))
    ax.w_zaxis.set_pane_color((1, 1, 1, 1))

    #plt.gcf().set_size_inches(12, 10)
    #plt.savefig('single-trial.pdf', dpi=600)
    plt.show()


if __name__ == '__main__':
    climate.call(main)
