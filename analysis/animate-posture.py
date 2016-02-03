import climate
import matplotlib.pyplot as plt
import matplotlib.animation as anim
import numpy as np

import constants as C
import util


def main(dataset='measurements.npy'):
    X = np.load(dataset, mmap_mode='r')
    print 'loaded', dataset, X.shape

    trial = X[0, 0, 0]
    fig = plt.figure()
    ax = util.axes(fig)
    lines = [ax.plot([], [], [], '.-', c='#111111')[0] for s in C.SKELETON]

    def init():
        for l in lines:
            l.set_data([], [])
            l.set_3d_properties([])
        return lines

    def draw(f):
        frame = trial[f % len(trial)]
        markers = frame[17:].reshape((-1, 4))
        for i, l in enumerate(lines):
            x, y, z = np.array(
                [util.identity(frame, markers[m, :3])
                 for m in C.SKELETON[i] if markers[m, 3] > 0]).T
            l.set_data(x, z)
            l.set_3d_properties(y)
        #ax.view_init(30, 0.3 * f)
        fig.canvas.draw()
        return lines

    a = anim.FuncAnimation(
        fig, draw, init_func=init, frames=240, interval=10, blit=False)
    #a.save('/tmp/trial.mp4', fps=15, extra_args=['-vcodec', 'libx264'])

    util.set_limits(ax, center=(0, 0, 0))
    plt.show()


if __name__ == '__main__':
    climate.call(main)
