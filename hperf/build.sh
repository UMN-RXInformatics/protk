#!/bin/bash

# FOR OS X
if [ `uname` == "Darwin" ]; then
gcc formantsl.c -o formantsl -I/opt/local/include -L/opt/local/lib -lgsl
gcc formantsl.c -o formantsl-test -DRUNTEST -I/opt/local/include -L/opt/local/lib -lgsl
# FOR LINUXORZ
elif [ `uname` == "Linux" ]; then
gcc formantsl.c -o formantsl
gcc formantsl.c -o formantsl-test -DRUNTEST
fi
