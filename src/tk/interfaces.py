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
# UserId
#
class IUserIdService(Interface):
  def getUserId(self) -> defer.Deferred:
    pass

#
# Utility
#   - a compilation of existing interfaces
#
class IUtilityService(
    IDirectoryHashService,
    ISelfExtractorService,
    IUserIdService,
    ICleanup
  ):
  pass

