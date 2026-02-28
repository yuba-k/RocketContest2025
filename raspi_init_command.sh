sudo apt update
sudo apt -y upgrade
sudo apt install -y vim
sudo apt install -y python3-opencv
sudo apt install -y python3-pip
sudo apt install -y git
sudo apt install -y libcamera-dev libcamera-apps
git clone https://github.com/yuba-k/RocketContest2025.git
cd RocketContest2025
pip3 install -r requirements.txt --break-system-packages