from importlib import resources
import jinja2

from zope.interface import implementer

from twisted.internet import defer

from twisted.application import service
from tkap.context_logger import ContextLogger
from tkap.interfaces import IUtilityService

from tkap.directory_hash import DirectoryHash
from tkap.mapper import (
  BaseMapper,
  KeyMapper,
  RelocatedMixin
)

from tkap.pipe_factory import PipeFactory
from tkap.self_extractor import SelfExtractor


#
# UtilityService
#
@implementer(IUtilityService)
class UtilityService(service.Service):
  logger = ContextLogger()

  def __init__(self):
    super().__init__()
    self.template_directory = None

  def getDirectoryHashMD5(self, fsid) -> defer.Deferred:
    return DirectoryHash.md5(fsid)
     
  def getDirectoryHashSHA256(self, fsid) -> defer.Deferred:
    return DirectoryHash.sha256(fsid)

  def getSelfExtractor(self, fsid) -> defer.Deferred:
    template_name = "install.sh.j2"

    if self.template_directory is None:
      d = SelfExtractor.from_package(template_name).generate(fsid)
    else:
      d = SelfExtractor.from_filesystem(self.template_directory, template_name).generate(fsid)

    return d

  def getUserId(self) -> defer.Deferred:
    return PipeFactory(["/usr/bin/id"]).run()

  def setTemplateDirectory(self, path) -> "UtilityService":
    self.template_directory = path
    return self

  def cleanup(self):
    pass

#
# _MappedUtilityService
#
class _MappedUtilityService(BaseMapper, UtilityService):

  def getDirectoryHashMD5(self, fsid) -> defer.Deferred:
    d = self.mapper(fsid)
    d.addCallback(super().getDirectoryHashMD5)
    return d
     
  def getDirectoryHashSHA256(self, fsid) -> defer.Deferred:
    d = self.mapper(fsid)
    d.addCallback(super().getDirectoryHashSHA256)
    return d

  def getSelfExtractor(self, fsid) -> defer.Deferred:
    d = self.mapper(fsid)
    d.addCallback(super().getSelfExtractor)
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
class KeyedRelocatedUtilityService(KeyMapper, _MappedUtilityService, RelocatedMixin):
  def __init__(self, fsmap):
    super().__init__(fsmap)
    self.relocate(fsmap)

  def stopService(self):
    self.cleanup()
    return super().stopService()
