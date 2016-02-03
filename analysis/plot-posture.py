import climate
import matplotlib.pyplot as plt
import numpy as np

from mpl_toolkits.mplot3d import Axes3D

import constants as C
import util

TARGET = C.cols('target-x', 'target-y', 'target-z')
N = 2
X = ((0.4, 0.6), (-0.6, -0.4)) # -0.6 to 0.6
Y = ((1.7, 1.9), (0.6, 0.8)) # 0.6 to 1.9
Z = (-0.1, 0.1) # -0.6 to 0.6


def within_region(frame, i):
    b, a = divmod(i, N)
    x, y, z = frame[TARGET]
    return (X[a][0] < x < X[a][1] and
            Y[b][0] < y < Y[b][1] and
            Z[0] < z < Z[1])


def main(dataset='measurements.npy'):
    data = np.load(dataset, mmap_mode='r')
    print 'loaded', dataset, data.shape

    plots = list(range(N * N))
    frames = [[] for _ in plots]
    for subj in data:
        for block in subj[1:]:
            for trial in block:
                if trial[0, C.col('trial-hand')] == C.right:
                    for frame in trial:
                        for i in plots:
                            if within_region(frame, i):
                                frames[i].append(frame)
                                break

    u, v = np.mgrid[0:2 * np.pi:11j, 0:np.pi:7j]
    sphx = np.cos(u) * np.sin(v)
    sphy = np.sin(u) * np.sin(v)
    sphz = np.cos(v)

    fig = plt.figure()
    for i, postures in enumerate(frames):
        if not postures:
            continue
        if i != 2:
            continue

        postures = np.array(postures)
        for m in range(50):
            marker = postures[:, 17+m*4:17+(m+1)*4]
            drops = marker[:, 3] < 0
            marker[drops, :3] = marker[~drops, :3].mean(axis=0)
        means = postures.mean(axis=0)
        stds = postures.std(axis=0)

        #ax = util.axes(fig, 111)
        #for frame in postures[::5]:
        #    util.plot_skeleton(ax, frame, alpha=0.1)
        ax = util.axes(fig, 110 * N + i + 1)
        util.plot_skeleton(ax, means, alpha=1.0)
        for m in range(50):
            mx, my, mz = means[17+m*4:20+m*4]
            sx, sy, sz = stds[17+m*4:20+m*4] / 2
            ax.plot_wireframe(sphx * sx + mx, sphz * sz + mz, sphy * sy + my,
                              color=C.MARKER_COLORS[m], alpha=0.3)

        #tgtx, tgty, tgtz = postures.mean(axis=0)[
        #    C.cols('target-x', 'target-y', 'target-z')]
        #ax.plot([tgtx], [tgtz], [tgty], 'o', color='#111111')

        #for m in range(50):
        #    marker = postures[:, 17 + 4 * m:17 + 4 * (m+1)]
        #    position = marker.mean(axis=0)
        #    size = marker.std(axis=0)
        #    ax.plot_surface()

        util.set_limits(ax, center=(0, -0.5, 1), span=1)
        ax.w_xaxis.set_pane_color((1, 1, 1, 1))
        ax.w_yaxis.set_pane_color((1, 1, 1, 1))
        ax.w_zaxis.set_pane_color((1, 1, 1, 1))
        ax.set_title(['Top Right', 'Top Left', 'Bottom Right', 'Bottom Left'][i])

    #for m in range(50):
    #    x, z, y = frame[m*4:m*4+3]
    #    ax.text(x, y, z, str(m))

    plt.gcf().set_size_inches(12, 10)
    #plt.savefig('reach-targets-with-variance.pdf', dpi=600)
    plt.show()


if __name__ == '__main__':
    climate.call(main)
