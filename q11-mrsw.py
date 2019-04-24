
# (C) CS 4410 Fall 2018 Staff, Cornell University
# All rights reserved

from rvr_sync_wrapper import MP, MPthread
import random
import signal

signal.signal(signal.SIGINT, signal.SIG_DFL)

#    Modify the ReaderWriterManager below to fit the specification.

################################################################################
## DO NOT WRITE OR MODIFY ANY CODE ABOVE THIS LINE #############################
################################################################################

class ReaderWriterManager(MP):
    """ This problem simulates a variant of the classic Readers-Writers problem.

    Below, Multiple Reader Single Writer (MRSW) is implemented using Locks and
    Condition variables. The MRSW implementation below should enforce these
    invariants:

    1) At any time, multiple readers OR a single writer is allowed in the
    critical section (multiple writer may lead to corrupt data).
    2) In our case, "multiple readers" means any amount of readers.
    3) Readers and Writers may not simultaneously be in the critical section.

    The following code appears to meet these requirements. However there are
    2 issues within the implementation that make it less than ideal. Your job
    here is to modify the ReaderWriterManager to enforce safety and liveness
    for any amount of Readers and Writers efficiently.

    Some questions to help guide your modifications:
    1) Is it really necessary to broadcast everywhere?
    2) What if the ReaderWriterManager has to handle infinite streams of
    Readers and Writers? Can you think of a starvation case for this code?
    """

    def __init__(self):
        """ Initializes an instance of ReaderWriterManager. Shared resources and
            locks get created in here.

        """
        MP.__init__(self)
        self.monitor_lock = self.Lock('monitor lock')

        self.num_readers = self.Shared('readers currently reading', 0)
        self.num_writers = self.Shared('writers currently writing', 0)

        self.writer_can_enter = self.monitor_lock.Condition('writer must wait')
        self.reader_can_enter = self.monitor_lock.Condition('reader must wait')

        # flag to indicate writers are active
        self.writer_is_writing = False

        # counter to indicate waiting readers, this implementation perfer writers
        self.waiting_writers_count = self.Shared("writers currently waiting", 0)


    def reader_enter(self):
        """ Called by Reader thread whe trying to enter the critical section.

        Reaching the end of this function means that the Reader successfully
        enters the critical section.
        """
        with self.monitor_lock:
            while self.writer_is_writing:
                self.reader_can_enter.wait()
            self.num_readers.inc()


    def reader_exit(self):
        """ Called by Reader thread after leaving the critical section.

        """
        with self.monitor_lock:
            self.num_readers.dec()
            if self.num_readers.read() == 0:
                self.writer_can_enter.signal()


    def writer_enter(self):
        """ Called by Writer thread when trying to enter the critical section.

        Reaching the end of this function means that the Writer successfully
        enters the critical section.
        """
        with self.monitor_lock:
            self.waiting_writers_count.inc()
            while (self.num_readers.read() > 0) or self.writer_is_writing:
                self.writer_can_enter.wait()
            self.writer_is_writing = True
            self.waiting_writers_count.dec()
            self.num_writers.inc()


    def writer_exit(self):
        """ Called by Writer thread after leaving the critical section.

        """
        with self.monitor_lock:
            self.num_writers.dec()
            self.writer_is_writing = False
            if self.waiting_writers_count.read() > 0:
                self.writer_can_enter.signal()
            else:
                self.reader_can_enter.broadcast()


################################################################################
## DO NOT WRITE OR MODIFY ANY CODE BELOW THIS LINE #############################
################################################################################

class Reader(MPthread):
    def __init__(self, manager, num):
        MPthread.__init__(self, manager, num)
        self.manager = manager
        self.id = num


    def run(self):
        self.manager.reader_enter()

        ### BEGIN CRITICAL SECTION ###
        with self.manager.monitor_lock:
            print('reader {} inside. crit section: {} readers   | {} writers'.format(
                self.id,
                self.manager.num_readers.read(),
                self.manager.num_writers.read()
            ))
        # -> this is where reading would happen
        self.delay(random.randint(0, 1))
        ### END CRITICAL SECTION ###

        self.manager.reader_exit()


class Writer(MPthread):
    def __init__(self, manager, num):
        MPthread.__init__(self, manager, num)
        self.manager = manager
        self.id = num


    def run(self):
        self.delay(random.randint(0,1))
        self.manager.writer_enter()

        ### BEGIN CRITICAL SECTION ###
        with self.manager.monitor_lock:
            print('writer {} inside. crit section: {} readers   | {} writers'.format(
                self.id,
                self.manager.num_readers.read(),
                self.manager.num_writers.read()
            ))
        # -> this is where writing would happen
        ### END CRITICAL SECTION ###

        self.manager.writer_exit()


if __name__ == '__main__':

    manager = ReaderWriterManager()
    for i in range(10):
        Reader(manager, i).start()
        Writer(manager, i).start()

    manager.Ready()
