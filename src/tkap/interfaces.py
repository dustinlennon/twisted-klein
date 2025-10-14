from zope.interface import Interface
from twisted.internet import defer

#
# DirectoryHash
#
class IDirectoryHash(Interface):
  def getDirectoryHashMd5(self, fsid) -> defer.Deferred:
    pass

  def getDirectoryHashSha256(self, fsid) -> defer.Deferred:
    pass

#
# TarballTemplate
#
class ITarballTemplate(Interface):
  def getTarballTemplate(self, fsid) -> defer.Deferred:
    pass    

#
# UserId
#
class IUserId(Interface):
  def getUserId(self) -> defer.Deferred:
    pass

