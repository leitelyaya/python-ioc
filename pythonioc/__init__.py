

from serviceregistry import ServiceRegistry
from pythonioc import serviceproxy
import inspect

__version__ = "0.2.1"

#
# global instance, if the Service-Decorator is used for classes and instances.
#
__globalServiceRegistry = None

def __serviceMetaClass(cls):
    pass

def __getGlobalServiceRegistry():
    global __globalServiceRegistry
    if not __globalServiceRegistry:
        __globalServiceRegistry = ServiceRegistry()
    return __globalServiceRegistry

def Service(cls):
    __getGlobalServiceRegistry().registerService(cls)
    # inspect.
    return cls

def Inject(service):
    return __getGlobalServiceRegistry()._getServiceProxy(service)

def getService(service):
    return __getGlobalServiceRegistry()._getServiceInstance(service)
