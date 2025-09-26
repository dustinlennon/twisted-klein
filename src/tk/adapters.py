from zope.interface import implementer

from twisted.internet import interfaces
from twisted.python import components
from twisted.web import resource

from tk.interfaces import *
from tk.klein_delegator import KleinDelegator
import tk.klein_mixins as mixins
from tk.netcat_request import NetcatRequestFactory

__all__ = []

#
# Adapter from IDirectoryHashAPI
#           to IProtocolFactory
#
@implementer(interfaces.IProtocolFactory)
class NetcatFactoryFromDirectoryHash(NetcatRequestFactory):
  def __init__(self, api : IDirectoryHashAPI):
    self.api = api

  def cmd_md5(self, fsid) -> defer.Deferred:
    return self.api.getDirectoryHashMD5(fsid)

  def cmd_sha256(self, fsid) -> defer.Deferred:
    return self.api.getDirectoryHashSHA256(fsid)
  
#
# Adapter from ISelfExtractorAPI
#           to IProtocolFactory
#
@implementer(interfaces.IProtocolFactory)
class NetcatFactoryFromSelfExtractor(NetcatRequestFactory):
  def __init__(self, api : ISelfExtractorAPI):
    self.api = api

  def cmd_pack(self, fsid) -> defer.Deferred:
    return self.api.getSelfExtractor(fsid)

#
# Adapter from IUtilityService 
#           to resource.IResource
#
@implementer(resource.IResource)
class ResourceFromUtilityService(
    KleinDelegator,
    mixins.KWelcome,
    mixins.KDirectoryHash,
    mixins.KSelfExtractor,
    mixins.KUserId
    ):
  
  def __init__(self, obj : IUtilityService):
    super().__init__(obj)

#
# Adapter from ICleanup 
#           to ICleanupContext
#
@implementer(ICleanupContext)
class CleanupContextFromCleaner(object):
  def __init__(self, cleaner : ICleanup):
    self.cleaner = cleaner

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_value, tb):
    self.cleaner.cleanup()

  
#
# Adapters class
#
class Adapters(object):
  __initialized__ = False

  args = [
    (
      NetcatFactoryFromDirectoryHash,
      IDirectoryHashAPI,
      interfaces.IProtocolFactory
    ),
    (
      NetcatFactoryFromSelfExtractor,
      ISelfExtractorAPI,
      interfaces.IProtocolFactory
    ),
    (
      ResourceFromUtilityService,
      IUtilityService,
      resource.IResource
    ),
    (
      CleanupContextFromCleaner,
      ICleanup,
      ICleanupContext
    )
  ]

  @classmethod
  def registerAll(cls):
    if cls.__initialized__ == False:
      for args in cls.args:
        components.registerAdapter(*args)
    cls.__initialized__ = True

Adapters.registerAll()
