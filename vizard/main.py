from __future__ import print_function

### BLOCK CONFIGURATION

SPEED = SLOW, FAST = 'SLOW', 'FAST'
WEIGHT = UNWEIGHTED, WEIGHTED = 'UNWEIGHTED', 'WEIGHTED'
HANDEDNESS = DOMINANT, NONDOMINANT = 'DOMINANT', 'NONDOMINANT'
PATH_SELECTION = RANDOM, SQUARE = 'RANDOM', 'SQUARE'

BLOCKS = [
    # every subject starts with a practice block.
    (SLOW, UNWEIGHTED, DOMINANT, RANDOM),

    # configure blocks for a subject here. each line must be a 4-tuple:
    #     (SPEED, WEIGHT, HANDEDNESS, PATH_SELECTION),
    (SLOW, UNWEIGHTED, DOMINANT, RANDOM),
    (SLOW, WEIGHTED, DOMINANT, RANDOM),
    (SLOW, UNWEIGHTED, DOMINANT, RANDOM),
    (SLOW, WEIGHTED, DOMINANT, RANDOM),
    (SLOW, UNWEIGHTED, DOMINANT, RANDOM),
    (SLOW, WEIGHTED, DOMINANT, RANDOM),
]

TRIALS_PER_BLOCK = 10

### EXPERIMENT CODE BELOW


# python imports
import datetime
import logging
import os
import random
import shutil

# vizard imports
import nvis
import viz
import vizact
import vizconfig
import vizproximity
import vizshape
import viztask

# local imports
import vrlab

# module constants
DESKTOP = 'C:\\Documents and Settings\\vrlab\\Desktop'

SPEED_MEANS = 0.5, 0.8
SPEED_STD = 0.1

PATH_SCALE = 0.7, 0.7, 0.7
PATH_TRANSLATE = 0, 1.3, 0


