# Simple Inversion-Of-Control-Container for python #

This package contains a simple inversion-of-control container. Every injectable element is registered
to the ServiceRegistry. By convention, the class' name with the first letter uncapitalized is used
(UserService -> userService).

An example below


```python

class Service(object):
    
    # this will make the service registry inject a service named u"someOtherService" which 
    # comes from class SomeOtherService
    _someOtherService = None
    
    def __init__(self):
        pass
        
    # will be called after everything is injected
    def postInit(self):
        pass
        
    # will be called right before the object is destroyed (the registry's destroy
    # method is called)
    def preDestroy(self):
        pass
        
        

class SomeOtherService(object):
    pass
    
# Use it like

reg = ServiceRegistry()
reg.registerService(Service())
reg.registerService(SomeOtherService())

# inject all dependencies
reg.wireServices()

```

