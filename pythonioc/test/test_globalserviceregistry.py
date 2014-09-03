#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
import unittest
import pythonioc


@pythonioc.Service
class SomeService(object):
    
    def getValue(self):
        return 42


class AnotherService(object):
    
    someService = pythonioc.Inject(SomeService)
    
    def useService(self):
        return self.someService.getValue() + 1
    
@pythonioc.Service
class CycleA(object):
    # we cannot use the class here... this wouldn't compile
    b = pythonioc.Inject('CycleB')
    
    def getValue(self):
        return 'a'
    
    def otherValue(self):
        return self.b.getValue()
    
@pythonioc.Service
class CycleB(object):
    a = pythonioc.Inject('CycleA')
    
    def getValue(self):
        return 'b'
    
    def otherValue(self):
        return self.a.getValue()

class TestGlobalServiceRegistry(unittest.TestCase):
    def test_serviceDependency(self):
        service = AnotherService()
        self.assertEquals(43, service.useService())
        
    def test_dependencyCycle(self):
        a = pythonioc.getService(CycleA)
        b = pythonioc.getService('CycleB')
        self.assertEquals('a', a.getValue())

        self.assertEquals('a', b.otherValue())
        self.assertEquals('b', a.otherValue())
        
        self.assertEquals(a, b.a._instance)
        self.assertEquals(b, a.b._instance)
        
    def test_cleanServiceRegistry(self):
        a = pythonioc.getService(CycleA)
        pythonioc.cleanServiceRegistry()
        b = pythonioc.getService(CycleA)
        
        self.assertNotEquals(a, b)
