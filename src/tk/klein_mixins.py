import os

from pathlib import Path

from twisted.python import failure
from twisted.web import server

from klein import Klein

from tk.tracer import Tracer

from tk.interfaces import (
  IDirectoryHashService,
  ISelfExtractorService,
  IUserIdService
)

class KBase(Tracer, verbose = False):
  app     = Klein()
  isLeaf  = True

#
# Welcome
#
class KWelcome(KBase):
  app = KBase.app

  @app.handle_errors(FileNotFoundError)
  def not_found(self, request, failure):
    request.setResponseCode(404)
    T = type(failure.value)
    return f"not found / {T.__name__}\n"

  @app.handle_errors(RuntimeError)
  def internal_server_error(self, request, failure):
    request.setResponseCode(500)
    T = type(failure.value)
    return f"internal server error / {T.__name__}\n"

  @app.route("/", branch = False)
  def home(self, request: server.Request):
    return ""

#
# ServiceBase
#   - common __init__ signature for derived classes taking a 'service' arg
#   - assign 'service' at derived-class level to preserve annotation typing
#
class KServiceBase(KBase):
  def __init__(self, service):
    super().__init__()
 
  # def cb_page(self, result : bytes, request : server.Request):
  #   return result.decode()

#
# DirectoryHash
#
class KDirectoryHash(KServiceBase):
  app = KBase.app

  def __init__(self, service : IDirectoryHashService):
    super().__init__(service)
    self.service = service

  @app.route("/md5/<path:fsid>")
  def md5(self, request: server.Request, fsid):
    request.setHeader('Content-Type', 'text/plain')
    return self.service.getDirectoryHashMD5(fsid)

  @app.route("/sha256/<fsid>")
  def sha256(self, request: server.Request, fsid):
    request.setHeader('Content-Type', 'text/plain')
    return self.service.getDirectoryHashSHA256(fsid)


#
# KSelfExtractor
#
class KSelfExtractor(KServiceBase):
  app = KBase.app

  def __init__(self, service : ISelfExtractorService):
    super().__init__(service)
    self.service = service

  @app.route("/postinstall/<fsid>")
  def postinstall(self, request: server.Request, fsid):
    request.setHeader('Content-Type', 'text/plain')
    return self.service.getSelfExtractor(fsid)


#
# KUserId
#
class KUserId(KServiceBase):
  app = KBase.app

  def __init__(self, service : IUserIdService):
    super().__init__(service)
    self.service = service

  @app.route("/userid")
  def userid(self, request: server.Request):
    request.setHeader('Content-Type', 'text/plain')
    return self.service.getUserId()
