# Simple Inversion-Of-Control-Container for python #

This package contains a simple inversion-of-control container. Every injectable element is registered
to the ServiceRegistry. By convention, the class' name with the first letter uncapitalized is used
(UserService -> userService).

## Features ##

* lazy initialization of services (if not registered as object)
* dependency cycle detection

An example:


```python

class Service(object):
    
    # this will make the service registry inject a service named "someOtherService" which 
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
reg.registerService(Service)
reg.registerService(SomeOtherService)

```

Once the system has all required services registered, a service can be injected by doing

```python

class WiredUser(object):

    _service=None
    
    def __init__(self, *args):
        pass
        
wiredUser = reg.createWired(WiredUser, 'arg1', 'arg2')


```

Wired objects are not automatically part of the service registry, only if added by calling `reg.registerServiceInstance`.
They can also wire new objects on the fly:

```python

class WiredUser(object):
    _service=None
    
    ...

class UserCreator(object):
    _serviceRegistry=None
    
    def createUser(self):
        return self._serviceRegistry.createWired(WiredUser) 
    
userCreator = reg.createWired(UserCreator)

# create some wired users
userA = userCreator.createUser()
userB = userCreator.createUser()
```