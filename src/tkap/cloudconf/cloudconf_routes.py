from twisted.web import server

from klein import Klein

from tkap.errors import CloudconfServiceError
from tkap.interfaces import *
from tkap.cloudconf.interfaces import ICloudconfService
from tkap.tracer import Tracer

#
# CloudconfResource
#
class CloudconfRoutes(Tracer, verbose = True):
  app     = Klein()
  isLeaf  = True

  def __init__(self, service : ICloudconfService):
    self.service = service

  @app.handle_errors(FileNotFoundError, CloudconfServiceError)
  def not_found(self, request, failure):
    request.setResponseCode(404)
    T = type(failure.value)
    return f"{T.__name__}: {failure.value}\n"

  @app.handle_errors(RuntimeError)
  def internal_server_error(self, request, failure):
    request.setResponseCode(500)
    T = type(failure.value)
    return f"internal server error / {T.__name__}\n"

  @app.route("/md5/<string:fsid>")
  def md5(self, request: server.Request, fsid):
    request.setHeader('Content-Type', 'text/plain')
    return self.service.getDirectoryHashMd5(fsid)

  @app.route("/sha256/<string:fsid>")
  def sha256(self, request: server.Request, fsid):
    request.setHeader('Content-Type', 'text/plain')
    return self.service.getDirectoryHashSha256(fsid)

  @app.route("/pack/<string:fsid>")
  def pack(self, request: server.Request, fsid):
    request.setHeader('Content-Type', 'text/plain')
    return self.service.getTarballTemplate(fsid)
  
  @app.route("/sshkeys/<string:userid>")
  def sshkeys(self, request: server.Request, userid):
    request.setHeader('Content-Type', 'text/plain')
    return self.service.getSshKeys(userid)

  @app.route("/config/meta-data")
  def nocloud_metadata(self, request: server.Request):    
    request.setHeader('Content-Type', 'text/plain')
    return self.service.getMetaData()

  @app.route("/config/user-data")
  def nocloud_userdata(self, request: server.Request):
    request.setHeader('Content-Type', 'text/plain')

    # hostname reverse lookup
    d = self.service.getReverseLookup( request.getClientIP() )
    d.addCallback(
      lambda hostname: self.service.getUserData(hostname = hostname)
    )
    return d

  @app.route("/config/vendor-data")
  def nocloud_vendordata(self, request: server.Request):
    request.setHeader('Content-Type', 'text/plain')
    return self.service.getVendorData()

  @app.route("/config", branch=True)
  def cloudconf_default(self, request: server.Request):
    request.setHeader('Content-Type', 'text/plain')
    return ""

