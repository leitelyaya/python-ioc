import unittest
import pythonioc
import time


class NowUser(object):
    timeInst = pythonioc.Inject('now')
    
class LibraryService(object):
    value = 42
    
class TestPythonioc(unittest.TestCase):
    """
    Tests module functions.
    """
    
    def test_registerService(self):
        pythonioc.registerService(LibraryService)
        
        d = pythonioc.getService('LibraryService')
        self.assertEquals(42, d.value)
    
    def test_registerServiceInstance(self):
        now = time.time()
        pythonioc.registerServiceInstance(now, 'now')
        
        nu = NowUser()
        
        self.assertEquals(str(now), str(nu.timeInst))
        
