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
from tkap.tarball_template import TarballTemplate


#
# UtilityService
#
@implementer(IUtilityService)
class UtilityService(service.Service):
  logger = ContextLogger()

  def __init__(self):
    super().__init__()
    self.template_directory = None
    self.template_name = None

  def getDirectoryHashMD5(self, fsid) -> defer.Deferred:
    return DirectoryHash.md5(fsid)
     
  def getDirectoryHashSHA256(self, fsid) -> defer.Deferred:
    return DirectoryHash.sha256(fsid)

  def getTarballTemplate(self, fsid) -> defer.Deferred:
    if self.template_name is None:
      d = TarballTemplate.from_raw("{{ b64encoded_tarball }}\n\n").generate(fsid)
    elif self.template_directory is None:
      d = TarballTemplate.from_package(self.template_name).generate(fsid)
    else:
      d = TarballTemplate.from_filesystem(self.template_directory, self.template_name).generate(fsid)

    return d

  def getUserId(self) -> defer.Deferred:
    return PipeFactory(["/usr/bin/id"]).run()

  def setTemplateDirectory(self, path) -> "UtilityService":
    self.template_directory = path
    return self

  def setTemplateName(self, name) -> "UtilityService":
    self.template_name = name
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

  def getTarballTemplate(self, fsid) -> defer.Deferred:
    d = self.mapper(fsid)
    d.addCallback(super().getTarballTemplate)
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
  def __init__(self, fsmap):
    super().__init__(fsmap)
    self.relocate(fsmap)

  def stopService(self):
    self.cleanup()
    return super().stopService()
