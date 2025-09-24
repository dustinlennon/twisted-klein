from zope.interface import Interface
from twisted.internet import defer

#
# DirectoryHash
#
class IDirectoryHashNetcatRequestFactory(Interface):
  def cmd_md5(self, fsid) -> defer.Deferred:
      """
      syntax: md5 fsid
      """

  def cmd_sha256(self, fsid) -> defer.Deferred:
      """
      syntax: sha256 fsid
      """

class IDirectoryHashService(Interface):
  def getDirectoryHashMD5(self, fsid) -> defer.Deferred:
    pass

  def getDirectoryHashSHA256(self, fsid) -> defer.Deferred:
    pass

#
# SelfExtractor
#
class ISelfExtractorNetcatRequestFactory(Interface):
  def cmd_pack(self, fsid) -> defer.Deferred:
    """
    syntax: pack fsid
    """

class ISelfExtractorService(Interface):
  def getSelfExtractor(self, fsid) -> defer.Deferred:
    pass    


#
# UtilityService
#   - a compilation of existing interfaces
#
class IUtilityService(
    IDirectoryHashService,
    ISelfExtractorService
  ):
  pass
