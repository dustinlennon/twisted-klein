from twisted.web import server

from klein import Klein

from tkap.interfaces import *
from tkap.cloudconf.interfaces import ICloudconfService
from tkap.tracer import Tracer

#
# CloudconfResource
#
class CloudconfResource(Tracer, verbose = True):
  app     = Klein()
  isLeaf  = True

  def __init__(self, service : ICloudconfService):
    self.service = service

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

  @app.route("/md5/<path:fsid>")
  def md5(self, request: server.Request, fsid):
    request.setHeader('Content-Type', 'text/plain')
    return self.service.getDirectoryHashMd5(fsid)

  @app.route("/sha256/<path:fsid>")
  def sha256(self, request: server.Request, fsid):
    request.setHeader('Content-Type', 'text/plain')
    return self.service.getDirectoryHashSha256(fsid)

  @app.route("/pack/<path:fsid>")
  def pack(self, request: server.Request, fsid):
    request.setHeader('Content-Type', 'text/plain')
    return self.service.getTarballTemplate(fsid)

  @app.route("/userid")
  def userid(self, request: server.Request):
    request.setHeader('Content-Type', 'text/plain')
    return self.service.getUserId()
