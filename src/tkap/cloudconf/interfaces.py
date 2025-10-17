from twisted.application import service
from tkap.interfaces import *

class ICloudconfService(
    service.IService,
    IDirectoryHash,
    ITarballTemplate,
    IEnvironment,
    ICloudConf
  ):
  pass
