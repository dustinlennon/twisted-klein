from zope.interface import implementer

from twisted.internet import defer
from twisted.application import service

from tk.context_logger import ContextLogger
from tk.interfaces import IUtilityService

#
# UtilityService
#   - our primary service
#
from tk.directory_hash import DirectoryHash
from tk.errors import UnknownFsidError
from tk.pipe_factory import PipeFactory
from tk.self_extractor import SelfExtractor

@implementer(IUtilityService)
class UtilityService(service.Service):
  logger = ContextLogger()

  def __init__(self, fsmap = None):
    self._transient = set()
    self.fsmap      = fsmap

  def map(self, fsid) -> defer.Deferred:
    try:
      dirname = self.fsmap[fsid]

    except TypeError:
      d = defer.succeed(fsid)

    except KeyError as e:
      exc = UnknownFsidError(fsid)
      exc.__cause__ = e
      self.logger.error("UtilityService.map: {e}", e = repr(exc))
      raise exc

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
    d.addCallback(self_extractor.generate)
    d.addBoth(self._cb_object_cleanup, self_extractor)
    return d

  def getUserId(self) -> defer.Deferred:
    d = PipeFactory(["/usr/bin/id"]).run()
    return d

  def _cb_object_cleanup(self, result, obj):
    self._transient.remove(obj)
    return result
