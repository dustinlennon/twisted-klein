#
# UtilityService
#   $ pipenv run python3 src/iso/server.py
#

from twisted.internet import endpoints, reactor
from twisted.logger import LogLevel
from twisted.web import resource, server

from iso.adapters import *
from iso.interfaces import (
  IDirectoryHashNetcatRequestFactory,
  ISelfExtractorNetcatRequestFactory
)
from iso.context_logger import initialize_logging
from iso.utility_service import UtilityService

#
# Create and serve endpoints
#
if __name__ == '__main__':

  initialize_logging(LogLevel.debug, {})

  s = UtilityService()

  endpoint = endpoints.serverFromString(reactor, "tcp:8120")
  endpoint.listen( IDirectoryHashNetcatRequestFactory(s) )

  endpoint = endpoints.serverFromString(reactor, "tcp:8121")
  endpoint.listen( ISelfExtractorNetcatRequestFactory(s) )

  endpoint = endpoints.serverFromString(reactor, "tcp:8122")
  endpoint.listen( server.Site(resource.IResource(s)) )

  reactor.run()
