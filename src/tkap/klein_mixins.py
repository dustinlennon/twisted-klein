import os

from pathlib import Path

from twisted.python import failure
from twisted.web import server

from klein import Klein

from tkap.tracer import Tracer

from tkap.interfaces import *

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
#   - common __init__ signature for derived classes taking an 'obj' arg
#   - assign 'obj' at derived-class level to preserve annotation typing
#
class KServiceBase(KBase):
  def __init__(self, api):
    super().__init__()
 
#
# DirectoryHash
#
class KDirectoryHash(KServiceBase):
  app = KBase.app

  def __init__(self, api : IDirectoryHashAPI):
    super().__init__(api)
    self.api = api

  @app.route("/md5/<path:fsid>")
  def md5(self, request: server.Request, fsid):
    request.setHeader('Content-Type', 'text/plain')
    return self.api.getDirectoryHashMD5(fsid)

  @app.route("/sha256/<path:fsid>")
  def sha256(self, request: server.Request, fsid):
    request.setHeader('Content-Type', 'text/plain')
    return self.api.getDirectoryHashSHA256(fsid)


#
# KSelfExtractor
#
class KSelfExtractor(KServiceBase):
  app = KBase.app

  def __init__(self, api : ISelfExtractorAPI):
    super().__init__(api)
    self.api = api

  @app.route("/postinstall/<path:fsid>")
  def postinstall(self, request: server.Request, fsid):
    request.setHeader('Content-Type', 'text/plain')
    return self.api.getSelfExtractor(fsid)


#
# KUserId
#
class KUserId(KServiceBase):
  app = KBase.app

  def __init__(self, api : IUserIdAPI):
    super().__init__(api)
    self.api = api

  @app.route("/userid")
  def userid(self, request: server.Request):
    request.setHeader('Content-Type', 'text/plain')
    return self.api.getUserId()
