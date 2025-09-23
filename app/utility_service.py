from zope.interface import implementer

from twisted.internet import defer
from twisted.application import service

from iso.callbacks import eb_crash
from iso.interfaces import IUtilityService

#
# UtilityService
#   - our primary service
#
from iso.directory_hash import DirectoryHash
from iso.self_extractor import SelfExtractor

@implementer(IUtilityService)
class UtilityService(service.Service):
  def __init__(self):
    self._transient = set()

  def getDirectoryHashMD5(self, dirpath) -> defer.Deferred:
    return DirectoryHash.md5(dirpath)

  def getDirectoryHashSHA256(self, dirpath) -> defer.Deferred:
    return DirectoryHash.sha256(dirpath)

  def getSelfExtractor(self, dirpath) -> defer.Deferred:
    self_extractor = SelfExtractor("./templates", "install.sh.j2")
    self._transient.add(self_extractor)

    d = self_extractor.generate(dirpath)
    d.addCallbacks(self._cb_object_cleanup, eb_crash, (self_extractor,))
    return d

  def _cb_object_cleanup(self, result, obj):
    self._transient.remove(obj)
    return result
