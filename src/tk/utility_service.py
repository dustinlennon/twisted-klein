from zope.interface import implementer

from twisted.internet import defer
from twisted.application import service

from tk.callbacks import eb_crash
from tk.interfaces import IUtilityService

#
# UtilityService
#   - our primary service
#
from tk.directory_hash import DirectoryHash
from tk.self_extractor import SelfExtractor

@implementer(IUtilityService)
class UtilityService(service.Service):
  def __init__(self, fsmap = None):
    self._transient = set()
    self.fsmap      = fsmap

  def map(self, fsid) -> defer.Deferred:
    try:
      dirname = self.fsmap[fsid]

    except TypeError:
      d = defer.succeed(fsid)

    except KeyError as e:
      d = defer.fail(e)

    else:
      d = defer.succeed(dirname)

    return d

  def getDirectoryHashMD5(self, fsid) -> defer.Deferred:
    d = self.map(fsid)
    d.addCallback(DirectoryHash.md5)
    return d
     
  def getDirectoryHashSHA256(self, fsid) -> defer.Deferred:
    d = self.map(fsid)
    d.addCallback(DirectoryHash.sha256)
    return d

  def getSelfExtractor(self, fsid, template_dir = "./templates", template = "install.sh.j2") -> defer.Deferred:
    self_extractor = SelfExtractor(template_dir, template)
    self._transient.add(self_extractor)

    d = self.map(fsid)
    d.addCallbacks(self_extractor.generate, eb_crash)
    d.addCallbacks(self._cb_object_cleanup, eb_crash, (self_extractor,))
    return d

  def _cb_object_cleanup(self, result, obj):
    self._transient.remove(obj)
    return result
