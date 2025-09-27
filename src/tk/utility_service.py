from importlib import resources
import jinja2

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

  def __init__(self):
    super().__init__()
    self.template = self.preload_template()

  def preload_template(self):
    # necessary because we drop privilege later, losing read access
    env = jinja2.Environment(
      loader = jinja2.PackageLoader("tk", "resources/templates")
    )
    return env.get_template("install.sh.j2")

  def getDirectoryHashMD5(self, fsid) -> defer.Deferred:
    return DirectoryHash.md5(fsid)
     
  def getDirectoryHashSHA256(self, fsid) -> defer.Deferred:
    return DirectoryHash.sha256(fsid)

  def getSelfExtractor(self, fsid) -> defer.Deferred:
    return SelfExtractor(self.template).generate(fsid)

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

  def getSelfExtractor(self, fsid) -> defer.Deferred:
    d = self.mapper(fsid)
    d.addCallback(SelfExtractor(self.template).generate)
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
    msg = "; ".join([ m.__name__ for m in type(self).__mro__ ])
    self.logger.info("{msg}", msg = msg)
    super().__init__(fsmap)
    self.validate_args(fsmap, root)

  def stopService(self):
    self.cleanup()
    return super().stopService()
