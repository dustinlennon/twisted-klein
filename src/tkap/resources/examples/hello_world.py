import sys

from zope.interface import implementer, Interface

from twisted.internet import (
  defer,
  endpoints,
  reactor
)
from twisted.internet.interfaces import IProtocolFactory
from twisted.logger import (
  FileLogObserver,
  formatEventAsClassicLogText,
  globalLogBeginner
)
from twisted.python import components
from twisted.web import server
from twisted.web.resource import IResource

from klein import Klein

from tkap.klein_resource_mixin import KleinResourceMixin
from tkap.netcat_request import NetcatRequestFactory

#
# A simple interface
#
class IHello(Interface):
  def hello(self) -> str:
    pass

#
# Adapter for a "netcat" endpoint
#
@implementer(IProtocolFactory)
class NetcatFactoryFromIHello(NetcatRequestFactory):
  def __init__(self, obj : IHello):
    self.obj = obj

  def cmd_hello(self, to_whom = None) -> defer.Deferred:
    response = self.obj.hello(to_whom)
    return defer.succeed( response.encode("utf8") )

#
# Adapter for an HTTP endpoint
#
@implementer(IResource)
class ResourceFromIHello(KleinResourceMixin):
  app     = Klein()
  isLeaf  = True

  def __init__(self, obj : IHello):
    self.obj = obj

  @app.route("/hello/<to_whom>")
  def hello(self, request: server.Request, to_whom):
    return self.obj.hello(to_whom)

  @app.route("/hello/")
  def hello_unknown(self, request: server.Request):
    return self.hello(request, None)


#
# register adapters / components
#
components.registerAdapter(NetcatFactoryFromIHello, IHello, IProtocolFactory)
components.registerAdapter(ResourceFromIHello, IHello, IResource)


#
# A concrete implementation of IHello
#
@implementer(IHello)
class ConcreteHello(object):
  def __init__(self, whoami):
    self.whoami = whoami

  def hello(self, to_whom):
    if to_whom is None:
      msg = f"Hello, I'm {self.whoami}.\n"

    elif to_whom == self.whoami:
      msg = "Thanks!\n"

    else:
      msg = f"I'm not {to_whom}.\n"

    return msg

#
# main
#
def main():
  # initialize logging
  observers = [ 
    FileLogObserver(sys.stdout, formatEventAsClassicLogText)
  ]
  globalLogBeginner.beginLoggingTo( observers )

  # Create an object that implements the IHello interface
  hello = ConcreteHello("world")

  # a "netcat" endpoint
  endpoint = endpoints.serverFromString(reactor, "tcp:8120")
  endpoint.listen( IProtocolFactory(hello) )

  # an HTTP endpoint
  site = server.Site( IResource(hello) )
  endpoint = endpoints.serverFromString(reactor, "tcp:8122")
  endpoint.listen( site )
  
  reactor.run()


if __name__ == '__main__':
  main()
