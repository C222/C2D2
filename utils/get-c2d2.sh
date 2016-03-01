wget https://bootstrap.pypa.io/get-pip.py
python get-pip.py
rm ./get-pip.py

pip install -U pip

declare -a packages=("Flask" "requests" "urllib3" "websocket-client")

for p in "${packages[@]}"
do
	pip install $p
done

wget https://github.com/C222/C2D2/archive/master.zip
unzip -u master.zip "C2D2-master/src/*" -d "./"
mv -ufn ./C2D2-master/src/* ./
rm -rf ./C2D2-master
rm ./master.zip

chmod +x c2d2.py

mv -n ./config.py.CHANGEME ./config.py
mv -n ./credentials.py.CHANGEME ./credentials.py

edit ./config.py
edit ./credentials.py