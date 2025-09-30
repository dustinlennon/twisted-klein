#
# UtilityService
#   $ pipenv run python3 src/tk/resources/examples/server.py
#

from importlib import resources
import sys

from twisted.internet import endpoints, reactor
from twisted.internet.interfaces import IReactorCore, IProtocolFactory
from twisted.logger import LogLevel
from twisted.web import resource, server

from tkap.adapters import *
from tkap.context_logger import initialize_logging
from tkap.interfaces import *
from tkap.utility_service import (
  KeyedUtilityService,
  KeyedRelocatedUtilityService,
  UtilityService
)

def cli():
  initialize_logging(LogLevel.debug, {}, running_as_script = True)

  # UtilityService
  src_path = resources.files("tkap") / "resources" / "data" / "foo"
  s = KeyedUtilityService({ 'foo' : src_path })
  # s = UtilityService()
  IReactorCore(reactor).addSystemEventTrigger("during", "shutdown", s.cleanup)

  # (componentized) endpoints
  endpoint = endpoints.serverFromString(reactor, "tcp:8120")
  endpoint.listen( IProtocolFactory(IDirectoryHashAPI(s)) )

  endpoint = endpoints.serverFromString(reactor, "tcp:8121")
  endpoint.listen( IProtocolFactory(ITarballTemplateAPI(s)) )

  endpoint = endpoints.serverFromString(reactor, "tcp:8122")
  endpoint.listen( server.Site(resource.IResource(s)) )
  
  reactor.run()

if __name__ == '__main__':
  sys.exit(cli())
