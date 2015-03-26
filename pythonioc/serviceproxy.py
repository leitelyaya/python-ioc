#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
class ServiceProxy(object):
    def __init__(self, serviceName, serviceRegistry):
        object.__setattr__(self, u'_serviceName', serviceName)
        object.__setattr__(self, u'_registry', serviceRegistry)
        object.__setattr__(self, u'_instance', None)
        object.__setattr__(self, u'_initializationDone', False)
        
    def __getattr__(self, name):
        if name == u'_instance':
            return object.__getattr__(self, u'_instance')
        
        self.__setupInstance()
        
        return getattr(self._instance, name)
    
    def __setupInstance(self):
        if not self._instance:
            self._instance = self._registry.getServiceInstance(self._serviceName)
            
    def __setattr__(self, name, value):
        if name == u'_instance':
            object.__setattr__(self, u'_instance', value)
            return
        
        self.__setupInstance()
        
        setattr(self._instance, name, value)

    def __str__(self):
        self.__setupInstance()
        
        return str(self._instance)
    
    def __call__(self, *args, **kwargs):
        self.__setupInstance()
        
        return self._instance(*args, **kwargs)
    
    def __repr__(self):
        self.__setupInstance()
        
        return repr(self._instance)
    
    @property
    def instance(self):
        self.__setupInstance()
        return self._instance

