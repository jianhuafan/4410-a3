
# (C) CS 4410 Fall 2018 Staff, Cornell University
# All rights reserved

from rvr_sync_wrapper import MP, MPthread
import random
import signal

signal.signal(signal.SIGINT, signal.SIG_DFL)

# This program simulates the creation of Oreos.

# Implement the OreoFactory monitor below using MPlocks and
# MPcondition variables.

################################################################################
## DO NOT WRITE OR MODIFY ANY CODE ABOVE THIS LINE #############################
################################################################################

class OreoFactory(MP):
    """ An Oreo is made from 2 cookies and a layer of icing (each piece of
        cookie and layer of icing can be used in only one oreo).

    A thread offers a piece of ingredient by calling the appropriate method;
    the thread will block until the ingredient can be used in the making of an
    Oreo.
    """

    def __init__(self):
        """ Initializes an instance of OreoFactory. Shared resources and locks
            get created in here.

        """
        MP.__init__(self)
        # TODO implement me
        self.cookie_count = self.Shared("number of cookie arrived", 0)
        self.icing_count = self.Shared("number of icing arrived", 0)
        self.cookie_guard = self.Shared("guard variable for cookie", 0)
        self.icing_guard = self.Shared("guard variable for icing", 0)

        self.lock = self.Lock("basic lock")
        self.cookie_cv = self.lock.Condition("cookie must wait")
        self.icing_cv = self.lock.Condition("icing must wait")


    def icing_arrived(self):
        """ A unit of icing has arrived at the factory.

        Block until it can be used to create an oreo. Exiting this function is
        equivalent to using the unit of icing in an oreo.
        """
        # TODO implement me
        with self.lock:
            self.icing_count.inc()
            if self.cookie_count.read() > 1:
                self.icing_count.dec()
                self.cookie_count.dec()
                self.cookie_count.dec()
                self.icing_guard.inc()
                self.cookie_guard.inc()
                self.cookie_guard.inc()
                self.cookie_cv.signal()
                self.cookie_cv.signal()
            else:
                while self.icing_guard.read() == 0:
                    self.icing_cv.wait()
            self.icing_guard.dec()


    def cookie_arrived(self):
        """ A unit of cookie has arrived at the factory.

        Block until it can be used to create an oreo. Exiting this function is
        equivalent to using the unit of cookie in an oreo.
        """
        # TODO implement me
        with self.lock:
            self.cookie_count.inc()
            if self.cookie_count.read() > 1 and self.icing_count.read() > 0:
                self.icing_count.dec()
                self.cookie_count.dec()
                self.cookie_count.dec()
                self.icing_guard.inc()
                self.cookie_guard.inc()
                self.cookie_guard.inc()
                self.icing_cv.signal()
                self.cookie_cv.signal()
            else:
                while self.cookie_guard.read() == 0:
                    self.cookie_cv.wait()
            self.cookie_guard.dec()


################################################################################
## DO NOT WRITE OR MODIFY ANY CODE BELOW THIS LINE #############################
################################################################################

class Icing(MPthread):
    def __init__(self, factory, id):
        MPthread.__init__(self, factory, id)
        self.factory = factory
        self.id = id


    def run(self):
        while True:
            print('icing {} arrived'.format(self.id))
            self.factory.icing_arrived()
            print('icing {} has been used'.format(self.id))
            self.delay(random.uniform(0, 0.25))


class Cookie(MPthread):
    def __init__(self, factory, id):
        MPthread.__init__(self, factory, id)
        self.factory = factory
        self.id = id


    def run(self):
        while True:
            print('cookie {} arrived'.format(self.id))
            self.factory.cookie_arrived()
            print('cookie {} has been used'.format(self.id))
            self.delay(random.uniform(0, 0.5))


if __name__ == '__main__':

    NUM_ICING = 4
    NUM_COOKIE = 8

    factory = OreoFactory()
    for i in range(NUM_ICING):
        Icing(factory, i).start()
    for j in range(NUM_COOKIE):
        Cookie(factory, j).start()

    factory.Ready()
