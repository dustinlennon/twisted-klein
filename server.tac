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
from twisted.logger import LogLevel
from twisted.web import resource, server

from tk.context_logger import initialize_logging
from tk.adapters import *
from tk.utility_service import KeyedRelocatedUtilityService

initialize_logging(LogLevel.debug, {})

# create application
application = service.Application('utility', uid = 1, gid = 1)
serviceCollection = service.IServiceCollection(application)

# create utility_service
utility_service = KeyedRelocatedUtilityService({ 'foo' : './tests/data/foo'}, "/run/tkus")
utility_service.setServiceParent(serviceCollection)

# create a site
site = server.Site( resource.IResource(utility_service) )

# HTTP endpoint
strports.service(
  "tcp:80", site
).setServiceParent(serviceCollection)

# HTTPS endpoint
strports.service(
  "ssl:port=443:certKey=/etc/ssl/newcerts/carolina.pem:privateKey=/etc/ssl/private/carolina.key", site
).setServiceParent(serviceCollection)
