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
        
    def test_registerServiceInstanceOverwrite(self):
        
        old = 0
        pythonioc.registerServiceInstance(old, 'value')
        self.assertEquals('0', str(pythonioc.getService('value')))

        new = 1
        self.assertRaises(AssertionError, pythonioc.registerServiceInstance, new, 'value')
        pythonioc.registerServiceInstance(new, 'value', overwrite=True)
        self.assertEquals('1', str(pythonioc.getService('value')))
        