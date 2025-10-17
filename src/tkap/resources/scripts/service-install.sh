#!/usr/bin/bash

if [ $# -ne 1 ]; then
	echo "syntax error: ./service-install.sh env.tkap"
	exit 1
elif [ -f "$1" ]; then
	source $1
	env_tkap_path=$1
else
	echo "file not found: $1"
	exit 1
fi

install_path=/var/lib/tkap/install

# create a virtualenv; install tkap
sudo python3 -m venv $install_path
sudo -- $install_path/bin/pip3 install --no-cache-dir $pip_tkap
sudo chown -R tkap:tkap $install_path

# create certs; install CA
if [ -n "$cert_output_path" ]; then
	$resources_path/scripts/cert.sh $env_tkap_path
fi

# install resources
sudo install -o tkap -g tkap -d $install_path/certs $install_path/templates
sudo install -o tkap -g tkap -t $install_path $resources_path/examples/tkap.tac
sudo install -o tkap -g tkap -t $install_path/templates $resources_path/templates/*
if [ -n "$cert_output_path" ]; then 
	sudo install -o tkap -g tkap -m 0644 -t $install_path/certs $cert_output_path/*crt
	sudo install -o tkap -g tkap -m 0600 -t $install_path/certs $cert_output_path/host.key
fi

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
cert_pem_path=$cert_pem_path
private_key_path=$private_key_path
site_cert_path=$site_cert_path
meta_data_path=templates/meta-data.yaml.j2
user_data_path=templates/user-data.yaml.j2
EOF
