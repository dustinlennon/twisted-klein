from zope.interface import implementer

from twisted.internet import interfaces
from twisted.python import components
from twisted.web import resource

from tkap.interfaces import *
from tkap.cloudconf.cloudconf_routes import CloudconfRoutes
from tkap.cloudconf.cloudconf_factory_methods import CloudconfFactoryMethods
from tkap.cloudconf.interfaces import ICloudconfService
from tkap.klein_resource_mixin import KleinResourceMixin
from tkap.netcat_request import NetcatServerFactory

__all__ = []

@implementer(interfaces.IProtocolFactory)
class ProtocolFactoryFromCloudconfService(CloudconfFactoryMethods, NetcatServerFactory):
  pass

@implementer(resource.IResource)
class ResourceFromCloudconfService(CloudconfRoutes, KleinResourceMixin):
  pass

#
# Adapters class
#
class Adapters(object):
  __initialized__ = False

  args = [
    (
      ProtocolFactoryFromCloudconfService,
      ICloudconfService,
      interfaces.IProtocolFactory
    ),
    (
      ResourceFromCloudconfService,
      ICloudconfService,
      resource.IResource
    )
  ]

  @classmethod
  def registerAll(cls):
    if cls.__initialized__ == False:
      for args in cls.args:
        components.registerAdapter(*args)
    cls.__initialized__ = True

Adapters.registerAll()
