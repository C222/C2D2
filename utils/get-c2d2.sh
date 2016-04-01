#!/bin/sh

echo "Making sure PIP exists"
wget -qO - https://bootstrap.pypa.io/get-pip.py | python -
pip install -U pip

echo "Installing Python dependancies"
pip install Flask requests urllib3 websocket-client cassandra-driver

exho "Installing C2D2"
wget https://github.com/C222/C2D2/archive/master.zip -O .temp.zip
unzip -u .temp.zip "C2D2-master/src/*" -d "./"
mv -f ./C2D2-master/src/* ./
rm -rf ./C2D2-master
rm ./.temp.zip
chmod +x c2d2.py

echo "Editing configuration files"
mv -n ./config.py.CHANGEME ./config.py
edit ./config.py


mv -n ./credentials.py.CHANGEME ./credentials.py
edit ./credentials.py
