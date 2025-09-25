#
# UtilityService
#   $ pipenv run python3 src/tk/server.py
#

from twisted.internet import endpoints, reactor
from twisted.internet.interfaces import IReactorCore
from twisted.logger import LogLevel
from twisted.web import resource, server

from tk.adapters import *
from tk.interfaces import (
  ICleanupContext,
  IDirectoryHashNetcatRequestFactory,
  ISelfExtractorNetcatRequestFactory
)
from context_logger import initialize_logging
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

  # s = UtilityService() 
  # s = KeyedUtilityService({ 'foo' : './tests/data/foo'})

  s = KeyedRelocatedUtilityService({ 'foo' : './tests/data/foo'}, "/tmp/tkus")
  IReactorCore(reactor).addSystemEventTrigger("during", "shutdown", s.cleanup)

  endpoint = endpoints.serverFromString(reactor, "tcp:8120")
  endpoint.listen( IDirectoryHashNetcatRequestFactory(s) )

  endpoint = endpoints.serverFromString(reactor, "tcp:8121")
  endpoint.listen( ISelfExtractorNetcatRequestFactory(s) )

  endpoint = endpoints.serverFromString(reactor, "tcp:8122")
  endpoint.listen( server.Site(resource.IResource(s)) )
  

  reactor.run()
