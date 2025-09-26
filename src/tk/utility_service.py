from zope.interface import implementer

from twisted.internet import defer

from twisted.application import service
from tk.context_logger import ContextLogger
from tk.interfaces import IUtilityService

from tk.directory_hash import DirectoryHash
from tk.mapper import (
  BaseMapper,
  KeyMapper,
  RelocatedMixin
)

from tk.pipe_factory import PipeFactory
from tk.self_extractor import SelfExtractor


#
# UtilityService
#
@implementer(IUtilityService)
class UtilityService(service.Service):
  logger = ContextLogger()

  def getDirectoryHashMD5(self, fsid) -> defer.Deferred:
    return DirectoryHash.md5(fsid)
     
  def getDirectoryHashSHA256(self, fsid) -> defer.Deferred:
    return DirectoryHash.sha256(fsid)

  def getSelfExtractor(self, fsid, template_dir = "./templates", template = "install.sh.j2") -> defer.Deferred:
    self_extractor = SelfExtractor(template_dir, template)
    return self_extractor.generate(fsid)

  def getUserId(self) -> defer.Deferred:
    return PipeFactory(["/usr/bin/id"]).run()
  
  def cleanup(self):
    pass

#
# _MappedUtilityService
#
class _MappedUtilityService(BaseMapper, UtilityService):

  def getDirectoryHashMD5(self, fsid) -> defer.Deferred:
    d = self.mapper(fsid)
    d.addCallback(DirectoryHash.md5)
    return d
     
  def getDirectoryHashSHA256(self, fsid) -> defer.Deferred:
    d = self.mapper(fsid)
    d.addCallback(DirectoryHash.sha256)
    return d

  def getSelfExtractor(self, fsid, template_dir = "./templates", template = "install.sh.j2") -> defer.Deferred:
    self_extractor = SelfExtractor(template_dir, template)

    d = self.mapper(fsid)
    d.addCallback(self_extractor.generate)
    return d

#
# KeyedUtilityService
#
@implementer(IUtilityService)
class KeyedUtilityService(KeyMapper, _MappedUtilityService):
  def __init__(self, fsmap):
    super().__init__(fsmap)

#
# KeyedRelocatedUtilityService
#
@implementer(IUtilityService)
class KeyedRelocatedUtilityService(KeyMapper, RelocatedMixin, _MappedUtilityService):
  def __init__(self, fsmap, root):
    self.validate_args(fsmap, root)

  def stopService(self):
    self.cleanup()
    return super().stopService()
