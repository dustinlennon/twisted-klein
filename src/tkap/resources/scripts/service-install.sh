#!/usr/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $(realpath "$SCRIPT_DIR/../../../..")

source .env.tkap

install_path=/var/lib/tkap/install
resources_path=src/tkap/resources

# create a virtualenv
sudo -u tkap -- python3 -m venv $install_path

# create a wheel; install into the virtualenv
poetry build --clean
sudo install -o tkap -g tkap -t $install_path dist/*whl
sudo -u tkap -- $install_path/bin/pip3 install --no-cache-dir $install_path/*whl

# create certs; install CA
$resources_path/scripts/cert.sh

# install resources
sudo install -o tkap -g tkap -d $install_path/certs $install_path/templates
sudo install -o tkap -g tkap -t $install_path $resources_path/examples/tkap.tac
sudo install -o tkap -g tkap -t $install_path/templates $resources_path/templates/*
sudo install -o tkap -g tkap -m 0644 -t $install_path/certs $cert_output_path/*crt
sudo install -o tkap -g tkap -m 0600 -t $install_path/certs $cert_output_path/host.key

# config.yaml
cat<<EOF | sudo -u tkap -- tee $install_path/config.yaml >/dev/null
fsmap:
  foo: $($install_path/bin/installer)/resources/data/foo

sshkeys:
  ubuntu:
    - "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICLqmmfByjFuStwUpyIc7dcn2nOV/q+LDTzAn/32zbc/ serviceacct"
EOF

# install.env
cat<<EOF | sudo -u tkap -- tee $install_path/install.env >/dev/null
yaml_path=config.yaml
cert_pem_path=certs/host.crt
private_key_path=certs/host.key
site_cert_path=certs/site.crt
meta_data_path=templates/meta-data.yaml.j2
user_data_path=templates/user-data.yaml.j2
EOF
