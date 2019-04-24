
# (C) CS 4410 Fall 2018 Staff, Cornell University
# All rights reserved

from rvr_sync_wrapper import MP, MPthread
import random
import signal

signal.signal(signal.SIGINT, signal.SIG_DFL)

#   Complete the implementation of the GraphicsEngine monitor using MP Locks and
#   MP Condition variables

################################################################################
## DO NOT WRITE OR MODIFY ANY CODE ABOVE THIS LINE #############################
################################################################################

class GraphicsEngine(MP):
    """ This monitor simulates a simplified graphics rendering engine for an on-
        screen physics simulation.

    Simple simulations are done on a per-frame basis. This means that each frame
    can be viewed as a 2D array of pixels (like an image). When displayed on
    screen in rapid succession, the frames make up a video - which we will refer
    to as the "simulation."

    Each simulation as begins at frame 0. To progress, we loop through all the
    pixels on the current frame and compute the pixel's value for the next frame.
    When a frame is completed, it will be displayed on screen by some external
    mechanism.

    Note that each frame must be fully computed before being displayed, or the
    simulation will appear "choppy." The GraphicsEngine specification adheres to
    this rule for all frames until either the simulation ends or is interrupted.

    On a single thread, the computation may be too slow so we will parallelize
    the workload to speed things up. This is commonly implemented in chunks -
    which splits up the work amongst worker threads which run in parallel.

    Your job here is to implement the engine that controls the worker threads
    to prevent choppy simulations.

    Clarification points:
    - You do not need to implement any computation or chunking.
    - Python can't actually parallelize within a single process because of the
    GIL. Think of this prompt as an academic exercise.
    """

    def __init__(self, num_workers):
        """ Initializes an instance of GraphicsEngine. Shared resources and locks
            get created in here.

        """
        MP.__init__(self)
        # TODO implement me
        self.finished_count = self.Shared("the number of worker that has finished current frame", 0)
        self.lock = self.Lock("basic lock")
        self.all_finished_cv = self.lock.Condition("all workers have finished current frame")
        self.NUM_WORKERS = num_workers
        self.guard = 0


    def start_next_frame(self):
        """ Called by a worker thread who has just completed its work on current
            frame.

        Wait until all other workers are done with current frame before starting
        on the next frame.
        """
        # TODO implement me
        with self.lock:
            self.finished_count.inc()
            my_guard = self.guard
            if self.finished_count.read() < self.NUM_WORKERS:
                while my_guard == self.guard:
                    self.all_finished_cv.wait()
            else:
                self.finished_count.write(0)
                self.guard += 1
                self.all_finished_cv.broadcast()


################################################################################
## DO NOT WRITE OR MODIFY ANY CODE BELOW THIS LINE #############################
################################################################################

class Worker(MPthread):

    def __init__(self, engine, name, id):
        MPthread.__init__(self, engine, name)
        self.engine = engine
        self.id = id


    def run(self):
        frame_no = 0
        while True:
            # wait for other workers from previous frame to finish
            #print('worker {} trying to start frame {}'.format(self.id, frame_no))
            self.engine.start_next_frame()

            # work on current frame
            self.delay(random.randint(0, 2))
            print('worker {} finished on frame {}'.format(self.id, frame_no))
            frame_no += 1


if __name__ == '__main__':

    NUM_THREADS = 10
    engine = GraphicsEngine(num_workers=NUM_THREADS)
    for i in range(NUM_THREADS):
        Worker(engine, 'Worker {}'.format(i), i).start()

    engine.Ready()
