#!/bin/bash

if [[ $USER == "root" ]]; then
  echo "Please don't run this as root, it'll goof stuff up bad."
  exit
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
CERT_DIR=`realpath $DIR/../resources/certs`

DEFAULT_NET_HAREWARE=`route -n get default | grep interface | awk '{print $2}'`
DEFAULT_NET_SERVICE=`networksetup -listallhardwareports | grep -B 1 $DEFAULT_NET_HAREWARE | head -n 1 | sed -E 's/.*: (.*)/\1/'`
sudo networksetup -setwebproxy "$DEFAULT_NET_SERVICE" 127.0.0.1 8888
sudo networksetup -setwebproxystate "$DEFAULT_NET_SERVICE" on
sudo networksetup -setsecurewebproxy "$DEFAULT_NET_SERVICE" 127.0.0.1 8888
sudo networksetup -setsecurewebproxystate "$DEFAULT_NET_SERVICE" on
sudo networksetup -setproxybypassdomains "$DEFAULT_NET_SERVICE" '*.apple.com' '*.icloud.com' '*.local' 169.254/16

mitmdump --listen-host 127.0.0.1 --listen-port 8888 --set confdir="$CERT_DIR" &
sleep 3
sudo security add-trusted-cert -d -r trustRoot -k "/Library/Keychains/System.keychain" "$CERT_DIR/mitmproxy-ca-cert.cer"
wait