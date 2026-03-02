sudo apt update
sudo apt -y upgrade
sudo apt install -y vim
sudo apt install -y python3-opencv
sudo apt install -y python3-pip
sudo apt install -y git
sudo apt install -y libcamera-dev libcamera-apps
sudo apt install -y python3-libcamera
sudo apt install -y python3-picamera2
git clone https://github.com/yuba-k/RocketContest2025.git
cd RocketContest2025
pip3 install picamera2 -y --break-system-packages
pip3 install board -y --break-system-packages
pip3 install adafruit-circuitpython-lsm6ds -y --break-system-packages
pip3 install pyserial -y --break-system-packages
 pip3 install smbus -y --break-system-packages