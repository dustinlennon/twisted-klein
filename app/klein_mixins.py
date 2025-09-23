import os

from pathlib import Path

from twisted.web import server
from klein import Klein

from tracer import Tracer

from interfaces import (
  IDirectoryHashService,
  ISelfExtractorService
)

class NotFound(Exception):
  pass

class KBase(Tracer, verbose = True):
  app     = Klein()
  isLeaf  = True

#
# Welcome
#
class KWelcome(KBase):
  app = KBase.app

  @app.handle_errors(NotFound)
  def notfound(self, request, failure):
    request.setResponseCode(404)
    return "page not found"

  @app.route("/", branch = False)
  def home(self, request: server.Request):
    return ""

#
# FsidMapper
#   - shared functionality for DirectoryHash and SelfExtractor
#
class FsidMapper(object):

  fsid_map = {
    'iso' : Path(os.environ.get('BASEDIR', '.'), 'isofs')
  }

  def map(self, request, fsid):
    raise NotImplementedError('TODO - refactor mappings to be configurable by client code')
  
    try:
      dirpath = self.fsid_map[fsid]
  
    except KeyError as e:
      raise NotFound(e)
    
    else:
      request.setHeader("Content-Type", "text/plain")

    return dirpath


#
# ServiceBase
#   - common __init__ signature for derived classes taking a 'service' arg
#   - assign 'service' at derived-class level to preserve annotation typing
#
class KServiceBase(KBase):
  def __init__(self, service):
    super().__init__()

#
# DirectoryHash
#
class KDirectoryHash(KServiceBase, FsidMapper):
  app = KBase.app

  def __init__(self, service : IDirectoryHashService):
    super().__init__(service)
    self.service = service

  @app.route("/md5/<fsid>")
  def md5(self, request: server.Request, fsid):
    dirpath = self.map(request, fsid)
    return self.service.getDirectoryHashMD5(dirpath)

  @app.route("/sha256/<fsid>")
  def sha256(self, request: server.Request, fsid):
    dirpath = self.map(request, fsid)
    return self.service.getDirectoryHashSHA256(dirpath)


#
# KSelfExtractor
#
class KSelfExtractor(KServiceBase, FsidMapper):
  app = KBase.app

  def __init__(self, service : ISelfExtractorService):
    super().__init__(service)
    self.service = service

  @app.route("/postinstall/<fsid>")
  def postinstall(self, request: server.Request, fsid):
    dirpath = self.map(request, fsid)
    return self.service.getSelfExtractor(dirpath)

