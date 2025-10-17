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
# CloudConf
#
class ICloudConf(Interface):
  def getMetaData(self, **kw) -> defer.Deferred:
    pass  
  
  def getUserData(self, **kw) -> defer.Deferred:
    pass  

  def getVendorData(self, **kw) -> defer.Deferred:
    pass  

  def getSshKeys(self, userid) -> defer.Deferred:
    pass

  def getReverseLookup(self, ipaddr) -> defer.Deferred:
    pass
