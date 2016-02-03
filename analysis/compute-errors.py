import climate
import collections
import lmj.plot
import numpy as np

from sklearn.linear_model import LinearRegression

import constants as C

GROUPS = (
    (C.WEIGHTED, C.DOMINANT),
    (C.UNWEIGHTED, C.DOMINANT),
    (C.WEIGHTED, C.NONDOMINANT),
    (C.UNWEIGHTED, C.NONDOMINANT),
)

PAIRS = (
    ('target', 'finger'),
    ('target', 'head'),
    ('finger', 'head'),
)

def distances(trial, src='target', tgt='finger'):
    src = trial[:, C.cols('{}-{}'.format(src, x) for x in 'xyz')]
    tgt = trial[:, C.cols('{}-{}'.format(tgt, x) for x in 'xyz')]
    return 1000 * np.sqrt(((src - tgt) ** 2).sum(axis=1))


@climate.annotate(
    dataset='dataset to plot',
    plot_mean=('if 1, plot means, else stdevs', 'option', None, int),
)
def main(dataset='measurements.npy', plot_mean=0):
    plot_mean = plot_mean > 0

    X = np.load(dataset, mmap_mode='r')
    print 'loaded', dataset, X.shape

    series = collections.defaultdict(list)

    for subject in X:
        for block in subject:
            for trial in block:
                weight = trial[0, C.col('block-weight')]
                if weight != C.UNWEIGHTED:
                    continue
                hand = trial[0, C.col('block-hand')]
                if hand != C.DOMINANT:
                    continue
                speed = trial[0, C.col('trial-speed')]
                for src, tgt in PAIRS:
                    d = distances(trial, src, tgt)
                    series[src, tgt].append((speed, d.mean(), d.std()))

    for i, (src, tgt) in enumerate(PAIRS):
        speed, mean, std = np.array(series[(src, tgt)]).T
        dependent = [std, mean][plot_mean]
        model = LinearRegression()
        model.fit(speed[:, None], np.log(dependent))
        idx = np.arange(len(speed))
        np.random.shuffle(idx)

        spines = []
        if i == 0:
            spines.append('left')
        if not plot_mean:
            spines.append('bottom')
        ax = lmj.plot.axes((1, len(series), i + 1), spines=spines)

        #ax.errorbar(speed, mean, yerr=std, fmt='o', alpha=0.9)
        ax.plot(speed[idx[:100]], dependent[idx[:100]], 'o', color='#111111', alpha=0.7)
        ax.plot([speed.min(), speed.max()],
                np.exp(model.predict([[speed.min()], [speed.max()]])),
                '-', color='#cc3333', lw=3)

        ax.set_ylim((10, 1000))
        ax.set_yscale('log')
        if plot_mean:
            ax.set_title('{} - {}'.format(src.capitalize(), tgt.capitalize()))
            ax.set_xticks([])
            ax.xaxis.set_ticks_position('none')
        else:
            ax.set_xlabel('Tracing Speed (m/s)')
        if i == 0:
            ax.set_ylabel('{} Distance (mm)'.format(['SD of', 'Mean'][plot_mean]))
        else:
            ax.set_yticks([])
            ax.yaxis.set_ticks_position('none')

    out = 'error-vs-speed-{}.pdf'.format(['std', 'mean'][plot_mean])
    print 'saving', out
    lmj.plot.gcf().set_size_inches(12, 3)
    lmj.plot.savefig(out, dpi=600)
    #lmj.plot.show()


if __name__ == '__main__':
    climate.call(main)
