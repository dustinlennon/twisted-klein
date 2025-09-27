#
# UtilityService
#   $ pipenv run python3 src/tk/resources/examples/server.py
#

from importlib import resources

from twisted.internet import endpoints, reactor
from twisted.internet.interfaces import IReactorCore, IProtocolFactory
from twisted.logger import LogLevel
from twisted.web import resource, server

from tk.adapters import *
from tk.context_logger import initialize_logging
from tk.interfaces import *
from tk.utility_service import (
  KeyedUtilityService,
  KeyedRelocatedUtilityService,
  UtilityService
)

#
# Create and serve endpoints
#
if __name__ == '__main__':

  initialize_logging(LogLevel.debug, {}, running_as_script = True)


  # UtilityService implementations:
  #   s = UtilityService() 
  src_path = resources.files("tk") / "resources" / "data" / "foo"
  s = KeyedUtilityService({ 'foo' : src_path })
  #   s = KeyedRelocatedUtilityService({ 'foo' : './tests/data/foo'}, "/tmp/tkus")

  IReactorCore(reactor).addSystemEventTrigger("during", "shutdown", s.cleanup)

  endpoint = endpoints.serverFromString(reactor, "tcp:8120")
  endpoint.listen( IProtocolFactory(IDirectoryHashAPI(s)) )

  endpoint = endpoints.serverFromString(reactor, "tcp:8121")
  endpoint.listen( IProtocolFactory(ISelfExtractorAPI(s)) )

  endpoint = endpoints.serverFromString(reactor, "tcp:8122")
  endpoint.listen( server.Site(resource.IResource(s)) )
  
  reactor.run()
