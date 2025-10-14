#
# CloudconfService
#   $ pipenv run python3 src/tkap/resources/examples/server.py
#   $ sudo -E pipenv run python3 src/tkap/resources/examples/server.py --installed

import argparse
import sys
from importlib import resources

from twisted.internet import endpoints, reactor
from twisted.internet.interfaces import IReactorCore, IProtocolFactory
from twisted.logger import LogLevel
from twisted.web import resource, server

from tkap.cloudconf.adapters import *
from tkap.cloudconf.cloudconf_service import (
  KeyedCloudconfService,
  InstalledCloudconfService
)
from tkap.context_logger import initialize_logging
from tkap.interfaces import *

parser = argparse.ArgumentParser()
parser.add_argument("--installed", action="store_true" )

def cli():
  initialize_logging(LogLevel.debug, {}, running_as_script = True)

  # args parser
  args = parser.parse_args()
  if args.installed:
    CloudconfT = InstalledCloudconfService
  else:
    CloudconfT = KeyedCloudconfService

  # CloudconfService setup
  src_path = resources.files("tkap") / "resources" / "data" / "foo"
  cc = CloudconfT({ 'foo' : src_path })

  # (componentized) endpoints
  endpoint = endpoints.serverFromString(reactor, "tcp:8121")
  endpoint.listen( IProtocolFactory( cc ) )

  endpoint = endpoints.serverFromString(reactor, "tcp:8122")
  endpoint.listen( server.Site( resource.IResource(cc) ) )

  # reactor lifecycle
  IReactorCore(reactor).addSystemEventTrigger("during", "shutdown", cc.cleanup)
  reactor.run()

if __name__ == '__main__':
  sys.exit( cli() )