def distance(obj1, obj2):
    '''Return the (squared) Euclidean distance between two objects.'''
    x1, y1, z1 = obj1.getPosition()
    x2, y2, z2 = obj2.getPosition()
    return (x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2


class Trial(vrlab.Trial):
    '''Manage a single trial of the tracing experiment.

    This class handles trial setup (displaying the path to trace, moving the
    target), running (moving the target, recording mocap and trial information,
    and teardown (showing the movement, removing the path, saving the recorded
    information).
    '''

    def __init__(self, block, name, vertices, speed):
        super(Trial, self).__init__()

        self.block = block
        self.name = name
        self.vertices = vertices
        self.speed = speed

        self.finger = None
        self.path = None
        self.trace = []
        self.trace_color = None
        self.trace_name = ''

        header = ['frame', 'elapsed_time',
                  'target_x', 'target_y', 'target_z',
                  'finger_x', 'finger_y', 'finger_z',
                  'head_x', 'head_y', 'head_z',
                  ]
        for mid in sorted(block.experiment.mocap.get_markers()):
            header.extend('{}_{}'.format(mid, f) for f in 'xyzc')
        self.records = [header]

    def setup(self):
        vrlab.sounds.cowbell.play()

        self.path = self.draw(self.vertices)
        self.path.color(0, 0, 0)

        yield viztask.waitTime(1)

        # move the last few frames to show target direction and speed.
        target = self.block.experiment.target
        target.setPosition(self.vertices[-10])
        for v in self.vertices[-10:]:
            yield viztask.addAction(
                target, vizact.moveTo(v, speed=self.speed))
        target.setPosition(self.vertices[0])

    def run(self):
        exp = self.block.experiment

        lf = exp.left_finger
        rf = exp.right_finger

        # wait for the subject to touch the target sphere.
        yield self.block.experiment.wait_for_target()

        # target touched, now figure out which hand is doing the tracing.
        left_is_closer = distance(lf, exp.target) < distance(rf, exp.target)
        finger = lf if left_is_closer else rf
        self.trace_color = (1, 0, 0) if left_is_closer else (0, 1, 0)
        self.trace_name = 'left' if left_is_closer else 'right'

        # animate the target along the path, recording mocap data as we go.
        start = viz.tick()
        for i, v in enumerate(self.vertices):
            # ramp up the speed linearly from 0.
            s = min(1, 0.1 * (i+1)) * self.speed
            yield viztask.addAction(exp.target, vizact.moveTo(v, speed=s))

            # keep track of the position of the tracing finger.
            finger_position = finger.getPosition()
            self.trace.append(finger_position)

            # record values from the simulation and from the mocap.
            fields = [i, viz.tick() - start]
            fields.extend(exp.target.getPosition())
            fields.extend(finger_position)
            fields.extend(exp.head.get_pose().pos)
            for _, marker in sorted(exp.mocap.get_markers().iteritems()):
                fields.extend(marker.pos)
                fields.append(marker.cond)
            self.records.append(fields)

    def teardown(self):
        trace = self.draw(self.trace)
        trace.color(*self.trace_color)

        self.write_records()

        yield viztask.waitTime(7)

        self.path.remove()
        trace.remove()

    def draw(self, vertices):
        viz.startLayer(viz.LINE_LOOP)
        viz.lineWidth(10)
        for v in vertices:
            viz.vertex(*v)
        return viz.endLayer()

    def write_records(self):
        stamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        output = os.path.join(self.block.output,
            '{}-{}-{}-speed_{:.3f}.csv'.format(
                stamp, self.name, self.trace_name, self.speed))
        with open(output, 'w') as handle:
            for fields in self.records:
                print(','.join(str(f) for f in fields), end='\n', file=handle)
        logging.info('trial output %s', os.path.basename(output))


class Block(vrlab.Block):
    '''Manage a block of trials in the tracing experiment.

    This class handles block setup (playing a sound, making a directory for
    recording data) and generates trials in the block by choosing appropriate
    paths and so forth.
    '''

    def __init__(self,
                 experiment,
                 block_num,
                 weight,
                 speed,
                 hand,
                 paths,
                 num_trials=TRIALS_PER_BLOCK,
                 scale=PATH_SCALE,
                 translate=PATH_TRANSLATE):
        super(Block, self).__init__()

        self.experiment = experiment
        self.speed_mean = SPEED_MEANS[speed == FAST]
        self.speed_std = SPEED_STD
        self.output = os.path.join(
            experiment.output, 'block{}-{}-{}-{}-{}'.format(
                block_num, weight, speed, hand, paths))

        if paths == SQUARE:
            self.path_names = ['square' for _ in range(num_trials)]
        else:
            # fill our block with trials drawn randomly from available paths.
            names = [l.replace('.txt', '') for l in os.listdir('paths')
                     if l.endswith('.txt') and l.startswith('1')]
            self.path_names = [random.choice(names) for _ in range(num_trials)]

        self.scale = scale
        self.translate = translate

        logging.info('NEW BLOCK -- %s %s %s %s', weight, speed, hand, paths)

    def setup(self):
        if not os.path.isdir(self.output):
            os.makedirs(self.output)
        vrlab.sounds.gong.play()
        yield viztask.waitKeyDown(' ')

    def generate_trials(self):
        for path_name in self.path_names:
            s = random.normalvariate(self.speed_mean, self.speed_std)
            yield Trial(self, path_name, self.load_path(path_name), speed=s)

    def load_path(self, path_name):
        sx, sy, sz = self.scale
        tx, ty, tz = self.translate

        path = []
        with open(os.path.join('paths', '{}.txt'.format(path_name))) as handle:
            for l in handle:
                try:
                    x, y, z = map(float, l.strip().split('#')[0].strip().split())
                except:
                    continue
                path.append((sx * x + tx, sy * y + ty, sz * z + tz))

        # start the path at a random place, and reverse it half the time.
        start = random.randint(0, len(path) - 1)
        path = path[start:] + path[:start]
        if random.random() < 0.5:
            path = path[::-1]

        return path


class Experiment(vrlab.Experiment):
    '''Manage a series of blocks in the tracing experiment.

    This class handles global experiment setup for a single subject. To set up,
    we turn on the motion-capture thread, create some experiment-relevant
    Vizard objects for representing the fingers and target, and creating a
    virtual environment for the tracing.

    We ultimately generate a series of experiment blocks by using the
    parameters set at the top of the module.
    '''

    def __init__(self, target_signal=None, motion='suit'):
        super(Experiment, self).__init__()

        self.left_finger = vizshape.addSphere(0.02, color=viz.RED)
        self.right_finger = vizshape.addSphere(0.02, color=viz.GREEN)
        self.target = vizshape.addSphere(0.05, color=viz.WHITE)
        self.target_signal = target_signal

        self.setup_world()
        self.setup_mocap(motion)
        self.setup_proximity()

    def setup_world(self):
        viz.setOption('viz.fullscreen.monitor', 1)
        #viz.setOption('viz.window.width', 2560)
        #viz.setOption('viz.window.height', 1040)
        #viz.setMultiSample(4)
        #viz.MainWindow.clip(0.01, 500)
        #viz.vsync(1)

        vizconfig.register(nvis.nvisorSX111())

        viz.go(viz.FULLSCREEN)

    def setup_mocap(self, motion):
        self.mocap = vrlab.Phasespace('192.168.1.230', postprocess=True)
        self.mocap.start_thread()

        left_finger_id = None
        right_finger_id = None
        if motion == 'suit':
            self.head = self.mocap.track_rigid(6, center_markers=(3, 5))
            self.motion = self.mocap.track_points(range(6, 50))
            left_finger_id = 25
            right_finger_id = 13
        elif motion == 'glove':
            self.head = self.mocap.track_rigid([0, 2, 4, 6, 8, 10], [4, 8])
            self.motion = self.mocap.track_points([38, 40, 42, 44])
            left_finger_id = 44
            right_finger_id = 0
        else:
            assert False, 'unknown motion source "{}"'.format(motion)

        self.head.link_pose(viz.MainView)
        vizact.onkeydown('r', self.head.reset)

        if left_finger_id:
            self.motion.link_marker(left_finger_id, self.left_finger)
        if right_finger_id:
            self.motion.link_marker(right_finger_id, self.right_finger)

    def setup_proximity(self):
        sensor = vizproximity.addBoundingSphereSensor(self.target, scale=0.7)

        prox = vizproximity.Manager()
        #prox.setDebug(viz.ON)

        prox.addSensor(sensor)
        prox.addTarget(self.left_finger)
        prox.addTarget(self.right_finger)

        prox.onEnter(sensor, lambda e: vrlab.sounds.drip.play())
        prox.onEnter(sensor, lambda e: self.target.color(viz.BLUE))
        if self.target_signal:
            prox.onEnter(sensor, self.target_signal.send)

        prox.onExit(sensor, lambda e: self.target.color(viz.WHITE))

    def wait_for_target(self):
        if self.target_signal:
            yield self.target_signal.wait()
        else:
            yield viztask.waitKeyDown(' ')

    def setup(self):
        yield viztask.waitTime(3)

        self.head.reset()

        stamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        self.output = os.path.join(
            DESKTOP, 'tracing-data', '{}-{:08x}'.format(
            stamp, random.randint(0, 0xffffff)))
        logging.info('storing output in %s', self.output)

        self.environment = viz.addChild('dojo.osgb')

    def teardown(self):
        self.environment.remove()

        name = os.path.basename(self.output)
        target = os.path.join(DESKTOP, 'leif', 'measurements', name)
        if not os.path.isdir(target):
            shutil.copytree(self.output, target)

    def generate_blocks(self):
        for i, (speed, weight, hand, paths)in enumerate(BLOCKS):
            yield Block(self, block_num=i, weight=weight, speed=speed, hand=hand, paths=paths)


if __name__ == '__main__':
    logging.basicConfig(
            stream=sys.stdout,
            level=logging.DEBUG,
            format='%(levelname).1s %(asctime)s %(name)s:%(lineno)d %(message)s',
        )
    Experiment(viztask.Signal(), motion='suit').main()
