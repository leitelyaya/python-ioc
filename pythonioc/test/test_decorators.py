#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
import unittest
import pythonioc


@pythonioc.Service
class ServiceClass(object):
    def getName(self):
        return self.__class__.__name__
    
@pythonioc.NamedService('MyService')
class AnotherServiceClass(object):
    
    def getName(self):
        return self.__class__.__name__
    
class TestDecorators(unittest.TestCase):
    
    def test_Service(self):
        c = pythonioc.getService('ServiceClass')
        self.assertEquals('ServiceClass', c.getName())
        
        d = pythonioc.getService(ServiceClass)
        self.assertEquals('ServiceClass', d.getName())
        
    def test_NamedService(self):
        c = pythonioc.getService('MyService')
        self.assertEquals('AnotherServiceClass', c.getName())
        
        self.assertRaises(Exception, pythonioc.getService, AnotherServiceClass)


    def test_ServiceAnnotationWithCustomConstructor(self):
        """
        Registering a service with a non-default-constructor should fail.
        """
        pass