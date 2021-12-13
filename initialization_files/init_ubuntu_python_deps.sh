sudo apt-get install python3.8-venv
sudo apt-get install git
python3 -m venv ./venv
source ./venv/bin/activate
python -m pip install --upgrade pip
python -m pip install wheel
sudo apt-get install postgresql-12
sudo apt-get install net-tools
sudo apt-get install openssl
sudo apt-get install libcairo2-dev
sudo apt-get install libjpeg-dev libgif-dev
sudo apt-get install build-essential
sudo apt-get install libgirepository1.0-dev pkg-config gir1.2-gtk-3.0
sudo apt-get install python3-dev
sudo apt-get install libpq-dev
sudo apt-get install libdbus-1-dev
sudo apt-get install libcups2-dev
python -m pip install -r ./initialization_files/requirements.txt
