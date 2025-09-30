from zope.interface import Interface
from twisted.internet import defer

#
# ICleaner
#
class ICleanup(Interface):
  def cleanup(self):
    pass  

#
# ICleanupContext
#
class ICleanupContext(Interface):
  def __enter__(self):
    pass

  def __exit__(self, exc_type, exc_value, tb):
    pass

#
# DirectoryHash
#
class IDirectoryHashAPI(Interface):
  def getDirectoryHashMD5(self, fsid) -> defer.Deferred:
    pass

  def getDirectoryHashSHA256(self, fsid) -> defer.Deferred:
    pass

#
# TarballTemplate
#
class ITarballTemplateAPI(Interface):
  def getTarballTemplate(self, fsid) -> defer.Deferred:
    pass    

#
# UserId
#
class IUserIdAPI(Interface):
  def getUserId(self) -> defer.Deferred:
    pass

#
# Utility
#   - a compilation of existing interfaces
#
class IUtilityService(
    IDirectoryHashAPI,
    ITarballTemplateAPI,
    IUserIdAPI
  ):
  pass

