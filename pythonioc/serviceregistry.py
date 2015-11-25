#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
from future.utils import itervalues

import logging
import inspect
import threading

from . import serviceproxy

class ServiceRegistry(object):

    #
    # no-instance-set singleton.
    # We cannot use None because a service's value may be None as well.
    # A service can also be a constant value...
    __NOT_SET = object()

    log = logging.getLogger(name=__name__)

    # constants that are used to mark instances of services of being initialized to avoid
    # double initialization. The __INIT_MEMBER_VALUE is an arbitrary value that we expect when the
    # other member is available.
    __INIT_MEMBERNAME = u'__initialization_done__'
    __INIT_MEMBER_VALUE = 5547534

    def __init__(self, useWiring=True):
        """
        Constructs a new Service Registry

        @param useWiring: if set to False, creating new service instances will not
                          wire their instance variables using introspection.
                          This is set to true when the global registry is used and therefore,
                          all dependencies should be injected using the injection-function.
        """
        # map names to serviceClasses and instances
        # values is (<class>, <instance>)
        self.__registry = {}

        # maps names to proxies that refer
        # to that name. We keep references to
        # (a) reuse proxies and
        # (b) reset proxies for registry reset (only for testing when using the global registry)
        self.__serviceProxies = {}

        self._serviceCreationLock = threading.RLock()

        #
        #
        self._useWiring = useWiring

        self.__dependencyGraph = {}
        self.__initializationStack = []

    def registerService(self, serviceClass, serviceName=None, overwrite=False):
        if not serviceName:
            serviceName = self.__makeServiceName(serviceClass.__name__)
        else:
            serviceName = self.__makeServiceName(serviceName)


        assert (overwrite or
                serviceName not in self.__registry or
                serviceClass == self.__registry[serviceName][0]), (u"Service named %s already registered with different type" % (serviceName,))

        self.__registry[serviceName] = (serviceClass, self.__NOT_SET)

    def registerServiceInstance(self, instance, serviceName=None, overwrite=False):
        if not serviceName:
            serviceName = self.__makeServiceName(instance.__class__.__name__)
        else:
            serviceName = self.__makeServiceName(serviceName)

        assert overwrite or serviceName not in self.__registry, (u"Service named %s already registered" % (serviceName,))
        self.__registry[serviceName] = (None, instance)

        self.injectDependencies(instance)

    def __makeServiceName(self, className):
        """
        Creates name for the service.
        """

        return className[:1].lower() + className[1:]

    def getServiceInstance(self, service):
        if inspect.isclass(service):
            service = self.__makeServiceName(service.__name__)
        else:
            service = self.__makeServiceName(service)

        return self._getServiceInstanceForName(service)

    def _getServiceInstanceForName(self, serviceName):
        if serviceName not in self.__registry:
            raise Exception('Service %s is not registered. Cannot create instance' % serviceName)

        with self._serviceCreationLock:
            (cls, instance) = self.__registry[serviceName]
            if instance is self.__NOT_SET:
                assert cls
                self.__registry[serviceName] = (cls, self.createWired(cls))

        return self.__registry[serviceName][1]
    def _getServiceProxy(self, service):
        """
        Returns the service proxy of a service.
        If a class is given, the name will be extracted.
        """
        if inspect.isclass(service):
            service = self.__makeServiceName(service.__name__)
        else:
            service = self.__makeServiceName(service)

        if service not in self.__serviceProxies:
            self.__serviceProxies[service] = serviceproxy.ServiceProxy(service, self)

        return self.__serviceProxies[service]

    def hasService(self, serviceName):
        """
        Checks whether a service is registered.
        """
        return serviceName in self.__registry

    def clean(self):
        """
        Destroys all service instances. They stay registered though.
        All proxies are cleared as well, so they'd have to get a new instance
        of their service.
        """

        for name in list(self.__registry.keys()):
            (cls, instance) = self.__registry[name]
            if instance and hasattr(instance, u'preDestroy'):
                instance.preDestroy()

            if cls:
                self.__registry[name] = (cls, self.__NOT_SET)
            else:
                # remove the entry completely
                del self.__registry[name]

        # remove all instances from the proxies.
        for proxy in itervalues(self.__serviceProxies):
            proxy._instance = None

        self.__dependencyGraph = {}
        self.__initializationStack = []

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

        # wire only if wished by the user
        if self._useWiring:
            for (name, _) in inspect.getmembers(service.__class__, memberFilter):

                # attributes must start with u'_' but not u'__'
                if name[0] != u'_' or name.startswith(u'__'):
                    continue

                # try to find the service with that name.
                serviceName = name[1:]
                if serviceName in self.__registry:
                    setattr(service, name, serviceproxy.ServiceProxy(serviceName, self))

        # run the postInit independent of the wiring
        if runPostInit:
            self._runServicePostInit(self.__makeServiceName(service.__class__.__name__), service)

    def getDependencyGraph(self):
        return unicode(self.__dependencyGraph)

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

            try:
                service.postInit()

                setattr(service, self.__INIT_MEMBERNAME, self.__INIT_MEMBER_VALUE)
            finally:
                assert len(self.__initializationStack) > 0
                del self.__initializationStack[-1:]
