from __future__ import print_function

import climate
import numpy as np
import os
import re

from constants import constants as C

logging = climate.get_logger('import-csvs')


def main(root='/tmp/measurements', output=None):
    data = []
    for s in os.listdir(root):
        subject = []
        for b in os.listdir(os.path.join(root, s)):
            block = []
            bweight, bspeed, bhand, bpaths = b.split('-')[1:]
            for t in os.listdir(os.path.join(root, s, b)):
                thand, tspeed = re.search(r'(left|right)-speed_(\d\.\d+)', t).groups()
                config = np.tile([
                    C[bweight], C[bspeed], C[bhand], C[bpaths],
                    C[thand], float(tspeed)], (120, 1))
                block.append(
                    np.hstack([
                        config,
                        np.loadtxt(os.path.join(root, s, b, t),
                                   skiprows=1, delimiter=',')]))
            subject.append(block)
        if len(subject) == 3:
            data.append(subject)
        else:
            print('incorrect block count! discarding {}'.format(s))
    data = np.array(data)
    logging.info('loaded data %s', data.shape)
    if output:
        np.save(output, data.astype('f'))


if __name__ == '__main__':
    climate.call(main)
