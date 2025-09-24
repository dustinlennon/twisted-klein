from zope.interface import implementer

from twisted.python import components
from twisted.web import resource

from tk.interfaces import *
from tk.klein_delegator import KleinDelegator
import tk.klein_mixins as mixins
from tk.netcat_request import NetcatRequestFactory

__all__ = []

#
# Adapter from IDirectoryHashService 
#           to IDirectoryHashNetcatRequestFactory
#
@implementer(IDirectoryHashNetcatRequestFactory)
class DirectoryHashFactoryFromUtilityService(NetcatRequestFactory):
  def __init__(self, service):
    self.service = service

  def cmd_md5(self, fsid) -> defer.Deferred:
    return self.service.getDirectoryHashMD5(fsid)

  def cmd_sha256(self, fsid) -> defer.Deferred:
    return self.service.getDirectoryHashSHA256(fsid)

#
# Adapter from ISelfExtractorService 
#           to ISelfExtractorNetcatRequestFactory
#
@implementer(ISelfExtractorNetcatRequestFactory)
class SelfExtractorFromUtilityService(NetcatRequestFactory):
  def __init__(self, service):
    self.service = service

  def cmd_pack(self, fsid) -> defer.Deferred:
    return self.service.getSelfExtractor(fsid)

# Adapter from IUtilityService 
#           to resource.IResource
#
@implementer(resource.IResource)
class ResourceFromUtilityService(
    KleinDelegator,
    mixins.KWelcome,
    mixins.KDirectoryHash,
    mixins.KSelfExtractor
    ):
  
  def __init__(self, service):
    super().__init__(service)


#
# Adapters class
#
class Adapters(object):
  __initialized__ = False

  args = [
    (
      DirectoryHashFactoryFromUtilityService,
      IDirectoryHashService,
      IDirectoryHashNetcatRequestFactory
    ),
    (
      SelfExtractorFromUtilityService,
      ISelfExtractorService,
      ISelfExtractorNetcatRequestFactory
    ),
    (
      ResourceFromUtilityService,
      IUtilityService,
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
