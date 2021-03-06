
# (C) CS 4410 Fall 2018 Staff, Cornell University
# All rights reserved

from rvr_sync_wrapper import MP, MPthread
import random
import signal

signal.signal(signal.SIGINT, signal.SIG_DFL)

#   Complete the implementation of the BusStoplight below using MP Semaphores.
#   Your implementation should be able to make progress if there are any
#   students wishing to board or depart.

################################################################################
## DO NOT WRITE OR MODIFY ANY CODE ABOVE THIS LINE #############################
################################################################################

class BusStoplight(MP):
    """ Sometimes the TCAT gets very crowded when it's bad weather.

    But often, students that are boarding crash into students that are departing,
    and everyone gets to class late. It is your job to implement the BusStoplight
    at the only door of the bus to fix this problem.

    The BusStoplight allows multiple students to cross at once, but at any
    point in time, all students crossing must be going in the same direction.
    Directions can either be boarding (0) or departing (1).

    Students wishing to cross will call the cross function. Once they have
    crossed, they will call the finished function.
    """

    def __init__(self):
        """ Initializes an instance of BusStoplight. Shared resources and locks
            get created in here.

        """
        MP.__init__(self)
        # TODO implement me

        # similar to multiple read and multiple writer problem
        self.boarding_count = self.Shared("number of student that is boarding", 0)
        self.departing_count = self.Shared("number of student that is departing", 0)
        self.board_lock = self.Semaphore("lock for board the bus", 1)
        self.depart_lock = self.Semaphore("lock for departing the bus", 1)


    def cross(self, direction):
        """ Wait for permission to cross the BusStoplight.

        :arg direction: is either 0 for boarding or 1 for departing
        """
        # TODO implement me
        if direction == 0:
            self.board_lock.procure()
            self.boarding_count.inc()
            # the first boarding student require the departing lock
            if self.boarding_count.read() == 1:
                self.depart_lock.procure()
            self.board_lock.vacate()
        else:
            self.depart_lock.procure()
            self.departing_count.inc()
            # the first departing student require the board lock
            if self.departing_count.read() == 1:
                self.board_lock.procure()
            self.depart_lock.vacate()




    def finished(self, direction):
        """ Finish crossing the BusStoplight.

        :arg direction: is either 0 for boarding or 1 for departing
        """
        # TODO implement me
        if direction == 0:
            self.board_lock.procure()
            self.boarding_count.dec()
            if self.boarding_count.read() == 0:
                self.depart_lock.vacate()
            self.board_lock.vacate()
        else:
            self.depart_lock.procure()
            self.departing_count.dec()
            if self.departing_count.read() == 0:
                self.board_lock.vacate()
            self.depart_lock.vacate()



################################################################################
## DO NOT WRITE OR MODIFY ANY CODE BELOW THIS LINE #############################
################################################################################

class Student(MPthread):
    def __init__(self, bus, student_id):
        MPthread.__init__(self, bus, student_id)
        self.direction   = random.randrange(2)
        self.wait_time   = random.uniform(0.1,0.5)
        self.bus         = bus
        self.student_id  = student_id


    def run(self):
        # walk to the bus door
        self.delay(self.wait_time)
        if self.direction == 0:
            print('student {} trying to board'.format(self.student_id))
        else:
            print('student {} trying to depart'.format(self.student_id))

        # request permission to cross
        self.bus.cross(self.direction)

        # walk across
        self.delay(0.01)
        print('student {} crossed'.format(self.student_id))

        # signal that we have finished crossing
        self.bus.finished(self.direction)
        print('student {} finished crossing'.format(self.student_id))


if __name__ == "__main__":

    boarding = 0
    departing = 1

    tcat = BusStoplight()
    for i in range(100):
        Student(tcat, i).start()
