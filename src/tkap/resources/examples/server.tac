#
# UtilityService
# 
# prerequisites:
#   $ apt install pipenv  # would prefer pipx, but sudo invokes
#
"""
sudo -E pipenv run installer --install
sudo -E pipenv run twistd -ny /var/lib/tkap/resources/examples/server.tac
"""

from pathlib import Path
from pwd import getpwnam

from twisted.application import service, strports
from twisted.logger import LogLevel
from twisted.web import resource, server

from tkap.context_logger import initialize_logging
from tkap.adapters import *
from tkap.utility_service import KeyedRelocatedUtilityService


initialize_logging(LogLevel.debug, {})

# create utility_service
src_path = Path.cwd()
utility_service = (
  KeyedRelocatedUtilityService({ 'foo' : src_path })
    .setTemplateDirectory("/var/lib/tkap/resources/templates")
)

# create application
pw = getpwnam("tkap")
application = service.Application('utility', uid = pw.pw_uid, gid = pw.pw_gid)
serviceCollection = service.IServiceCollection(application)

# add utility_service to application
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

