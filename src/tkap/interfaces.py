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
# Environment
#
class IEnvironment(Interface):
  def getEnvId(self) -> defer.Deferred:
    pass

  def getEnvPwd(self) -> defer.Deferred:
    pass

#
# SshKeys
#
class ISshKeys(Interface):
  def getSshKeys(self, userid) -> defer.Deferred:
    pass