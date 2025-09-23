from zope.interface import Interface
from twisted.internet import defer

#
# DirectoryHash
#
class IDirectoryHashNetcatRequestFactory(Interface):
  def cmd_md5(self, dirname) -> defer.Deferred:
      """
      syntax: md5 dirname
      """

  def cmd_sha256(self, dirname) -> defer.Deferred:
      """
      syntax: sha256 dirname
      """

class IDirectoryHashService(Interface):
  def getDirectoryHashMD5(self, dirpath) -> defer.Deferred:
    pass

  def getDirectoryHashSHA256(self, dirpath) -> defer.Deferred:
    pass

#
# SelfExtractor
#
class ISelfExtractorNetcatRequestFactory(Interface):
  def cmd_pack(self, dirname) -> defer.Deferred:
    """
    syntax: pack dirname
    """

class ISelfExtractorService(Interface):
  def getSelfExtractor(self, dirpath) -> defer.Deferred:
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
