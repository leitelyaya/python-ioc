#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
from __future__ import print_function


import unittest
from pythonioc import serviceregistry
import time
import threading

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
        mockService = self.serviceRegistry._getServiceProxy(u"mockService")
        anotherService = self.serviceRegistry._getServiceProxy(u"anotherService")

        # should not be initailzed yet
        self.assertFalse(ServiceRegistryTest.mockserviceInitialized)

        # even using the other service does not initialize the mock service
        self.assertEquals(u"hello", anotherService.serviceMethod())
        self.assertFalse(ServiceRegistryTest.mockserviceInitialized)

        # now use it
        self.assertEquals(u"hello", mockService.useAnotherService())
        self.assertTrue(ServiceRegistryTest.mockserviceInitialized)

    def test_postInit_concurrentLongrunning(self):
        self.serviceRegistry.registerService(LongRunningPostInitService)

        errors = []
        def getService():
            try:
                self.serviceRegistry.getServiceInstance(LongRunningPostInitService)
            except Exception as e:
                errors.append(e)

        t1 = threading.Thread(target=getService)
        t2 = threading.Thread(target=getService)

        t1.start()
        time.sleep(0.1)
        t2.start()

        for t in [t1, t2]:
            t.join()

        self.assertEquals(1, LongRunningPostInitService.initialized[0])
        self.assertEquals(0, len(errors))


    def testInjectOnlyClassVars(self):
        """
        Make sure only class variables are injected.
        MockService therefore initializes an instance variable
        in its init which has the same name as a service.
        """
        self.serviceRegistry.registerService(MockService)
        self.serviceRegistry.registerService(SecondService)

        mockService = self.serviceRegistry._getServiceProxy(u"mockService")
        self.assertEquals(u"not-wired", mockService._secondService)

    def test_clean(self):

        self.serviceRegistry.registerService(MockService)
        mockService = self.serviceRegistry.getServiceInstance("mockService")

        self.assertFalse(mockService.destroyed)
        self.serviceRegistry.clean()
        self.assertTrue(mockService.destroyed)

        # it still has the service, but there is no instance yet
        self.assertTrue(self.serviceRegistry.hasService(u"mockService"))

        # requesting the service a second time will create a new instance
        mockService2 = self.serviceRegistry.getServiceInstance(u"mockService")
        self.assertNotEquals(mockService, mockService2)

    def test_clean_proxybuffer(self):
        self.serviceRegistry.registerService(MockService)
        serviceProxy = self.serviceRegistry._getServiceProxy("mockService")
        realService = self.serviceRegistry.getServiceInstance(u"mockService")
        self.assertFalse(serviceProxy.destroyed)
        self.assertFalse(realService.destroyed)

        self.assertEquals(serviceProxy._instance, realService)

        self.serviceRegistry.clean()

        self.assertTrue(serviceProxy._instance is None)
        self.assertTrue(realService.destroyed)


        # get the service proxy again

        serviceProxy2 = self.serviceRegistry._getServiceProxy("mockService")
        realService2 = self.serviceRegistry.getServiceInstance(u"mockService")
        self.assertFalse(serviceProxy2.destroyed)
        self.assertFalse(realService2.destroyed)

        self.assertEquals(serviceProxy, serviceProxy2)
        self.assertNotEquals(serviceProxy2._instance, realService)
        self.assertEquals(serviceProxy2._instance, realService2)

    def testRegisterServiceInstance(self):
        self.serviceRegistry.registerService(A)

        b = B()
        self.serviceRegistry.registerServiceInstance(b)
        self.assertEquals(u"A", b.getOtherName())


    def testCycles(self):
        self.serviceRegistry.registerService(B)
        self.serviceRegistry.registerService(A)

        a = self.serviceRegistry._getServiceProxy(u"a")

        self.assertEquals(u"A", a.getName())
        self.assertEquals(u"B", a.getOtherName())

    def testPostInitCycles(self):
        self.serviceRegistry.registerService(C)
        self.serviceRegistry.registerService(D)

        c = self.serviceRegistry._getServiceProxy(u"c")

        self.assertRaises(Exception, lambda: c.doSomething())

    def testDependencyGraph(self):
        self.serviceRegistry.registerService(A)
        self.serviceRegistry.registerService(B)
        self.serviceRegistry.registerService(MockService)
        self.serviceRegistry.registerService(AnotherService)

        a = self.serviceRegistry._getServiceProxy(u"a")
        mockService = self.serviceRegistry._getServiceProxy(u"mockService")

        a.getName()
        mockService.useAnotherService()


    def testCreateWired(self):
        """
        @TODO: what's that test supposed to do?
        """
        self.serviceRegistry.createWired(MockService)
        self.serviceRegistry.createWired(MockService)
        self.serviceRegistry.createWired(MockService)

    def test_registerServiceInstanceOverwrite(self):

        old = 0
        self.serviceRegistry.registerServiceInstance(old, 'value')
        self.assertEquals('0', str(self.serviceRegistry._getServiceInstanceForName('value')))

        new = 1
        self.assertRaises(AssertionError, self.serviceRegistry.registerServiceInstance, new, 'value')
        self.serviceRegistry.registerServiceInstance(new, 'value', overwrite=True)
        self.assertEquals('1', str(self.serviceRegistry._getServiceInstanceForName('value')))

    @unittest.skip("None is actually allowed")
    def test_registerServiceInstance_rejectNone(self):
        self.assertRaises(AssertionError, self.serviceRegistry.registerServiceInstance, None, "somename")


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
        print(u"success")

class D(object):
    _c = None

    def postInit(self):
        print(self._c.doSomething())

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



class LongRunningPostInitService(object):
    initialized = [0]

    def postInit(self):
        time.sleep(0.4)
        self.initialized[0] += 1
