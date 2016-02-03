import numpy as np

import constants as C


def rx(theta):
    ct = np.cos(theta)
    st = np.sin(theta)
    return np.array([[1, 0, 0], [0, ct, -st], [0, st, ct]])

def ry(theta):
    ct = np.cos(theta)
    st = np.sin(theta)
    return np.array([[ct, 0, st], [0, 1, 0], [-st, 0, ct]])

def rz(theta):
    ct = np.cos(theta)
    st = np.sin(theta)
    return np.array([[ct, -st, 0], [st, ct, 0], [0, 0, 1]])


def axes(fig, which=111):
    ax = fig.add_subplot(which, projection='3d')
    #ax.axis('off')
    return ax


TARGET = C.cols('target-x', 'target-y', 'target-z')
FINGER = C.cols('finger-x', 'finger-y', 'finger-z')
HEAD = C.cols('head-x', 'head-y', 'head-z')
atan = np.arctan2

def canonical(frame, marker):
    hx, hy, hz = frame[HEAD] - frame[FINGER]
    ax = 0#atan(hz, hy)
    ay = -atan(hx, hz)
    az = 0
    return np.dot(rx(ax), np.dot(ry(ay), marker - frame[FINGER]))


def identity(frame, marker):
    return marker


def plot_skeleton(ax, frame, transform=identity, **kwargs):
    markers = frame[17:].reshape((-1, 4))
    for m, color in enumerate(C.MARKER_COLORS):
        if markers[m, 3] > 0:
            x, y, z = transform(frame, markers[m, :3])
        ax.plot([x], [z], [y], 'o', c=color, **kwargs)
    for ms in C.SKELETON:
        try:
            x, y, z = np.array(
                [transform(frame, markers[m, :3])
                 for m in ms if markers[m, 3] > 0]).T
            ax.plot(x, z, y, '-', c='#111111', **kwargs)
        except ValueError:
            pass


def set_limits(ax, center=(0, 0, 1.5), span=1.5):
    cx, cy, cz = center
    ax.set_xlim((cx - span, cx + span))
    #ax.set_xlabel('X')
    ax.set_ylim((cy - span, cy + span))
    #ax.set_ylabel('Y')
    ax.set_zlim((cz - span, cz + span))
    #ax.set_zlabel('Z')
    # elevation, azimuth (orientation)
    ax.view_init(10, 145)
