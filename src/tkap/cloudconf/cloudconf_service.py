from pathlib import Path
import shutil
import uuid

from zope.interface import implementer

from twisted.internet import defer
from twisted.application import service

from jinja2 import Environment, FileSystemLoader, Template

from tkap.cloudconf import filters
from tkap.cloudconf.interfaces import ICloudconfService
from tkap.cloudconf.mapper import (
  KeyMapper,
  RelocatedMixin
)
from tkap.context_logger import ContextLogger
from tkap.directory_hash import DirectoryHash
from tkap.errors import CloudConfigKeyError, SshKeyError
from tkap.pipe_factory import PipeFactory
from tkap.tarball_template import TarballTemplate


#
# CloudconfService
#
@implementer(ICloudconfService)
class CloudconfService(service.Service):
  logger = ContextLogger()
  empty_template = Template("")

  def __init__(self):
    super().__init__()
    self.tarball_template_directory = None
    self.tarball_template_name = None
    
    self.sshkeys = dict()
    
    self.nocloud_template = dict()
    self.nocloud_kwargs = dict()

  def setTarballTemplateDirectory(self, path) -> "CloudconfService":
    self.template_directory = path
    return self

  def setTarballTemplateName(self, name) -> "CloudconfService":
    self.template_name = name
    return self

  def setSshKeys(self, sshkeys) -> "CloudconfService":
    if sshkeys:
      self.sshkeys = sshkeys
    return self

  def setMetaDataTemplate(self, meta_data_path, **kwargs) -> "CloudconfService":
    if meta_data_path:
      self.nocloud_template['meta'] = self._get_template(meta_data_path)
      self.nocloud_kwargs['meta'] = kwargs
    return self

  def setUserDataTemplate(self, user_data_path, **kwargs) -> "CloudconfService":
    if user_data_path:
      self.nocloud_template['user'] = self._get_template(user_data_path)
      self.nocloud_kwargs['user'] = kwargs
    return self
  
  def setVendorDataTemplate(self, vendor_data_path, **kwargs) -> "CloudconfService":
    if vendor_data_path:
      self.nocloud_template['vendor'] = self._get_template(vendor_data_path)
      self.nocloud_kwargs['vendor'] = kwargs
    return self  

  def _get_template(self, path):
      pth = Path(path).resolve()
      env = Environment( loader = FileSystemLoader( pth.parent ) )
      env.filters['from_path'] = filters.from_path
      env.globals['instance_id'] = filters.instance_id
      return env.get_template( pth.name )
  

  # -- IDirectoryHash ---------------------------------------------------------
  def getDirectoryHashMd5(self, fsid) -> defer.Deferred:
    return DirectoryHash.md5(fsid)
     
  def getDirectoryHashSha256(self, fsid) -> defer.Deferred:
    return DirectoryHash.sha256(fsid)

  # -- ITarballTemplate -------------------------------------------------------
  def getTarballTemplate(self, fsid) -> defer.Deferred:
    if self.tarball_template_name is None:
      d = TarballTemplate.from_raw("{{ b64encoded_tarball }}\n\n").generate(fsid)
    elif self.tarball_template_directory is None:
      d = TarballTemplate.from_package(self.tarball_template_name).generate(fsid)
    else:
      d = TarballTemplate.from_filesystem(self.tarball_template_directory, self.tarball_template_name).generate(fsid)

    return d

  # -- IEnvironment -----------------------------------------------------------
  def getEnvId(self) -> defer.Deferred:
    return PipeFactory(["/usr/bin/id"]).run()

  def getEnvPwd(self) -> defer.Deferred:
    return PipeFactory(["/usr/bin/pwd"]).run()
  
  # -- ICloudConf -------------------------------------------------------------
  def getMetaData(self, **kw) -> defer.Deferred:
    return self._nocloud_template('meta', **kw)

  def getUserData(self, **kw) -> defer.Deferred:
    return self._nocloud_template('user', **kw)

  def getVendorData(self, **kw) -> defer.Deferred:
    return self._nocloud_template('vendor', **kw)

  def _nocloud_template(self, key, **kw):
    template  = self.nocloud_template.get(key, self.empty_template)
    kw.update( self.nocloud_kwargs.get(key, dict()) )
    content = template.render(**kw)
    return defer.succeed(content)

  def getSshKeys(self, userid) -> defer.Deferred:
    keylist = self.sshkeys.get(userid, [])
    sshkeys = "\n".join( keylist )

    if len(sshkeys) > 0:
      return defer.succeed( sshkeys )
    else:
      raise SshKeyError(f"'{userid}' unknown")

  def getReverseLookup(self, ipaddr) -> defer.Deferred:
    d = PipeFactory([ f"dig @192.168.1.1 +short -x {ipaddr}" ]).run()
    d.addCallback(bytes.decode)
    return d


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

