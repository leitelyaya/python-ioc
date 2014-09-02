#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
class ServiceProxy(object):
    def __init__(self, serviceClass, serviceRegistry):
        object.__setattr__(self, u'_serviceClass', serviceClass)
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
            self._instance = self._registry.createAndWireInstance(self._serviceClass)
            
    def __setattr__(self, name, value):
        if name == u'_instance':
            object.__setattr__(self, u'_instance', value)
            return 
        
        self.__setupInstance()
        
        setattr(self._instance, name, value)
