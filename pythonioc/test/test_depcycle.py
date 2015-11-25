import unittest
import pythonioc

class SpecificException(Exception):
    pass

class ErrorInitService(object):

    def postInit(self):
        raise SpecificException("not working")

    def doSomething(self):
        pass

class TestDepCycle(unittest.TestCase):
    """
    Regression test for issue #3 dependency cycle on error.
    """

    def test_depcycle(self):
        # register a service that will fail on initialization
        pythonioc.registerService(ErrorInitService, overwrite=True)

        # repeatedly try to use it, accept its specific exception but
        # fail on the cycle-exception (which is a normal Exception and not catched)
        for _ in range(10):
            try:
                pythonioc.Inject('errorInitService').doSomething()
            except SpecificException:
                pass

