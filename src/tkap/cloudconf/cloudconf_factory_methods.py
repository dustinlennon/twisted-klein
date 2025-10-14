from twisted.internet import defer
from tkap.cloudconf.interfaces import ICloudconfService

class CloudconfFactoryMethods(object):

  def __init__(self, delegate : ICloudconfService):
      self.delegate = delegate

  def cmd_md5(self, fsid) -> defer.Deferred:
    return self.delegate.getDirectoryHashMd5(fsid)

  def cmd_sha256(self, fsid) -> defer.Deferred:
    return self.delegate.getDirectoryHashSha256(fsid)
  
  def cmd_pack(self, fsid) -> defer.Deferred:
    return self.delegate.getTarballTemplate(fsid)

  def cmd_env_id(self) -> defer.Deferred:
    return self.delegate.getEnvId()
  
  def cmd_env_pwd(self) -> defer.Deferred:
    return self.delegate.getEnvPwd()
