#!/usr/bin/bash

# -- init ---------------------------------------------------------------------

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
SCRIPT_NAME="$( basename -- ${BASH_SOURCE[0]})"
source $SCRIPT_DIR/init_script $SCRIPT_NAME "$@"

resolve_path $tkap_base_path \
	cert_output_path

# -----------------------------------------------------------------------------

if [ -z "$cert_output_path" ]; then
	exit 0
fi

mkdir -p $cert_output_path

rm -f $cert_output_path/site* \
	  $cert_output_path/host* \
	  $cert_output_path/*conf

# -- Site CA ------------------------------------------------------------------

# generate rsa private key
openssl genpkey -algorithm RSA -quiet -out $cert_output_path/site.key

cat <<EOF > $cert_output_path/ca.conf
[ req ]
prompt = no
distinguished_name = req_distinguished_name
x509_extensions = req_x509_extensions

[ req_distinguished_name ]
CN = myorg

[ req_x509_extensions ]
basicConstraints = critical, CA:true
keyUsage = critical, keyCertSign
EOF

# Create site CA
openssl req -x509 -new -noenc \
  -config $cert_output_path/ca.conf \
  -key $cert_output_path/site.key -out $cert_output_path/site.crt

# -- Host CSR -----------------------------------------------------------------

# generate rsa private key
openssl genpkey -algorithm RSA -quiet -out $cert_output_path/host.key

cat <<EOF > $cert_output_path/csr.conf
[ req ]
prompt = no
distinguished_name = req_distinguished_name
req_extensions = req_x509_extensions

[ req_distinguished_name ]
O = myorg
CN = myhost.myorg

[ req_x509_extensions ]
basicConstraints = critical, CA:false
subjectAltName = $subject_alt_names
keyUsage = critical, digitalSignature
extendedKeyUsage = serverAuth
EOF

# Create host CSR
openssl req -new -noenc \
	-config $cert_output_path/csr.conf \
	-key $cert_output_path/host.key -out $cert_output_path/host.csr

# Sign host CSR with site CA
2>/dev/null \
openssl x509 -req -in $cert_output_path/host.csr \
	-CA $cert_output_path/site.crt -CAkey $cert_output_path/site.key \
	-extfile $cert_output_path/csr.conf -extensions req_x509_extensions \
	-out $cert_output_path/host.crt 

openssl verify -CAfile $cert_output_path/site.crt $cert_output_path/host.crt

# cleanup
rm $cert_output_path/ca.conf $cert_output_path/csr.conf $cert_output_path/host.csr

# install site CA certificate
sudo cp $cert_output_path/site.crt /usr/local/share/ca-certificates
sudo update-ca-certificates --fresh
