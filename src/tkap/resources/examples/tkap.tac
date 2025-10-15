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

# read configuration
config = {
  **dotenv_values(".env.tkap"),
  **os.environ
}

with open( config["yaml_path"] ) as f:
  config_yaml = yaml.safe_load(f)

# create component
adaptable = (
  InstalledCloudconfService( config_yaml["fsmap"] )
    .setTemplateDirectory("/var/lib/tkap/resources/templates")
    .setTemplateName(None)
    .setSshKeys( config_yaml["sshkeys"] )
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
cert_pem_path     = config.get("cert_pem_path")
private_key_path  = config.get("private_key_path")

if cert_pem_path and private_key_path:
  strports.service(
    f"ssl:port=443:certKey={cert_pem_path}:privateKey={private_key_path}", site
  ).setServiceParent(serviceCollection)

