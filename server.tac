#
# UtilityService
#   - apt install pipenv
#
"""
PIPENV_PIPFILE=/home/dnlennon/Workspace/Sandbox/twisted-klein/Pipfile \
sudo -E pipenv \
run twistd -ny server.tac
"""

from twisted.application import service, strports
from twisted.logger import LogLevel, Logger
from twisted.web import resource, server

from tk.context_logger import initialize_logging, ContextLogger
from tk.adapters import *
from tk.utility_service import KeyedRelocatedUtilityService

initialize_logging(LogLevel.debug, {})
logger = ContextLogger()

utility_service = KeyedRelocatedUtilityService({ 'foo' : './tests/data/foo'}, "/run/tkus")

application = service.Application('utility', uid = 1, gid = 1)

serviceCollection = service.IServiceCollection(application)
serviceCollection.addService(utility_service)

site = server.Site(resource.IResource(utility_service))

strports.service("tcp:80", site).setServiceParent(application)

strports.service(
  "ssl:port=443:certKey=/etc/ssl/newcerts/carolina.pem:privateKey=/etc/ssl/private/carolina.key", site
).setServiceParent(serviceCollection)
