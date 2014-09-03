#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
import unittest
from pythonioc import serviceregistry
from pythonioc import serviceproxy

class TestServiceProxy(unittest.TestCase):
    
    
    def testProxy(self):
        reg = serviceregistry.ServiceRegistry()
        reg.registerService(A)
        proxy = reg._getServiceProxy('A')
        
        self.assertEquals(42, proxy.someService())
        
class A(object):
    def __init__(self):
        self.init = False
        
    def postInit(self):
        self.init = True
    
    def someService(self):
        assert self.init == True
        return 42