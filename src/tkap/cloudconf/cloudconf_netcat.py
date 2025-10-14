from twisted.internet import defer
from tkap.cloudconf.interfaces import ICloudconfService

class CloudconfNetcat(object):

  def __init__(self, delegate : ICloudconfService):
      self.delegate = delegate

  def cmd_md5(self, fsid) -> defer.Deferred:
    return self.delegate.getDirectoryHashMd5(fsid)

  def cmd_sha256(self, fsid) -> defer.Deferred:
    return self.delegate.getDirectoryHashSha256(fsid)
  
  def cmd_pack(self, fsid) -> defer.Deferred:
    return self.delegate.getTarballTemplate(fsid)
