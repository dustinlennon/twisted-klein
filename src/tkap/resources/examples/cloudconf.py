#
# CloudconfService
#   $ pipenv run python3 src/tkap/resources/examples/cloudconf.py
#   $ sudo -E pipenv run python3 src/tkap/resources/examples/cloudconf.py --installed

import argparse
import sys
from importlib import resources

from twisted.internet import endpoints, reactor
from twisted.internet.interfaces import IReactorCore, IProtocolFactory
from twisted.logger import LogLevel
from twisted.web import server
from twisted.web.resource import IResource

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
    ServiceT = InstalledCloudconfService
  else:
    ServiceT = KeyedCloudconfService

  # CloudconfService setup
  src_path = resources.files("tkap") / "resources" / "data" / "foo"
  adaptable = (
    ServiceT({ 'foo' : src_path })
      .setMetaDataTemplate( "src/tkap/resources/templates/meta-data.yaml.j2" )
      .setUserDataTemplate( "src/tkap/resources/templates/user-data.yaml.j2", site_cert_path = "certs/site.crt" )
  )

  # (componentized) endpoints
  endpoint = endpoints.serverFromString(reactor, "tcp:8121")
  endpoint.listen( IProtocolFactory( adaptable ) )

  site = server.Site( IResource( adaptable ) )
  endpoint = endpoints.serverFromString(reactor, "tcp:8122")
  endpoint.listen( site )

  # reactor lifecycle
  IReactorCore(reactor).addSystemEventTrigger("during", "shutdown", adaptable.stopService)
  reactor.run()

if __name__ == '__main__':
  sys.exit( cli() )
