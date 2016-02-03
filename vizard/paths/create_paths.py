#!/usr/bin/env python

from __future__ import print_function

import climate
import lmj.sim
import lmj.sim.viewer
import logging
import numpy as np
import time


class World(lmj.sim.physics.World):
    def on_key_press(self, key, keys):
        if key == keys.W:
            self.write()

    def step(self):
        super(World, self).step()

        now = time.time()

        if now - self.wrote > 300:
            self.write()
            self.reset()
            self.wrote = now

        n = len(self.balls)
        for i, b in enumerate(self.balls):
            if self.sides == 0 and np.random.random() < 1. / n:
                rnd = np.random.randn(3)
                rnd /= np.linalg.norm(rnd)
                rad = b.position - self.center_of_mass()
                rad /= np.linalg.norm(rad)
                b.force = 3000 * (0.7 * rnd + 0.3 * rad) / n
            if self.sides > 0 and 0 == i % (n // self.sides):
                t = 2 * np.pi * i / n
                b.force = 2 * np.cos(t), 2 * np.sin(t), 0

    def reset(self):
        ts = np.linspace(0, 2 * np.pi, len(self.balls) + 1)[:-1]
        for t, b in zip(ts, self.balls):
            b.position = np.cos(t), np.sin(t), 3
            b.quaternion = 1, 0, 0, 0
            b.linear_velocity = 0, 0, 0
            b.angular_velocity = 0, 0, 0
            b.force = 0, 0, 0

    def center_of_mass(self):
        return np.mean([b.position for b in self.balls], axis=0)

    def write(self):
        com = self.center_of_mass()
        output = '/tmp/paths/{}.txt'.format(int(time.time()))
        with open(output, 'w') as handle:
            for b in self.balls:
                line = '{} {} {}'.format(*(b.position - com))
                print(line, end='\n', file=handle)
        logging.info('wrote %s', output)

    def setup(self, count, zstop=np.pi / 100, rstop=np.pi / 10):
        self.wrote = time.time()

        def stiff(joint):
            joint.lo_stops = -zstop, -rstop
            joint.hi_stops = zstop, rstop
            joint.stop_cfms = 1e-3
            joint.stop_erps = 1e-1

        # create a planar shape of balls, connected with universal joints.
        self.balls = []
        self.positions = []
        for position in self._triangle(count):
            ball = self.create_body('sphere', radius=np.pi / count)
            ball.position = position
            if self.balls:
                radial = np.concatenate([position[:2], [0]])
                radial /= np.linalg.norm(radial)
                joint = self.join('uni', ball, self.balls[-1], anchor=ball.position)
                joint.axes = (0, 0, 1), radial
                stiff(joint)
            self.balls.append(ball)
            self.positions.append(position)

        # close the end of the path to the beginning.
        first = self.balls[0]
        last = self.balls[-1]
        joint = self.join('uni', last, first, anchor=last.position)
        joint.axes = (0, 0, 1), tuple(last.position[:2]) + (0, )
        stiff(joint)

        # anchor one ball to the world.
        #self.join('uni', first, anchor=first.position)

    def _circle(self, count):
        for t in np.linspace(0, 2 * np.pi, count + 1)[:-1]:
            yield np.cos(t), np.sin(t), 3

    def _square(self, count):
        per_side = count // 4
        assert per_side * 4 == count
        e = 2 * np.pi / 8
        for p in np.linspace(e, -e, per_side + 1)[:-1]:
            yield e, p, 3
        for p in np.linspace(e, -e, per_side + 1)[:-1]:
            yield p, -e, 3
        for p in np.linspace(-e, e, per_side + 1)[:-1]:
            yield -e, p, 3
        for p in np.linspace(-e, e, per_side + 1)[:-1]:
            yield p, e, 3

    def _triangle(self, count):
        per_side = count // 3
        assert per_side * 3 == count
        x = np.pi / np.sqrt(12)
        y = np.pi / 3
        m = np.sqrt(12) / 6
        for p in np.linspace(y, -y, per_side + 1)[:-1]:
            yield -x, p, 3
        for p in np.linspace(-x, x, per_side + 1)[:-1]:
            yield p, m * p - y / 2, 3
        for p in np.linspace(x, -x, per_side + 1)[:-1]:
            yield p, -m * p + y / 2, 3


def main(balls=120):
    world = World()
    world.gravity = 0, 0, 0
    world.sides = 0
    world.setup(int(balls))#, zstop=np.pi / 10)
    lmj.sim.viewer.Physics(world, paused=True).run()


if __name__ == '__main__':
    climate.call(main)
