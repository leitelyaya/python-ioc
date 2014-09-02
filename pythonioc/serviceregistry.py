#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
import logging
import inspect
import serviceproxy


class ServiceRegistry(object):
    
    
    log = logging.getLogger(name=__name__)

    # constants that are used to mark instances of services of being initialized to avoid
    # double initialization. The __INIT_MEMBER_VALUE is an arbitrary value that we expect when the
    # other member is available.    
    __INIT_MEMBERNAME = u'__initialization_done__'
    __INIT_MEMBER_VALUE = 5547534
    
    
    def __init__(self):
        
        # map names to services
        self.__registry = {}
        
        # since we use lazy initialization,
        # we cannot allow to register service classes once an instance
        # has been registered. Otherwise we're likely to miss dependencies
        self._instancesAdded = False
        
        
        self.__dependencyGraph = {} 
        self.__initializationStack = []
                        
    def registerService(self, serviceClass):
        serviceName = self.__makeServiceName(serviceClass.__name__)
        
        if self._instancesAdded:
            self.log.warn("""registering service %s after an instance has been added. 
                            The instance might miss some dependencies""" % serviceName)
        assert serviceName not in self.__registry, (u"Service named %s already registered" % (serviceName,))
        
        self.__registry[serviceName] = serviceproxy.ServiceProxy(serviceClass, self)
        
    def registerServiceInstance(self, instance):
        serviceName = self.__makeServiceName(instance.__class__.__name__)
        assert serviceName not in self.__registry, (u"Service named %s already registered" % (serviceName,))
        self.__registry[serviceName] = instance
        
        self.injectDependencies(instance)

        self._instancesAdded = True
        
    def __makeServiceName(self, className):
        """
        Creates name for the service.
        """
        
        return className[:1].lower() + className[1:]
        
    def getServiceByName(self, serviceName):
        """
        This is only a method for testing. Don't use in production, it's going to 
        return the ServiceProxy object, not the real service!
        """
        
        assert serviceName in self.__registry, (u"No Service %s registered" % serviceName)
        
        return self.__registry[serviceName]
    
    def hasService(self, serviceName):
        """
        Checks whether a service is registered.
        """
        return serviceName in self.__registry
               
    def destroy(self):
        """
        Destroys all services.
        """
        
        for service in self.__registry.itervalues():
            if hasattr(service, u'preDestroy'):
                service.preDestroy()
                
        self.__registry = {}
        
    def createWired(self, itemClass, *args, **kwargs):
        """
        Create an item, automatically injecting all
        dependencies.
        """
        instance = itemClass(*args, **kwargs)
        self.injectDependencies(instance)
        return instance
            
    def injectDependencies(self, service, runPostInit=True):
        
        if(hasattr(service, self.__INIT_MEMBERNAME) and 
           getattr(service, self.__INIT_MEMBERNAME) == self.__INIT_MEMBER_VALUE):
            # already initialized and postinit has run
            # TODO we may have to fix that.
            return
        
        def memberFilter(obj):
            u" filter for inspect.getmembers to return only None class variables "
            return obj is None and not inspect.ismethod(obj)
        
        for (name, _) in inspect.getmembers(service.__class__, memberFilter):
                        
            # attributes must start with u'_' but not u'__'
            if name[0] != u'_' or name.startswith(u'__'):
                continue
            
            # try to find the service with that name.
            serviceName = name[1:]
            if serviceName in self.__registry:
                setattr(service, name, self.__registry[serviceName])
        if runPostInit:
            self._runServicePostInit(self.__makeServiceName(service.__class__.__name__), service)
            
    def getDependencyGraph(self):
        return unicode(self.__dependencyGraph)
    
    def createAndWireInstance(self, serviceClass):
        instance = serviceClass()
        self.injectDependencies(instance)
        
        return instance
            
    def _runServicePostInit(self, serviceName, service):
        if hasattr(service, u'postInit'):
            if hasattr(service, self.__INIT_MEMBERNAME):
                # if the member is there, it must have our value
                # Otherwise it came from somewhere else which can cause serious issues
                assert getattr(service, self.__INIT_MEMBERNAME) == self.__INIT_MEMBER_VALUE, u"duplicate initialization variable."
                raise AssertionError(u"double initialization (postInit in %s %s). Not good!" % (unicode(service), unicode(type(service))))
            # if I am already initializing, there is a cycle!
            if serviceName in self.__initializationStack:
                raise Exception(u"***Dependency cycle detected***\n\t" + u'\n\t->'.join(self.__initializationStack + [serviceName]))
                
            
            # get top of stack
            currentInitService = self.__initializationStack[-1:]
            
            if len(currentInitService) == 0:
                self.__initializationStack.append(serviceName)
                
                if serviceName not in self.__dependencyGraph:
                    self.__dependencyGraph[serviceName] = set()
            else:
                self.__dependencyGraph[currentInitService[0]].add(serviceName)
                
                if serviceName not in self.__dependencyGraph:
                    self.__dependencyGraph[serviceName] = set()
                
                self.__initializationStack.append(serviceName)
            
            service.postInit()
            setattr(service, self.__INIT_MEMBERNAME, self.__INIT_MEMBER_VALUE)
            
            assert len(self.__initializationStack) > 0
            del self.__initializationStack[-1:]
            
