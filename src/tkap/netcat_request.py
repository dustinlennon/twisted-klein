from twisted.internet import defer, protocol
from twisted.logger import Logger
from twisted.protocols import basic

from tkap.callbacks import cb_log_result

#
# Netcat Request
#   $ echo "md5 foo" | nc -C localhost 8120
#

#
# NetcatRequestProtocol
#
class NetcatRequestProtocol(basic.LineReceiver):
  def lineReceived(self, request):
    self.factory.logger.debug("received: {r}", r = request)

    d = self.factory.handle_request( request.decode() )
    d.addCallbacks(self._cb_request, self._eb_request)
    d.addBoth(self._cb_lose_connection)

  def _cb_request(self, value):
    self.transport.write(value + b"\n")

  def _cb_lose_connection(self, _):
    self.transport.loseConnection()

  def _eb_request(self, failure):
    self.factory.logger.error("{f}", f = str(failure))
    self.transport.write(b"unknown error\n")

#
# NetcatRequestFactory
#
class NetcatRequestFactory(protocol.ServerFactory):
  protocol  = NetcatRequestProtocol
  logger = Logger()

  def handle_request(self, request : str) -> defer.Deferred:
    cmdargs = request.split(maxsplit = 1)
    cmd     = cmdargs[0].lower()
    args    = cmdargs[1:]
    method_name = f"cmd_{cmd}"

    m = getattr(self, method_name, None)

    if m is None:
      d = defer.succeed(f"unsupported method: {cmd}".encode('utf8'))
    
    else:
      try:
        d = m(*args)

      except Exception as e:
        d = defer.fail(e)  

    return d
