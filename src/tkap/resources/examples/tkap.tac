#
# Cloudconf
# 
# prerequisites:
#   $ apt install pipenv  # would prefer pipx, but sudo invokes
#   $ sudo -E pipenv run installer --install
#
# run:
#   $ sudo -E pipenv run twistd -ny /var/lib/tkap/resources/examples/tkap.tac
#
# client api:
#   $ curl -L -s http://localhost/...

import os
from pathlib import Path
from pwd import getpwnam

from dotenv import dotenv_values
import yaml

from twisted.application import service, strports
from twisted.internet.interfaces import IProtocolFactory
from twisted.logger import globalLogBeginner, Logger
from twisted.web import resource, server

from tkap.cloudconf.adapters import *
from tkap.cloudconf.cloudconf_service import InstalledCloudconfService  
from tkap.interfaces import *

# logging
# logger = Logger()
# globalLogBeginner.beginLoggingTo([])
# logger.info("Starting...")

# read configuration
config = {
  **dotenv_values(".env.tkap"),
  **os.environ
}

# create component
with open( config["fsmap_yaml"] ) as f:
  fsmap = yaml.safe_load(f)

adaptable = (
  InstalledCloudconfService(fsmap)
    .setTemplateDirectory("/var/lib/tkap/resources/templates")
    .setTemplateName(None)
)

# create application
user = getpwnam("tkap")
application = service.Application('tkap', uid = user.pw_uid, gid = user.pw_gid)
serviceCollection = service.IServiceCollection(application)

# add component to application
adaptable.setServiceParent(serviceCollection)

# a "control" endpoint
strports.listen(
  "tcp:8121", IProtocolFactory(adaptable)
)

# the Site, used by HTTP and HTTPS endpoints
site = server.Site( resource.IResource(adaptable) )

# HTTP endpoint
strports.service(
  "tcp:80", site
).setServiceParent(serviceCollection)

# HTTPS endpoint
cert_pem_file     = config.get("cert_pem_file")
private_key_file  = config.get("private_key_file")

if cert_pem_file and private_key_file:
  strports.service(
    f"ssl:port=443:certKey={cert_pem_file}:privateKey={private_key_file}", site
  ).setServiceParent(serviceCollection)

