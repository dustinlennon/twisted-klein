
from twisted.protocols import basic
from twisted.internet import defer, protocol

from callbacks import cb_log_result, eb_crash
from context_logger import ContextLogger

#
# Netcat Request
#   $ printf "md5 ./isofs\n" | nc -C localhost 8120
#

class NetcatRequestProtocol(basic.LineReceiver):
  def lineReceived(self, request):
    self.factory.logger.debug("received: {r}", r = request)

    d = self.factory.handle_request( request.decode() )
    d.addCallbacks(self._cb_request, self._eb_request)
    d.addCallbacks(self._cb_lose_connection, eb_crash)
    d.addCallback(cb_log_result, format = "finished lineReceived deferred")

  def _cb_request(self, value):
    self.transport.write(value + b"\n")

  def _cb_lose_connection(self, _):
    self.transport.loseConnection()

  def _eb_request(self, failure):
    self.factory.logger.error("{f}", f = str(failure))
    self.transport.write(b"unknown error\n")

class NetcatRequestFactory(protocol.ServerFactory):
  protocol  = NetcatRequestProtocol
  logger    = ContextLogger()

  def handle_request(self, request : str) -> defer.Deferred:
    cmdargs = request.split(maxsplit = 1)
    cmd     = cmdargs[0].lower()
    args    = cmdargs[1:]
    method_name = f"cmd_{cmd}"
    d = defer.Deferred()

    try:
      m = getattr(self, method_name)
      d = m(*args)

    except AttributeError as e:
      d = defer.succeed(f"unsupported method: {cmd}".encode('utf8'))

    except TypeError as e:
      self.logger.info("{e}", e = str(e))
      d = defer.succeed(f"syntax error: {request}".encode('utf8'))

    except Exception as e:      
      d = defer.fail(e)

    return d
