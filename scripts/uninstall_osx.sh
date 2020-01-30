#!/bin/bash

MITMPROXY_DIR="$HOME/.mitmproxy"
sudo security delete-cert -c mitmproxy "/Library/Keychains/System.keychain"

DEFAULT_NET_HAREWARE=`route -n get default | grep interface | awk '{print $2}'`
DEFAULT_NET_SERVICE=`networksetup -listallhardwareports | grep -B 1 $DEFAULT_NET_HAREWARE | head -n 1 | sed -E 's/.*: (.*)/\1/'`

sudo networksetup -setwebproxy "$DEFAULT_NET_SERVICE" '' ''
sudo networksetup -setwebproxystate "$DEFAULT_NET_SERVICE" off
sudo networksetup -setsecurewebproxy "$DEFAULT_NET_SERVICE" '' ''
sudo networksetup -setsecurewebproxystate "$DEFAULT_NET_SERVICE" off
sudo networksetup -setproxybypassdomains "$DEFAULT_NET_SERVICE" '*.local' 169.254/16