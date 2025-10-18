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

# configuration
config_env = {
  **dotenv_values(".tkap"),
  **os.environ
}

# structured data
with open( config_env["config_path"] ) as f:
  config_yaml = yaml.safe_load(f)

# create component
adaptable = (
  InstalledCloudconfService( config_yaml.get("fsmap", dict()) )
    .setSshKeys( config_yaml.get("sshkeys") )
    .setMetaDataTemplate( config_env.get("meta_data_path") )
    .setUserDataTemplate( config_env.get("user_data_path"), site_cert_path = config_env.get("site_cert_path") )
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
host_cert_path  = config_env.get("host_cert_path")
host_key_path   = config_env.get("host_key_path")

if host_cert_path and host_key_path:
  strports.service(
    f"ssl:port=443:certKey={host_cert_path}:privateKey={host_key_path}", site
  ).setServiceParent(serviceCollection)

