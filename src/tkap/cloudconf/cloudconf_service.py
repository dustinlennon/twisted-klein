import shutil

from zope.interface import implementer

from twisted.internet import defer
from twisted.application import service

from tkap.cloudconf.interfaces import ICloudconfService
from tkap.cloudconf.mapper import (
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

  def setTemplateDirectory(self, path) -> "CloudconfService":
    self.template_directory = path
    return self

  def setTemplateName(self, name) -> "CloudconfService":
    self.template_name = name
    return self

  # -- IDirectoryHash ---------------------------------------------------------
  def getDirectoryHashMd5(self, fsid) -> defer.Deferred:
    return DirectoryHash.md5(fsid)
     
  def getDirectoryHashSha256(self, fsid) -> defer.Deferred:
    return DirectoryHash.sha256(fsid)

  # -- ITarballTemplate -------------------------------------------------------
  def getTarballTemplate(self, fsid) -> defer.Deferred:
    if self.template_name is None:
      d = TarballTemplate.from_raw("{{ b64encoded_tarball }}\n\n").generate(fsid)
    elif self.template_directory is None:
      d = TarballTemplate.from_package(self.template_name).generate(fsid)
    else:
      d = TarballTemplate.from_filesystem(self.template_directory, self.template_name).generate(fsid)

    return d

  # -- IEnvironment -----------------------------------------------------------
  def getEnvId(self) -> defer.Deferred:
    return PipeFactory(["/usr/bin/id"]).run()

  def getEnvPwd(self) -> defer.Deferred:
    return PipeFactory(["/usr/bin/pwd"]).run()


#
# KeyedCloudConfService
#
@implementer(ICloudconfService)
class KeyedCloudconfService(CloudconfService):
  def __init__(self, fsmap):
    super().__init__()
    self.mapper = KeyMapper(fsmap)

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
# InstalledCloudConfService
#
@implementer(ICloudconfService)
class InstalledCloudconfService(KeyedCloudconfService, RelocatedMixin):
  def __init__(self, fsmap):
    fsmap = self.relocate(fsmap)
    super().__init__(fsmap)

  def stopService(self):
    super().stopService()
    self.cleanup()
  
  def cleanup(self):
    for pth in self.mapper.fsmap.values():
      self.logger.info("removing {pth}", pth = pth)
      shutil.rmtree(pth)

