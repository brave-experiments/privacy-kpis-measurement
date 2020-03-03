#!/bin/bash

# run this if you want to reset the profile storage within the internal docker volume storage. This
# is the default location that runall.sh will store them.

docker volume rm privacykpis.profiles.1
docker volume rm privacykpis.profiles.2
