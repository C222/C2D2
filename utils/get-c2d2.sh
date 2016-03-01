#!/bin/sh

wget -qO - https://bootstrap.pypa.io/get-pip.py | python -
python get-pip.py
rm ./get-pip.py

pip install -U pip

pip install Flask requests urllib3 websocket-client

wget https://github.com/C222/C2D2/archive/master.zip -O .temp.zip
unzip -u .temp.zip "C2D2-master/src/*" -d "./"
mv -ufn ./C2D2-master/src/* ./
rm -rf ./C2D2-master
rm ./.temp.zip

chmod +x c2d2.py

mv -n ./config.py.CHANGEME ./config.py
edit ./config.py

mv -n ./credentials.py.CHANGEME ./credentials.py
edit ./credentials.py