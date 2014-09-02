#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
import unittest
from pythonioc import serviceregistry

class ServiceRegistryTest(unittest.TestCase):
    
    
    __mockserviceInitialized = False   
    
    def setUp(self):
        ServiceRegistryTest.mockserviceInitialized = False
        
        self.serviceRegistry = serviceregistry.ServiceRegistry()
        
    def tearDown(self):
        self.serviceRegistry = None
    
    def testRegisterService(self):
        self.serviceRegistry.registerService(MockService)
        self.assertTrue(self.serviceRegistry.hasService(u"mockService"))
        self.assertFalse(self.serviceRegistry.hasService(u"non-existent"))
        
    def testPostInit(self):
        # register
        self.serviceRegistry.registerService(MockService)
        self.serviceRegistry.registerService(AnotherService)
        
        # get the proxies
        mockService = self.serviceRegistry.getServiceByName(u"mockService")
        anotherService = self.serviceRegistry.getServiceByName(u"anotherService")
        
        # should not be initailzed yet
        self.assertFalse(ServiceRegistryTest.mockserviceInitialized)
        
        # even using the other service does not initialize the mock service
        self.assertEquals(u"hello", anotherService.serviceMethod())
        self.assertFalse(ServiceRegistryTest.mockserviceInitialized)
        
        # now use it
        self.assertEquals(u"hello", mockService.useAnotherService())
        self.assertTrue(ServiceRegistryTest.mockserviceInitialized)

        
    def testInjectOnlyClassVars(self):
        """
        Make sure only class variables are injected.
        MockService therefore initializes an instance variable
        in its init which has the same name as a service.
        """
        self.serviceRegistry.registerService(MockService)
        self.serviceRegistry.registerService(SecondService)
        
        mockService = self.serviceRegistry.getServiceByName(u"mockService")
        self.assertEquals(u"not-wired", mockService._secondService)
        
    def testDestroy(self):

        self.serviceRegistry.registerService(MockService)
        mockService = self.serviceRegistry.getServiceByName(u"mockService")
        
        self.serviceRegistry.destroy()
        self.assertTrue(mockService.destroyed)
        self.assertFalse(self.serviceRegistry.hasService(u"mockService"))
        
    def testRegisterServiceInstance(self):
        self.serviceRegistry.registerService(A)
        
        b = B()
        self.serviceRegistry.registerServiceInstance(b)
        self.assertEquals(u"A", b.getOtherName())
        
                
    def testCycles(self):
        self.serviceRegistry.registerService(B)
        self.serviceRegistry.registerService(A)
        
        a = self.serviceRegistry.getServiceByName(u"a")
        
        self.assertEquals(u"A", a.getName())
        self.assertEquals(u"B", a.getOtherName())
        
    def testPostInitCycles(self):
        self.serviceRegistry.registerService(C)
        self.serviceRegistry.registerService(D)
        
        c = self.serviceRegistry.getServiceByName(u"c")
        
        self.assertRaises(Exception, lambda: c.doSomething())
        
    def testDependencyGraph(self):
        self.serviceRegistry.registerService(A)
        self.serviceRegistry.registerService(B)
        self.serviceRegistry.registerService(MockService)
        self.serviceRegistry.registerService(AnotherService)
        
        a = self.serviceRegistry.getServiceByName(u"a")
        mockService = self.serviceRegistry.getServiceByName(u"mockService")
        
        a.getName()
        mockService.useAnotherService()
        
        
    def testCreateWired(self):
        self.serviceRegistry.createWired(MockService)
        self.serviceRegistry.createWired(MockService)
        self.serviceRegistry.createWired(MockService)
        
class A(object):
    _b = None
    
    def getName(self):
        return u"A"
    
    def getOtherName(self):
        return self._b.getName()
    
class B(object):
    _a = None
    
    def getName(self):
        return u"B"
    
    def getOtherName(self):
        return self._a.getName()
    
class C(object):
    _d = None
    
    def postInit(self):
        self._d.getSomeValue()
    
    def doSomething(self):
        print u"success"

class D(object):
    _c = None
    
    def postInit(self):
        print self._c.doSomething()
    
    def getSomeValue(self):
        return 42
        
class MockService(object):
    
    _anotherService = None
    
    _nonExistentService = None
    
    destroyed = False
    
    def __init__(self):
        self._secondService = u'not-wired'
    
    def useAnotherService(self):
        return self._anotherService.serviceMethod()
    
    def postInit(self):
        ServiceRegistryTest.mockserviceInitialized = True
        
    def preDestroy(self):
        self.destroyed = True
    
class AnotherService(object):
    
    def serviceMethod(self):
        return u"hello"
    
class SecondService(object):
    pass
        