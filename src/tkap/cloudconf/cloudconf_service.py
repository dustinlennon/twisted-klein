import shutil

from zope.interface import implementer

from twisted.internet import defer
from twisted.application import service

from tkap.cloudconf.interfaces import ICloudconfService
from tkap.cloudconf.mapper import (
  BaseMapper,
  KeyMapper,
  RelocatedMixin
)
from tkap.context_logger import ContextLogger
from tkap.directory_hash import DirectoryHash
from tkap.pipe_factory import PipeFactory
from tkap.tarball_template import TarballTemplate


#
# CloudconfService
#
@implementer(ICloudconfService)
class CloudconfService(service.Service):
  logger = ContextLogger()

  def __init__(self):
    super().__init__()
    self.template_directory = None
    self.template_name = None

  def getDirectoryHashMd5(self, fsid) -> defer.Deferred:
    return DirectoryHash.md5(fsid)
     
  def getDirectoryHashSha256(self, fsid) -> defer.Deferred:
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

  def setTemplateDirectory(self, path) -> "CloudconfService":
    self.template_directory = path
    return self

  def setTemplateName(self, name) -> "CloudconfService":
    self.template_name = name
    return self

  def cleanup(self):
    pass

#
# _MappedCloudconfService
#
class _MappedCloudconfService(CloudconfService):

  mapper : BaseMapper

  def getDirectoryHashMd5(self, fsid) -> defer.Deferred:
    d = self.mapper.map(fsid)
    d.addCallback(super().getDirectoryHashMd5)
    return d
     
  def getDirectoryHashSha256(self, fsid) -> defer.Deferred:
    d = self.mapper.map(fsid)
    d.addCallback(super().getDirectoryHashSha256)
    return d

  def getTarballTemplate(self, fsid) -> defer.Deferred:
    d = self.mapper.map(fsid)
    d.addCallback(super().getTarballTemplate)
    return d

#
# KeyedCloudConfService
#
@implementer(ICloudconfService)
class KeyedCloudconfService(_MappedCloudconfService):
  def __init__(self, fsmap):
    super().__init__()
    self.mapper = KeyMapper(fsmap)

#
# InstalledCloudConfService
#
@implementer(ICloudconfService)
class InstalledCloudconfService(KeyedCloudconfService, RelocatedMixin):
  def __init__(self, fsmap):
    fsmap = self.relocate(fsmap)
    super().__init__(fsmap)

  def stopService(self):
    self.cleanup()
    return super().stopService()
  
  def cleanup(self):
    for pth in self.mapper.fsmap.values():
      self.logger.info("removing {pth}", pth = pth)
      shutil.rmtree(pth)

