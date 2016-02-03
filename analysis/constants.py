'''Constants for tracing experiments.'''

import matplotlib
import numpy as np

WEIGHTED = 1
UNWEIGHTED = 0
FAST = 11
SLOW = 10
DOMINANT = 101
NONDOMINANT = 100
SQUARE = 1001
RANDOM = 1000
left = 10001
right = 10000

CONSTANTS = {
    'WEIGHTED': WEIGHTED,
    'UNWEIGHTED': UNWEIGHTED,
    'FAST': FAST,
    'SLOW': SLOW,
    'DOMINANT': DOMINANT,
    'NONDOMINANT': NONDOMINANT,
    'SQUARE': SQUARE,
    'RANDOM': RANDOM,
    'left': left,
    'right': right,
}

COLUMNS = (
    'block-weight',
    'block-speed',
    'block-hand',
    'block-paths',

    'trial-hand',
    'trial-speed',

    'frame',
    'elapsed',

    'target-x', 'target-y', 'target-z',
    'finger-x', 'finger-y', 'finger-z',
    'head-x', 'head-y', 'head-z',

    'm000-x', 'm000-y', 'm000-z', 'm000-c',
    'm001-x', 'm001-y', 'm001-z', 'm001-c',
    'm002-x', 'm002-y', 'm002-z', 'm002-c',
    'm003-x', 'm003-y', 'm003-z', 'm003-c',
    'm004-x', 'm004-y', 'm004-z', 'm004-c',
    'm005-x', 'm005-y', 'm005-z', 'm005-c',
    'm006-x', 'm006-y', 'm006-z', 'm006-c',
    'm007-x', 'm007-y', 'm007-z', 'm007-c',
    'm008-x', 'm008-y', 'm008-z', 'm008-c',
    'm009-x', 'm009-y', 'm009-z', 'm009-c',
    'm010-x', 'm010-y', 'm010-z', 'm010-c',
    'm011-x', 'm011-y', 'm011-z', 'm011-c',
    'm012-x', 'm012-y', 'm012-z', 'm012-c',
    'm013-x', 'm013-y', 'm013-z', 'm013-c',
    'm014-x', 'm014-y', 'm014-z', 'm014-c',
    'm015-x', 'm015-y', 'm015-z', 'm015-c',
    'm016-x', 'm016-y', 'm016-z', 'm016-c',
    'm017-x', 'm017-y', 'm017-z', 'm017-c',
    'm018-x', 'm018-y', 'm018-z', 'm018-c',
    'm019-x', 'm019-y', 'm019-z', 'm019-c',
    'm020-x', 'm020-y', 'm020-z', 'm020-c',
    'm021-x', 'm021-y', 'm021-z', 'm021-c',
    'm022-x', 'm022-y', 'm022-z', 'm022-c',
    'm023-x', 'm023-y', 'm023-z', 'm023-c',
    'm024-x', 'm024-y', 'm024-z', 'm024-c',
    'm025-x', 'm025-y', 'm025-z', 'm025-c',
    'm026-x', 'm026-y', 'm026-z', 'm026-c',
    'm027-x', 'm027-y', 'm027-z', 'm027-c',
    'm028-x', 'm028-y', 'm028-z', 'm028-c',
    'm029-x', 'm029-y', 'm029-z', 'm029-c',
    'm030-x', 'm030-y', 'm030-z', 'm030-c',
    'm031-x', 'm031-y', 'm031-z', 'm031-c',
    'm032-x', 'm032-y', 'm032-z', 'm032-c',
    'm033-x', 'm033-y', 'm033-z', 'm033-c',
    'm034-x', 'm034-y', 'm034-z', 'm034-c',
    'm035-x', 'm035-y', 'm035-z', 'm035-c',
    'm036-x', 'm036-y', 'm036-z', 'm036-c',
    'm037-x', 'm037-y', 'm037-z', 'm037-c',
    'm038-x', 'm038-y', 'm038-z', 'm038-c',
    'm039-x', 'm039-y', 'm039-z', 'm039-c',
    'm040-x', 'm040-y', 'm040-z', 'm040-c',
    'm041-x', 'm041-y', 'm041-z', 'm041-c',
    'm042-x', 'm042-y', 'm042-z', 'm042-c',
    'm043-x', 'm043-y', 'm043-z', 'm043-c',
    'm044-x', 'm044-y', 'm044-z', 'm044-c',
    'm045-x', 'm045-y', 'm045-z', 'm045-c',
    'm046-x', 'm046-y', 'm046-z', 'm046-c',
    'm047-x', 'm047-y', 'm047-z', 'm047-c',
    'm048-x', 'm048-y', 'm048-z', 'm048-c',
    'm049-x', 'm049-y', 'm049-z', 'm049-c',
)

def col(name):
    return COLUMNS.index(name)

def cols(*names):
    if len(names) == 1:
        names = names[0] # assume we got a generator arg
    return [col(n) for n in names]


SKELETON = (
    # right leg
    [34, 44, 45, 46], #47, 48, 49],
    # left leg
    [35, 37, 38, 39], #40, 41, 42],
    # right arm
    [32, 6, 7, 8, 9, 15],
    # left arm
    [32, 18, 19, 20, 21, 27],
    # right hand
    [10, 14, 11, 14, 12, 15, 13, 15, 16, 17],
    # left hand
    [26, 22, 26, 23, 27, 24, 27, 25, 28, 29],
    # head + torso
    [1, 4, 5, 3, 2, 0, 32, 33, 34, 35, 36, 43, 30, 31],
)

SKELETON_COLORS = matplotlib.cm.winter(np.linspace(0, 1, len(SKELETON)))
MARKER_COLORS = matplotlib.cm.Set1(np.linspace(0, 1, 50))
