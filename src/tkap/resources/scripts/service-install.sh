#!/usr/bin/bash

# -- init ---------------------------------------------------------------------

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
SCRIPT_NAME="$( basename -- ${BASH_SOURCE[0]})"
source $SCRIPT_DIR/init_script $SCRIPT_NAME "$@"

resolve_path $tkap_base_path \
	config_path \
	tac_path \
	meta_data_path \
	user_data_path \
	host_cert_path \
	host_key_path \
	site_cert_path

# -----------------------------------------------------------------------------

install_path=/var/lib/tkap/install

# create a virtualenv; install tkap
sudo python3 -m venv $install_path
sudo -- $install_path/bin/pip3 $pip_install_tkap
sudo chown -R tkap:tkap $install_path

# install resources to known locations
sudo install -o tkap -g tkap -d $install_path/certs $install_path/templates
sudo install -o tkap -g tkap $tac_path $install_path/server.tac
sudo install -o tkap -g tkap $config_path $install_path/config.yaml
sudo install -o tkap -g tkap $meta_data_path $install_path/templates/meta-data.yaml.j2
sudo install -o tkap -g tkap $user_data_path $install_path/templates/user-data.yaml.j2
sudo install -o tkap -g tkap -m 0644 $host_cert_path $install_path/certs/host.crt
sudo install -o tkap -g tkap -m 0644 $site_cert_path $install_path/certs/site.crt
sudo install -o tkap -g tkap -m 0600 $host_key_path $install_path/certs/host.key

# create install.env
cat<<EOF | sudo -u tkap -- tee $install_path/install.env >/dev/null
config_path=config.yaml
host_cert_path=certs/host.crt
host_key_path=certs/host.key
site_cert_path=certs/site.crt
meta_data_path=templates/meta-data.yaml.j2
user_data_path=templates/user-data.yaml.j2
EOF
