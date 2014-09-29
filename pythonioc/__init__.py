

from serviceregistry import ServiceRegistry
from pythonioc import serviceproxy
import inspect

__version__ = "0.3.0"

#
# global instance, if the Service-Decorator is used for classes and instances.
#
__globalServiceRegistry = None

def __getGlobalServiceRegistry():
    global __globalServiceRegistry
    if not __globalServiceRegistry:
        __globalServiceRegistry = ServiceRegistry(useWiring=False)
    return __globalServiceRegistry


def NamedService(name):
    """
    Use this decorator on classes specifying a custom name for their service.
    """
    def Service(cls):
        __getGlobalServiceRegistry().registerService(cls, serviceName=name)
        
        return cls 
    
    return Service
def Service(cls):
    """
    Use this decorator to register classes to the global Service Registry.
    """
    __getGlobalServiceRegistry().registerService(cls)
    # TODO: inspect to check whether the class has a non-default constructor
    return cls

def Inject(service):
    """
    Use this function to create auto-injecting instance properties.
    
    Class MyClass(object):
        # inject by name
        service = pythonioc.Inject('SomeService')
        
        # inject by class
        service2 = pythonioc.Inject(SomeServiceClass)
        
    An instance of "SomeService" will be injected (and created) when used. 
    """
    return __getGlobalServiceRegistry()._getServiceProxy(service)


def registerService(serviceClass, serviceName=None, overwrite=False):
    __getGlobalServiceRegistry().registerService(serviceClass, serviceName, overwrite)
    
def registerServiceInstance(instance, serviceName=None, overwrite=False):
    __getGlobalServiceRegistry().registerServiceInstance(instance, serviceName, overwrite)

def getService(service):
    """
    Get a service (create or return existing) by class or name using the global service registry.
    """
    return __getGlobalServiceRegistry().getServiceInstance(service)

def cleanServiceRegistry():
    """
    Removes all service instances from the global registry. Mainly for testing to start with a clean registry.
    """
    __getGlobalServiceRegistry().clean()
